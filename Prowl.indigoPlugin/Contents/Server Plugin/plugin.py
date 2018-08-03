#!/usr/bin/env python2.5

import prowl

import iplug

################################################################################
class Plugin(iplug.PluginBase):

    #---------------------------------------------------------------------------
    def validatePrefsConfigUi(self, values):
        errors = indigo.Dict()

        # application name is required...
        appname = values.get('appname', None)
        if appname is None or len(appname) == 0:
            errors['appname'] = 'You must provide an application name'

        # an API key is required and must be valid...
        apikey = values.get('apikey', None)
        if apikey is None or len(apikey) == 0:
            errors['apikey'] = 'You must provide your Prowl API key'
        else:
            # we need a temporary client to validate the API key
            client = prowl.Client('VERIFY_ONLY', apikey)
            if not client.verifyCredentials():
                self.logger.warn('Could not verify API key')
                errors['apikey'] = 'Invalid API key (or call limit exceeded)'

        return ((len(errors) == 0), values, errors)

    #---------------------------------------------------------------------------
    def validateActionConfigUi(self, values, typeId, devId):
        errors = indigo.Dict()

        # building a description for the Indigio UI...
        priority = values['priority'];
        desc = 'Prowl [' + priority + ']: '

        title = values.get('title', None)
        if title is not None and len(title) > 0:
            subst = self.substitute(title, validateOnly=True)
            if subst[0]: desc += title + '-'
            else: errors['title'] = subst[1]

        message = values.get('message', None)
        if message is not None and len(message) > 0:
            subst = self.substitute(message, validateOnly=True)
            if subst[0]: desc += message
            else: errors['message'] = subst[1]

        # FIXME a message or title is required

        url = values.get('url', None)
        if url is not None and len(url) > 0:
            subst = self.substitute(url, validateOnly=True)
            if not subst[0]: errors['url'] = subst[1]

        # create the description for Indigo's UI
        values['description'] = desc

        return ((len(errors) == 0), values, errors)

    #---------------------------------------------------------------------------
    def notify(self, action):
        # load fields and send using the Prowl client
        title = self.substitute(action.props.get('title', ''))
        message = self.substitute(action.props.get('message', ''))
        url = self.substitute(action.props.get('url', ''))
        priority = int(action.props.get('priority', '0'))

        self.logger.debug(u'notify: [%d] %s - %s', priority, title, message)
        self.client.notify(message=message, title=title, priority=priority, url=url)

    #---------------------------------------------------------------------------
    def loadPluginPrefs(self, values):
        iplug.PluginBase.loadPluginPrefs(self, values)

        appname = values.get('appname', None)
        apikey = values.get('apikey', None)

        self.logger.debug(u'initializing Prowl client: %s {%s}', appname, apikey)
        self.client = prowl.Client(appname, apikey)

