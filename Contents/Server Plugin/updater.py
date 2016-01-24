#!/usr/bin/env python2.5

# this module will check for newer releases on a github repo and update accordingly
# in order for this to work properly, tags for releases must be in the format:
#   v{major}.{minor}.{revision} - e.g. v1.0.0

import json
import httplib, urllib

def update(owner, repo, currentVersion, targetPath=None, plugin=None):
    latestUrl = '/repos/' + owner + '/' + repo + '/releases/latest'
    if plugin: plugin.debugLog(latestUrl)

    headers = {
        'User-Agent': 'Indigo-Plugin-Updater',
        'Accept': 'application/vnd.github.v3+json'
    }

    try:
        conn = httplib.HTTPSConnection('api.github.com')
        conn.request('GET', latestUrl, None, headers)
        resp = conn.getresponse()
        release = json.loads(resp.read())

    except Exception, e:
        if plugin: plugin.errorLog(str(e))

    latestVersion = release['tag_name']
    plugin.debugLog('Latest release is: ' + latestVersion)
