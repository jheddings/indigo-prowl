#!/usr/bin/env python2.5

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# this module will check for newer releases on a github repo and update accordingly

# in order for this to work properly, tags for releases should be in the format:
#   v{major}.{minor}.{revision} - e.g. v1.0.0

# also, only full releases will be used...  draft and pre-releases are not considered

import json
import httplib

class GitHubUpdater(object):

    #---------------------------------------------------------------------------
    def __init__(self, owner, repo, plugin=None):
        self.owner = owner
        self.repo = repo
        self.plugin = plugin

    #---------------------------------------------------------------------------
    # returns the URL for an update if there is one
    def getUpdate(self, currentVersion):
        release = self.getLatestRelease()

        if (release == None):
            self._debug('No release available')
            return None

        # TODO we should have some better error checking in here...

        # assume the tag is the release version
        latestVersion = release['tag_name'].lstrip('v')
        latestReleaseURL = release['html_url']

        self._debug('Latest release is: %s' % latestVersion)
        self._debug(latestReleaseURL)

        if (ver(latestVersion) > ver(currentVersion)):
            return latestReleaseURL

        return None

    #---------------------------------------------------------------------------
    # returns the latest release information from a given user / repo
    def getLatestRelease(self):
        apiPath = '/repos/' + self.owner + '/' + self.repo + '/releases/latest'
        self._debug(apiPath)

        headers = {
            'User-Agent': 'Indigo-Plugin-Updater',
            'Accept': 'application/vnd.github.v3+json'
        }

        release = None

        try:
            conn = httplib.HTTPSConnection('api.github.com')
            conn.request('GET', apiPath, None, headers)
            resp = conn.getresponse()

            # maybe check out https://developer.github.com/v3/rate_limit/
            rateLimit = int(resp.getheader('X-RateLimit-Limit', -1))
            rateRemain = int(resp.getheader('X-RateLimit-Remaining', -1))
            rateReset = int(resp.getheader('X-RateLimit-Reset', -1))

            self._debug('HTTP %d %s' % (resp.status, resp.reason))
            self._debug('Rate Limit: %d/%d' % (rateRemain, rateLimit))

            if (resp.status == 200):
                release = json.loads(resp.read())
            else:
                self._error('ERROR: %s' % resp.reason)

        except Exception as e:
            self._error(str(e))

        return release

    #---------------------------------------------------------------------------
    # convenience method for debug messages
    def _debug(self, msg):
        if self.plugin:
            self.plugin.debugLog(msg)

    #---------------------------------------------------------------------------
    # convenience method for error messages
    def _error(self, msg):
        if self.plugin:
            self.plugin.errorLog(msg)

################################################################################
# maps the standard version string as a tuple for comparrison
def ver(vstr): return tuple(map(int, (vstr.split('.'))))
