## Prowl interface

import logging
import httplib
import urllib

from xml.etree import ElementTree

################################################################################
class Client():

    #---------------------------------------------------------------------------
    def __init__(self, appname, key):
        self.logger = logging.getLogger('Plugin.prowl.Client')

        self.appname = appname
        self.apikey = key

    #---------------------------------------------------------------------------
    def notify(self, message, title=None, priority=0):
        # construct the API call body
        params = urllib.urlencode({
            'apikey' : self.apikey,
            'priority' : str(priority),
            'event' : title,
            'description' : message,
            'application' : self.appname
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
    # verify the internal credentials are valid
    def verifyCredentials(self):
        params = urllib.urlencode({ 'apikey': self.apikey })
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

