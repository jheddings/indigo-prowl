#!/usr/bin/env python2.5

import prowl

from ghpu import GitHubPluginUpdater

# TODO test this in a new DB

################################################################################
class Plugin(indigo.PluginBase):

    #---------------------------------------------------------------------------
    def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
        self.updater = GitHubPluginUpdater(self)
        self._loadPluginPrefs(pluginPrefs)

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
                errors['apikey'] = 'Invalid API key (or call limit exceeded)'

        return ((len(errors) == 0), values, errors)

    #---------------------------------------------------------------------------
    def closedPrefsConfigUi(self, values, canceled):
        if canceled: return
        self._loadPluginPrefs(values)

    #---------------------------------------------------------------------------
    def validateActionConfigUi(self, values, typeId, devId):
        errors = indigo.Dict()

        # building a description for the Indigio UI...
        priority = values['priority'];
        header = 'Prowl [' + priority + ']: '

        # the title is not required, but check substitutions if it is there...
        title = values.get('title', None)
        if title is not None and len(title) > 0:
            subst = self.substitute(title, validateOnly=True)
            if (subst[0]): header += title + '-'
            else: errors['title'] = subst[1]

        # a message is required, and we'll verify substitutions
        message = values.get('message', None)
        if message is None or len(message) == 0:
            errors['message'] = 'You must provide a message'
        else:
            subst = self.substitute(message, validateOnly=True)
            if not subst[0]: errors['message'] = subst[1]

        # create the description for Indigo's UI
        values['description'] = header + message

        return ((len(errors) == 0), values, errors)

    #---------------------------------------------------------------------------
    def notify(self, action):
        # load fields and send using the Prowl client
        title = self.substitute(action.props.get('title', ''))
        message = self.substitute(action.props.get('message', ''))
        priority = int(action.props.get('priority', '0'))

        # TODO debug logging here
        self.client.notify(message, title=title, priority=priority)

    #---------------------------------------------------------------------------
    def _loadPluginPrefs(self, values):
        logLevelTxt = values.get('logLevel', None)

        if logLevelTxt is None:
            self.logLevel = 20
        else:
            logLevel = int(logLevelTxt)
            self.logLevel = logLevel

        self.indigo_log_handler.setLevel(self.logLevel)
        self.logger.debug(u'pluginPrefs[logLevel] - %s', self.logLevel)

        appname = values.get('appname', None)
        apikey = values.get('apikey', None)
        self.client = prowl.Client(appname, apikey)

