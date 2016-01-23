#!/usr/bin/env python

import httplib, urllib
import xml.etree.ElementTree as ET

kProwlAPI = 'https://api.prowlapp.com/publicapi/'
kProwlProviderKey = 'd96ce35a294c10c8b5683645f55ad23275a82241'

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
    def validatePrefsConfigUi(self, values):
        errors = indigo.Dict()

        if values['apikey'] == '':
            errors['apikey'] = 'You must provide your Prowl API key'
        elif not self.prowl_verify(values['apikey']):
            errors['apikey'] = 'Invalid API key'

        return ((len(errors) == 0), values, errors)

    #---------------------------------------------------------------------------
    def validateActionConfigUi(self, values, typeId, devId):
        return (True, values)

    #---------------------------------------------------------------------------
    def notify(self, action):
        params = urllib.urlencode({
            'apikey' : self.pluginPrefs.get('apikey', None),
            'priority' : action.props.get('priority', '0'),
            'event' : action.props.get('title', ''),
            'description' : action.props.get('description', ''),
            'application' : 'Indigo'
        })
        self.debugLog('notify: ' + params)

        headers = {
            'Content-type': 'application/x-www-form-urlencoded',
            'Accept': 'text/plain'
        }

        conn = httplib.HTTPConnection('api.prowlapp.com')
        conn.request('POST', '/publicapi/add', params, headers)
        resp = conn.getresponse()
        self.prowl_std_response(resp)

    #---------------------------------------------------------------------------
    def prowl_verify(self, apikey):
        params = urllib.urlencode({'apikey': apikey})
        self.debugLog('verify: ' + params)

        conn = httplib.HTTPConnection('api.prowlapp.com')
        conn.request('GET', '/publicapi/verify?' + params)
        resp = conn.getresponse()

        return self.prowl_std_response(resp)

    #---------------------------------------------------------------------------
    def prowl_std_response(self, resp):
        self.debugLog(str(resp.status) + ':' + resp.reason)

        #TODO log remaining calls on success
        #self.debugLog(resp.read())

        #TODO use self.errorLog for errors

        return (resp.status == 200)

