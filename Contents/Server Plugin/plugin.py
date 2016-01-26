#!/usr/bin/env python2.5

import os, httplib, urllib, plistlib
import xml.etree.ElementTree as ET

import updater

################################################################################
class Plugin(indigo.PluginBase):

    #---------------------------------------------------------------------------
    def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
        self.debug = pluginPrefs.get('debug', False)
        self.pluginPath = self.getPluginPath()

    #---------------------------------------------------------------------------
    def __del__(self):
        indigo.PluginBase.__del__(self)

    #---------------------------------------------------------------------------
    def getPluginPath(self):
        self.debugLog('Looking for plugin installation: %s' % self.pluginId)

        # assume the plugin is installed under the standard installation folder...
        path = os.path.join(indigo.server.getInstallFolderPath(), 'Plugins', self.pluginDisplayName + '.indigoPlugin')
        self.debugLog('Calculated plugin path: %s' % path)

        plistFile = os.path.join(path, 'Contents', 'Info.plist')
        self.debugLog('Plugin info file: %s' % plistFile)

        if (not os.path.isfile(plistFile)):
            self.errorLog('File not found: %s' % plistFile)
            return None

        try:
            # make sure the plugin is the by reading the info file
            plist = plistlib.readPlist(plistFile)
            pluginId = plist.get('CFBundleIdentifier', None)
            self.debugLog('Found plugin: %s' % pluginId)

            if (self.pluginId == pluginId):
                self.debugLog('Verified plugin path: %s' % path)
            else:
                self.errorLog('Incorrect plugin ID in path: %s found, %s expected' % ( pluginId, self.pluginId ))
                path = None

        except Exception as e:
            self.errorLog('Error reading Info.plist: %s' % str(e))
            path = None

        return path

    #---------------------------------------------------------------------------
    def checkForUpdates(self):
        indigo.server.log('Checking for updates')

        try:
            currentVersion = str(self.pluginVersion)
            update = updater.getUpdate('jheddings', 'indigo-prowl', currentVersion, plugin=self)
        except Exception as e:
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

        # application name is required...
        appname = values.get('appname', '')
        if (len(appname) == 0):
            errors['appname'] = 'You must provide an application name'

        # an API key is required...
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
        self.debugLog('notify: ' + params)

        # Prowl won't accept the POST unless it carries the right content type
        headers = {
            'Content-type': 'application/x-www-form-urlencoded'
        }

        try:
            conn = httplib.HTTPConnection('api.prowlapp.com')
            conn.request('POST', '/publicapi/add', params, headers)
            resp = conn.getresponse()

            # so we can see the results in the log...
            self.processStdResponse(resp)

        except Exception as e:
            self.errorLog(str(e))

    #---------------------------------------------------------------------------
    # verify the given API key is valid with Prowl
    def prowlVerify(self, apikey):
        params = urllib.urlencode({ 'apikey': apikey })
        self.debugLog('verify: ' + params)
        verified = False

        try:
            conn = httplib.HTTPConnection('api.prowlapp.com')
            conn.request('GET', '/publicapi/verify?' + params)
            resp = conn.getresponse()
            verified = self.processStdResponse(resp)

        except Exception as e:
            self.errorLog(str(e))

        return verified

    #---------------------------------------------------------------------------
    # returns True if the response represents success, False otherwise
    def processStdResponse(self, resp):
        self.debugLog('HTTP %d %s' % (resp.status, resp.reason))

        root = ET.fromstring(resp.read())
        content = root[0]

        if (content.tag == 'success'):
            remain = content.attrib['remaining']
            self.debugLog('success: ' + remain + ' calls remaining')

        elif (content.tag == 'error'):
            self.errorLog('error: ' + content.text)

        else:
            # just in case something strange comes along...
            raise Exception('unknown response', content.tag)

        return (resp.status == 200)

