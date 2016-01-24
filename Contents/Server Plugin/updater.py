#!/usr/bin/env python2.5

# this module will check for newer releases on a github repo and update accordingly

# in order for this to work properly, tags for releases should be in the format:
#   v{major}.{minor}.{revision} - e.g. v1.0.0

# also, only full releases will be used...  draft and pre-releases are not considered

import json
import httplib, urllib

################################################################################
def has_update(owner, repo, currentVersion, plugin=None):
    latestReleaseAPI = '/repos/' + owner + '/' + repo + '/releases/latest'
    if plugin: plugin.debugLog(latestReleaseAPI)

    headers = {
        'User-Agent': 'Indigo-Plugin-Updater',
        'Accept': 'application/vnd.github.v3+json'
    }

    try:
        conn = httplib.HTTPSConnection('api.github.com')
        conn.request('GET', latestReleaseAPI, None, headers)
        resp = conn.getresponse()
        release = json.loads(resp.read())

    except Exception, e:
        if plugin: plugin.errorLog(str(e))

    latestVersion = release['tag_name'].lstrip('v')
    latestReleaseURL = release['html_url']

    plugin.debugLog('Latest release is: ' + latestVersion)
    plugin.debugLog(latestReleaseURL)

    if (ver(latestVersion) > ver(currentVersion)):
        return latestReleaseURL

    return None

################################################################################
# maps the standard version string as a tuple for comparrison
def ver(vstr): return tuple(map(int, (vstr.split("."))))
