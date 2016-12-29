#!/usr/bin/env python2.5

import os, httplib, urllib, plistlib

from ghpu import GitHubPluginUpdater
from xml.etree import ElementTree

################################################################################
class Plugin(indigo.PluginBase):

    #---------------------------------------------------------------------------
    def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
        self.updater = GitHubPluginUpdater(self)
        self._initializeLogging(pluginPrefs)

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
        elif (not self._prowlVerify(apikey)):
            errors['apikey'] = 'Invalid API key'

        return ((len(errors) == 0), values, errors)

    #---------------------------------------------------------------------------
    def closedPrefsConfigUi(self, values, canceled):
        if canceled: return
        self._initializeLogging(values)

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
        self.logger.debug(u'notify: %s', params)

        # Prowl won't accept the POST unless it carries the right content type
        headers = {
            'Content-type': 'application/x-www-form-urlencoded'
        }

        try:
            conn = httplib.HTTPSConnection('api.prowlapp.com')
            conn.request('POST', '/publicapi/add', params, headers)
            resp = conn.getresponse()

            # so we can see the results in the log...
            self._processStdResponse(resp)

        except Exception as e:
            self.logger.error(str(e))

    #---------------------------------------------------------------------------
    def _initializeLogging(self, values):
        levelTxt = values.get('logLevel', None)

        if levelTxt is None:
            self.logLevel = 20
        else:
            self.logLevel = int(levelTxt)

        self.indigo_log_handler.setLevel(self.logLevel)

    #---------------------------------------------------------------------------
    # verify the given API key is valid with Prowl
    def _prowlVerify(self, apikey):
        params = urllib.urlencode({ 'apikey': apikey })
        self.logger.debug(u'verify: %s', params)
        verified = False

        try:
            conn = httplib.HTTPConnection('api.prowlapp.com')
            conn.request('GET', '/publicapi/verify?' + params)
            resp = conn.getresponse()
            verified = self._processStdResponse(resp)

        except Exception as e:
            self.logger.error(str(e))

        return verified

    #---------------------------------------------------------------------------
    # returns True if the response represents success, False otherwise
    def _processStdResponse(self, resp):
        self.logger.debug(u'HTTP %d %s', resp.status, resp.reason)

        root = ElementTree.fromstring(resp.read())
        content = root[0]

        if (content.tag == 'success'):
            remain = int(content.attrib['remaining'])
            self.logger.debug(u'success: %d calls remaining', remain)

        elif (content.tag == 'error'):
            self.logger.warn(u'received error: %s', content.text)

        else:
            # just in case something strange comes along...
            raise Exception('unknown response', content.tag)

        return (resp.status == 200)

