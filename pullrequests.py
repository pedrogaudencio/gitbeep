import json
from os import path
import requests
from datetime import datetime


class PRCalc(object):

    """Calculation of pull requests' time till merging."""

    def __init__(self):

        if path.isfile("pullrequests.json"):
            self._pr_file = open("pullrequests.json", "r+")
        else:
            self._pr_file = open("pullrequests.json", "w+")

        try:
            self._pr = json.loads(self._pr_file.read())
        except ValueError:
            self._pr = {}

    def update(self, repo):
        """Update pull requests."""
        r = requests.get(repo)

        if r.ok:
            repoItem = json.loads(r.text or r.content)
            for preq in repoItem:
                if preq['user']['id'] not in self._pr:
                    self._pr[preq['user']['id']] = {
                        preq['merge_commit_sha']: preq['created_at']}
                else:
                    self._pr[preq['user']['id']][
                        preq['merge_commit_sha']] = preq['created_at']
            self._pr_file.close()
            self._pr_file = open("pullrequests.json", "w+")
            self._pr_file.write(json.dumps(self._pr))

    def get_frustration_time(self, user_id, sha, commit_time):
        """Return time that took to get merged since the commit was done."""

        prtime = datetime.strptime(
            self._pr[user_id][sha], '%Y-%m-%dT%H:%M:%SZ')
        ctime = datetime.strptime(commit_time, '%Y-%m-%dT%H:%M:%SZ')

        return ctime - prtime
