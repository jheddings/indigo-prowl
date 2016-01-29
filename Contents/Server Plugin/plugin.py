#!/usr/bin/env python2.5

import os, httplib, urllib, plistlib

from ghpu import GitHubPluginUpdater
from xml.etree import ElementTree

################################################################################
class Plugin(indigo.PluginBase):

    #---------------------------------------------------------------------------
    def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
        self.debug = pluginPrefs.get('debug', False)
        self.updater = GitHubPluginUpdater('jheddings', 'indigo-prowl', self)

    #---------------------------------------------------------------------------
    def __del__(self):
        indigo.PluginBase.__del__(self)

    #---------------------------------------------------------------------------
    def checkForUpdates(self):
        self.updater.checkForUpdate()

    #---------------------------------------------------------------------------
    def updatePlugin(self):
        self.updater.update()

    #---------------------------------------------------------------------------
    def toggleDebugging(self):
        self.debug = not self.debug
        self.pluginPrefs['debug'] = self.debug

    #---------------------------------------------------------------------------
    def validatePrefsConfigUi(self, values):
        errors = indigo.Dict()

        # application name is required...
        appname = values.get('appname', '')
        if (len(appname) == 0):
            errors['appname'] = 'You must provide an application name'

        # an API key is required and must be valid...
        apikey = values.get('apikey', '')
        if (len(apikey) == 0):
            errors['apikey'] = 'You must provide your Prowl API key'
        elif (not self.prowlVerify(apikey)):
            errors['apikey'] = 'Invalid API key'

        return ((len(errors) == 0), values, errors)

    #---------------------------------------------------------------------------
    def closedPrefsConfigUi(self, values, canceled):
        if (not canceled):
            self.debug = values.get('debug', False)

    #---------------------------------------------------------------------------
    def validateActionConfigUi(self, values, typeId, devId):
        errors = indigo.Dict()

        # building a description for the Indigio UI...
        priority = values['priority'];
        header = 'Prowl [' + priority + ']: '

        # the title is not required, but check substitutions if it is there...
        title = values.get('title', '')
        if (len(title) > 0):
            subst = self.substitute(title, validateOnly=True)
            if (subst[0]): header += title + '-'
            else: errors['title'] = subst[1]

        # a message is required, and we'll verify substitutions
        message = values.get('message', '')
        if (len(message) == 0):
            errors['message'] = 'You must provide a message'
        else:
            subst = self.substitute(message, validateOnly=True)
            if (not subst[0]): errors['message'] = subst[1]

        # create the description for Indigo's UI
        values['description'] = header + message

        return ((len(errors) == 0), values, errors)

    #---------------------------------------------------------------------------
    def notify(self, action):
        # perform substitution on the title and message
        title = self.substitute(action.props.get('title', ''))
        message = self.substitute(action.props.get('message', ''))

        # construct the API call body
        params = urllib.urlencode({
            'apikey' : self.pluginPrefs.get('apikey', None),
            'priority' : action.props.get('priority', '0'),
            'event' : title,
            'description' : message,
            'application' : self.pluginPrefs.get('appname', 'Indigo')
        })
        self._debug('notify: ' + params)

        # Prowl won't accept the POST unless it carries the right content type
        headers = {
            'Content-type': 'application/x-www-form-urlencoded'
        }

        try:
            conn = httplib.HTTPSConnection('api.prowlapp.com')
            conn.request('POST', '/publicapi/add', params, headers)
            resp = conn.getresponse()

            # so we can see the results in the log...
            self.processStdResponse(resp)

        except Exception as e:
            self._error(str(e))

    #---------------------------------------------------------------------------
    # verify the given API key is valid with Prowl
    def prowlVerify(self, apikey):
        params = urllib.urlencode({ 'apikey': apikey })
        self._debug('verify: ' + params)
        verified = False

        try:
            conn = httplib.HTTPConnection('api.prowlapp.com')
            conn.request('GET', '/publicapi/verify?' + params)
            resp = conn.getresponse()
            verified = self.processStdResponse(resp)

        except Exception as e:
            self._error(str(e))

        return verified

    #---------------------------------------------------------------------------
    # returns True if the response represents success, False otherwise
    def processStdResponse(self, resp):
        self._debug('HTTP %d %s' % (resp.status, resp.reason))

        root = ElementTree.fromstring(resp.read())
        content = root[0]

        if (content.tag == 'success'):
            remain = content.attrib['remaining']
            self._debug('success: ' + remain + ' calls remaining')

        elif (content.tag == 'error'):
            self._error('error: ' + content.text)

        else:
            # just in case something strange comes along...
            raise Exception('unknown response', content.tag)

        return (resp.status == 200)

    #---------------------------------------------------------------------------
    # convenience method for logging
    def _log(self, msg):
        indigo.server.log(msg)

    #---------------------------------------------------------------------------
    # convenience method for debug messages
    def _debug(self, msg):
        self.debugLog(msg)

    #---------------------------------------------------------------------------
    # convenience method for error messages
    def _error(self, msg):
        self.errorLog(msg)

