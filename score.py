from os import path, system
import json
import operator

from colors import bcolors


class Leaderboard(object):

    """Calculation of committs per user and score assignment."""

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
        """Add score to commit's author."""
        if not self._score["last_commit"] == sha:
            self._score["last_commit"] = sha
            if not name in self._score:
                self._score["commiters"][name] = 1
            else:
                self._score["commiters"][name] += 1
            self._score_file.close()
            self._score_file = open("scores.sco", "w+")
            self._score_file.write(json.dumps(self._score))

    def print_leaderboard(self):
        """Print leaderboard."""
        clear = lambda: system('clear')
        clear()
        commiters = self._score["commiters"]
        sorted_score = sorted(
            commiters.iteritems(), key=operator.itemgetter(1))
        to_print = bcolors.HEADER + \
            "LEADERBOARD : \n ===========\n" + bcolors.ENDC
        for score in sorted_score:
            to_print += "\n"
            to_print += str(score[0])
            to_print += "  "
            to_print += bcolors.OKBLUE + str(score[1]) + bcolors.ENDC

        print to_print
