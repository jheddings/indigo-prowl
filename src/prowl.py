## Prowl interface

import logging
import requests

from xml.etree import ElementTree

API_BASE_URL = 'https://api.prowlapp.com/publicapi'

################################################################################
class Client():

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
    def notify(self, message=None, title=None, url=None, priority=0):
        params = {
            'priority' : str(priority),
            'application' : self.appname,
            'apikey' : self.apikey
        }

        if title is not None and len(title) > 0:
            params['event'] = title

        if message is not None and len(message) > 0:
            params['description'] = message

        if url is not None and len(url) > 0:
            params['url'] = url

        self.logger.debug(u'notify: %s', params)
        return self._api_post('add', params)

    #---------------------------------------------------------------------------
    def _api_get(self, func, params):

        try:
            resp = requests.get(f'{API_BASE_URL}/{func}', params=params)
            success = self._processStdResponse(resp)

        except Exception as e:
            self.logger.error(str(e))
            success = False

        return success

    #---------------------------------------------------------------------------
    def _api_post(self, func, params):
        success = None

        headers = {
            'Content-type': 'application/x-www-form-urlencoded'
        }

        try:
            resp = requests.get(f'{API_BASE_URL}/{func}', params=params, headers=headers)
            success = self._processStdResponse(resp)

        except Exception as e:
            self.logger.error(str(e))
            success = False

        return success

    #---------------------------------------------------------------------------
    # returns True if the response represents success, False otherwise
    def _processStdResponse(self, resp):
        self.logger.debug(u'HTTP %d %s', resp.status_code, resp.reason)

        root = ElementTree.fromstring(resp.content)
        content = root[0]

        if (content.tag == 'success'):
            self.remaining = int(content.attrib['remaining'])
            self.logger.debug(u'success: %d calls remaining', self.remaining)

        elif (content.tag == 'error'):
            self.logger.warn(u'received error: %s', content.text)

        else:
            # just in case something strange comes along...
            raise Exception('unknown response', content.tag)

        return (resp.status_code == 200)
