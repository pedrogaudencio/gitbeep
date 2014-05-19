import requests
import json
from time import sleep
from datetime import datetime
from os import path
import subprocess
import shlex
import select
import sys
import logging
import curses
import signal

from colors import bcolors
from score import Leaderboard
from pullrequests import PRCalc




config = {}
# stdscr = curses.initscr()
# curses.noecho()
# curses.cbreak()
# stdscr.keypad(1)


my_leaderboard = Leaderboard()
pull_requests = PRCalc()


def fetch_newest_commit(repo):
    """Fetch the newest from the repository."""
    r = requests.get(repo)
    if r.ok:
        repoItem = json.loads(r.text or r.content)
        items = (repoItem[0]['sha'], repoItem[0]['commit'],
                 repoItem[0]['author']['id'])
        return items


def get_song_name(name):
    """
    Get the song name from the configuration file.

    If the author's individual song isn't defined in the
    configuration file, it plays the default one.
    """
    if name not in config['individual'] or not config['individual'][name]:
        return config['music']
    return config['individual']['name']


def play_song(music):
    """Play the given song."""
    play_command = 'mpg123 -q %s' % path.join(config['song_folder'], music)
    proc = subprocess.Popen(shlex.split(play_command), stdout=subprocess.PIPE)
    proc.communicate()


class MainWorker(object):

    def __init__(self, window, config, last_commit_sha):
        self.window = window
        self.config = config
        self.last_commit_sha = last_commit_sha
        signal.signal(signal.SIGINT, self.signal_handler)

    def begin(self):
        while True:
            self.go()
            sleep(10)

    def go(self):
        """
        Main function, always running.

        * fethes the newest commit and compares it to the previous one fetched
        * prints the message if it's new
        * updates the score of its author
        * updates the pull requests storage
        * plays song
        * waits for 10 seconds and repeats everything
        """
        #try:
        newest_commit_sha, commit, user_id = fetch_newest_commit(
            self.config['commit_repo'])
        if newest_commit_sha != self.last_commit_sha:
            self.last_commit_sha = newest_commit_sha
            self.print_commit(commit, user_id, newest_commit_sha)
            my_leaderboard.score_add_commit(commit['author']['name'],
                                            newest_commit_sha)
            pull_requests.update(config['pullrequests_repo'])
            song_to_play = get_song_name(commit['author']['name'])
            play_song(song_to_play)
        #except Exception as e:
            # stdscr.addstr(0, 0, "github doesn't answer {0}".format(e))
            # stdscr.refresh()
            # last_commit_sha = None

    def print_commit(self, commit, user_id, sha):
        """Print the author's name, commit message and merge waiting time."""
        committer = '%s\n%s just got merged!%s\n\n' % \
                    (bcolors.OKGREEN,
                     commit['author']['name'],
                     bcolors.ENDC)
        message = '%s' % commit['message']
        # merging_time = pull_requests.get_frustration_time(
        #     user_id, sha, commit['author']['date'])
        # merging_timep = '%sIt took %s to get merged.%s\n\n' % \
        #                 (bcolors.OKBLUE, merging_time, bcolors.ENDC)
        line = 0

        lines_to_print = committer + message  # + merging_timep
        lines_to_print = lines_to_print.split('\n')
        for i in lines_to_print:
            self.window.addstr(line, 0, i)
            self.window.refresh()
            line = line + 1

    def signal_handler(self, signal, frame):
        """ Handles user interrupt """
        self.window.addstr("You pressed Ctrl+C!")
        self.window.refresh()
        sys.exit(0)


def main(window):
    with open('config.json') as handle:
        config.update(json.load(handle))
    try:
        last_commit = fetch_newest_commit(config['commit_repo'])
    except Exception as e:
        window.addstr(0, 0, "github won't answer {0}".format(e.message))
        window.refresh()
        last_commit = None

    worker = MainWorker(window, config, last_commit)
    worker.begin()


if __name__ == '__main__':
    curses.wrapper(main)
