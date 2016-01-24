#!/usr/bin/env python2.5

import httplib, urllib
import xml.etree.ElementTree as ET

import updater

################################################################################
class Plugin(indigo.PluginBase):

    #---------------------------------------------------------------------------
    def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
        self.debug = pluginPrefs.get('debug', False)

    #---------------------------------------------------------------------------
    def __del__(self):
        indigo.PluginBase.__del__(self)

    #---------------------------------------------------------------------------
    def checkForUpdates(self):
        currentVersion = str(self.pluginVersion)
        indigo.server.log('Checking for updates')

        try:
            update = updater.getUpdate('jheddings', 'indigo-prowl', currentVersion, plugin=self)
        except Exception, e:
            self.errorLog('An error occured during update %s' % str(e))
            update = None

        if (update == None):
            indigo.server.log('No updates are available')
        else:
            self.errorLog('A new version is available:')
            self.errorLog(update)

    #---------------------------------------------------------------------------
    def toggleDebugging(self):
        self.debug = not self.debug
        self.pluginPrefs['debug'] = self.debug

    #---------------------------------------------------------------------------
    def validatePrefsConfigUi(self, values):
        errors = indigo.Dict()

        if values['appname'] == '':
            errors['appname'] = 'You must provide an application name'

        if values['apikey'] == '':
            errors['apikey'] = 'You must provide your Prowl API key'
        elif not self.prowlVerify(values['apikey']):
            errors['apikey'] = 'Invalid API key'

        return ((len(errors) == 0), values, errors)

    #---------------------------------------------------------------------------
    def closedPrefsConfigUi(self, values, canceled):
        if not canceled:
            self.debug = values.get('debug', False)

    #---------------------------------------------------------------------------
    def validateActionConfigUi(self, values, typeId, devId):
        errors = indigo.Dict()

        priority = values['priority'];
        header = 'Prowl [' + priority + ']: '

        title = values['title'];
        if (title and len(title) > 0):
            header += title + '-'

        if values['message'] == '':
            errors['message'] = 'You must provide message'
        else:
            message = values['message'];
            values['description'] = header + message

        return ((len(errors) == 0), values, errors)

    #---------------------------------------------------------------------------
    def notify(self, action):
        title = self.substitute(action.props.get('title', ''))
        message = self.substitute(action.props.get('message', ''))

        params = urllib.urlencode({
            'apikey' : self.pluginPrefs.get('apikey', None),
            'priority' : action.props.get('priority', '0'),
            'event' : title,
            'description' : message,
            'application' : self.pluginPrefs.get('appname', 'Indigo')
        })
        self.debugLog('notify: ' + params)

        headers = {
            'Content-type': 'application/x-www-form-urlencoded',
            'Accept': 'text/plain'
        }

        try:
            conn = httplib.HTTPConnection('api.prowlapp.com')
            conn.request('POST', '/publicapi/add', params, headers)
            resp = conn.getresponse()
            self.processStdResponse(resp)

        except Exception, e:
            self.errorLog(str(e))

    #---------------------------------------------------------------------------
    def prowlVerify(self, apikey):
        params = urllib.urlencode({'apikey': apikey})
        self.debugLog('verify: ' + params)
        verified = False

        try:
            conn = httplib.HTTPConnection('api.prowlapp.com')
            conn.request('GET', '/publicapi/verify?' + params)
            resp = conn.getresponse()
            verified = self.processStdResponse(resp)

        except Exception, e:
            self.errorLog(str(e))

        return verified

    #---------------------------------------------------------------------------
    def processStdResponse(self, resp):
        self.debugLog('HTTP response - ' + str(resp.status) + ':' + resp.reason)

        root = ET.fromstring(resp.read())
        content = root[0]

        if (content.tag == 'success'):
            remain = content.attrib['remaining']
            self.debugLog('success: ' + remain + ' remaining')
        elif (content.tag == 'error'):
            self.errorLog('error: ' + content.text)
        else:
            raise Exception('unknown response', content.tag)

        return (resp.status == 200)

