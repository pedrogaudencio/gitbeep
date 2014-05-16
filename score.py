import json
from os import path


class Leaderboard(object):
    def __init__(self):

        if path.isfile("scores.sco"):
            self._score_file = open("scores.sco", "r+")
        else:
            self._score_file = open("scores.sco", "w+")

        try:
            self._score = json.loads(self._score_file.read())
        except ValueError:
            self._score = {"last_commit": None, "commiters": {}}

    def score_add_commit(self, name, sha):
        if not self._score["last_commit"] == sha:
            self._score["last_commit"] = sha
            if not name in self._score:
                self._score["commiters"][name] = 1
            else:
                self._score["commiters"][name] += 1
            self._score_file.close()
            self._score_file = open("scores.sco", "w+")
            self._score_file.write(json.dumps(self._score))

