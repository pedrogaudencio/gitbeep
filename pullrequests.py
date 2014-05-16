import json
from os import path
import requests
import datetime


class PRCalc(object):

    """Calculation of pull requests' time till merging."""

    def __init__(self):

        if path.isfile("pullrequests.req"):
            self._pr_file = open("pullrequests.req", "r+")
        else:
            self._pr_file = open("pullrequests.req", "w+")

        try:
            self._pr = json.loads(self._pr_file.read())
        except ValueError:
            self._pr = {}


    def update_pullrequests(self, repo):
        """Update of pull requests."""
        r = requests.get(repo)

        if r.ok:
            repoItem = json.loads(r.text or r.content)
            for preq in repoItem:
                if preq['user']['id'] not in self._pr:
                    self._pr[preq['user']['id']] = {preq['merge_commit_sha']: preq['created_at']}
                else:
                    self._pr[preq['user']['id']][preq['merge_commit_sha']] = preq['created_at']
            self._pr_file.close()
            self._pr_file = open("pullrequests.req", "w+")
            self._pr_file.write(json.dumps(self._pr))


    def get_frustration_time(self, user_id, sha, commit_time):
        """
        Return time that took to get merged since the commit was done.

        It's hardcoded for now because we need to find a smarter way to do it.
        The problem is that the pull requests' data have to be in storage before
        the newly merged commit is checked...
        """
        user_id = '416548'
        sha = 'e3803e979be9c0de21d8855ef1935b05054f5ed9'

        prtime = datetime.datetime.strptime(self._pr[user_id][sha], '%Y-%m-%dT%H:%M:%SZ')
        ctime = datetime.datetime.strptime(commit_time, '%Y-%m-%dT%H:%M:%SZ')

        return ctime - prtime
