#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import logging
import unittest
import prowl

# keep logging output to a minumim for testing
logging.basicConfig(level=logging.ERROR)

# XXX note that the API keys in this file are specific to my user account...  they
# should never be used in production, since their limits are often exceeded during
# testing and may be revoked at any time if they are misused

################################################################################
class VerifyAPIKey(unittest.TestCase):

    def test_valid_key(self):
        # this is a valid API key for development
        client = prowl.Client('Unit Test', '04db42f70722c526b71722fca57e790e47bd426b')
        valid = client.verifyCredentials()
        self.assertTrue(valid, 'verify failed using a valid key')

    def test_invalid_key(self):
        # a valid-looking key
        client = prowl.Client('Unit Test', '117644459ad8c4f530df3796ed45e8fda5c6abc2')
        valid = client.verifyCredentials()
        self.assertFalse(valid, 'client accepted an invalid key')

    def test_revoked_key(self):
        # this key was deleted on 2 Jan, 2017
        client = prowl.Client('Unit Test', '5accd68735633f0bd34a28938ee9c3758c657ff7')
        valid = client.verifyCredentials()
        self.assertFalse(valid, 'client accepted an invalid key')

    def test_malformed_key(self):
        # a completely invalid API key
        client = prowl.Client('Unit Test', '0123456789')
        valid = client.verifyCredentials()
        self.assertFalse(valid, 'client accepted an invalid key')

    def test_bad_key_format(self):
        # a completely invalid API key
        client = prowl.Client('Unit Test', 42)
        valid = client.verifyCredentials()
        self.assertFalse(valid, 'client accepted an invalid key')

    def test_empty_key(self):
        client = prowl.Client('Unit Test', None)
        valid = client.verifyCredentials()
        self.assertFalse(valid, 'client accepted an invalid key')

################################################################################
@unittest.skip('forceably eliminates all remaining API calls')
class APILimit(unittest.TestCase):

    def setUp(self):
        client = prowl.Client('Unit Test', '04db42f70722c526b71722fca57e790e47bd426b')
        self.assertIsNone(client.remaining)

        # verify once to read the remaining call count
        client.verifyCredentials()
        self.assertIsNotNone(client.remaining)

        # drain the API calls for this client
        while client.remaining > 0:
            client.verifyCredentials()

        self.client = client

    def test_rate_limit(self):
        valid = client.verifyCredentials()
        self.assertEqual(self.client.remaining, None)

################################################################################
class TestMessagePriority(unittest.TestCase):

    def setUp(self):
        self.client = prowl.Client('Unit Test', '04db42f70722c526b71722fca57e790e47bd426b')

    def test_emergency_message(self):
        success = self.client.notify('Emergency message', priority=2)
        self.assertTrue(success, 'notification failed')

    def test_important_message(self):
        success = self.client.notify('Important message', priority=1)
        self.assertTrue(success, 'notification failed')

    def test_moderate_message(self):
        success = self.client.notify('Moderate priority message', priority=-1)
        self.assertTrue(success, 'notification failed')

    def test_very_low_message(self):
        success = self.client.notify('Very low priority message', priority=-2)
        self.assertTrue(success, 'notification failed')

    def test_priority_too_high(self):
        success = self.client.notify('Bad message priority', priority=3)
        self.assertFalse(success, 'notification should not have sent')

    def test_priority_too_low(self):
        success = self.client.notify('Bad message priority', priority=-3)
        self.assertFalse(success, 'notification should not have sent')

################################################################################
class TestNotifications(unittest.TestCase):

    def setUp(self):
        self.client = prowl.Client('Unit Test', '04db42f70722c526b71722fca57e790e47bd426b')

    def test_basic_message(self):
        success = self.client.notify('Basic test message')
        self.assertTrue(success, 'notification failed')

    def test_unicode_message(self):
        success = self.client.notify(u'Unicode message: ß !!')
        self.assertTrue(success, 'notification failed')

    def test_message_with_title(self):
        success = self.client.notify('Basic message with title', title='Test Message')
        self.assertTrue(success, 'notification failed')

    def test_message_no_title(self):
        success = self.client.notify('Basic message with no title')
        self.assertTrue(success, 'notification failed')

    def test_message_blank_title(self):
        success = self.client.notify('Basic message with blank title', title='')
        self.assertTrue(success, 'notification failed')

    def test_blank_message(self):
        success = self.client.notify(None, title='Blank Message')
        self.assertTrue(success, 'notification failed')

    def test_blank_message_and_title(self):
        success = self.client.notify(None)
        self.assertFalse(success, 'must provide title or message')

################################################################################
## MAIN ENTRY

if __name__ == '__main__':
    unittest.main(verbosity=2)

