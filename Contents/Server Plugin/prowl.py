## Prowl interface

import logging
import httplib
import urllib

from xml.etree import ElementTree

################################################################################
class Client():

    apiroot = 'https://api.prowlapp.com/publicapi'

    #---------------------------------------------------------------------------
    def __init__(self, appname, apikey):
        self.logger = logging.getLogger('Plugin.prowl.Client')

        self.appname = appname
        self.apikey = apikey

        self.remaining = None

    #---------------------------------------------------------------------------
    # verify the internal credentials are valid
    def verifyCredentials(self):
        params = {
            'apikey': self.apikey
        }

        self.logger.debug(u'verify: %s', params)
        return self._api_get('verify', params)

    #---------------------------------------------------------------------------
    def notify(self, message, title=None, priority=0):
        params = {
            'priority' : str(priority),
            'application' : self._sanitize(self.appname),
            'event' : self._sanitize(title),
            'description' : self._sanitize(message),
            'apikey' : self.apikey
        }

        self.logger.debug(u'notify: %s', params)
        return self._api_post('add', params)

    #---------------------------------------------------------------------------
    def _sanitize(self, value):
        # urlencode doesn't work with unicode, so encode as UTF-8
        if isinstance(value, unicode): value = value.encode('utf8')

        return value

    #---------------------------------------------------------------------------
    def _api_get(self, func, params):
        data = urllib.urlencode(params)
        path = '/publicapi/%s?%s' % (func, data)
        success = None

        try:
            conn = httplib.HTTPSConnection('api.prowlapp.com')
            conn.request('GET', path)
            resp = conn.getresponse()
            success = self._processStdResponse(resp)

        except Exception as e:
            self.logger.error(str(e))
            success = False

        return success

    #---------------------------------------------------------------------------
    def _api_post(self, func, params):
        data = urllib.urlencode(params)
        path = '/publicapi/%s' % func
        success = None

        headers = {
            'Content-type': 'application/x-www-form-urlencoded'
        }

        try:
            conn = httplib.HTTPSConnection('api.prowlapp.com')
            conn.request('POST', path, data, headers)
            resp = conn.getresponse()
            success = self._processStdResponse(resp)

        except Exception as e:
            self.logger.error(str(e))
            success = False

        return success

    #---------------------------------------------------------------------------
    # returns True if the response represents success, False otherwise
    def _processStdResponse(self, resp):
        self.logger.debug(u'HTTP %d %s', resp.status, resp.reason)

        root = ElementTree.fromstring(resp.read())
        content = root[0]

        if (content.tag == 'success'):
            self.remaining = int(content.attrib['remaining'])
            self.logger.debug(u'success: %d calls remaining', self.remaining)

        elif (content.tag == 'error'):
            self.logger.warn(u'received error: %s', content.text)

        else:
            # just in case something strange comes along...
            raise Exception('unknown response', content.tag)

        return (resp.status == 200)

