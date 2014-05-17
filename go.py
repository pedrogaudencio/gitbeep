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


def signal_handler(signal, frame):
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()
    print('You pressed Ctrl+C!')
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)


config = {}
stdscr = curses.initscr()
curses.noecho()
curses.cbreak()

my_leaderboard = Leaderboard()
pull_requests = PRCalc()


def fetch_newest_commit(repo):
    """Fetch the newest from the repository."""
    r = requests.get(repo)

    if r.ok:
        repoItem = json.loads(r.text or r.content)
        return repoItem[0]['sha'], repoItem[0]['commit'], repoItem[0]['author']['id']


def get_song_name(name):
    """
    Get the song name from the configuration file.

    If the author's individual song isn't defined in the
    configuration file, it plays the default one.
    """
    if name not in config['individual']:
        return config['music']
    return config['individual']['name']


def print_commit(commit, user_id, sha):
    """Print the author's name, commit message and merge waiting time."""
    committer = '%s\n%s just got merged!%s\n\n' % \
                (bcolors.OKGREEN,
                 commit['author']['name'],
                 # '{:%Y-%m-%d %H:%M:%S}'.format(datetime.strptime(commit['author']['date'],
                 #                                                 '%Y-%m-%dT%H:%M:%SZ')),
                 bcolors.ENDC)
    message = '%s' % commit['message']
    merging_time = pull_requests.get_frustration_time(user_id,
                                                      sha,
                                                      commit['author']['date'])
    merging_timep = '%sIt took %s to get merged.%s\n\n' % \
                    (bcolors.OKBLUE, merging_time, bcolors.ENDC)
    line = 0

    lines_to_print = committer + message + merging_timep
    lines_to_print = lines_to_print.split('\n')
    for i in lines_to_print:
        stdscr.addstr(line, 0, i)
        stdscr.refresh()
        line = line + 1


def play_song(music):
    """Play the given song."""
    play_command = 'mpg123 -q %s' % path.join(config['song_folder'], music)
    proc = subprocess.Popen(shlex.split(play_command), stdout=subprocess.PIPE)
    proc.communicate()


def go(last_commit_sha):
    """
    Main function, always running.

    * fethes the newest commit and compares it to the previous one fetched
    * prints the message if it's new
    * updates the score of its author
    * updates the pull requests storage
    * plays song
    * waits for 10 seconds and repeats everything
    """
    try:
        newest_commit_sha, commit, user_id = fetch_newest_commit(
            config['commit_repo'])
        if newest_commit_sha != last_commit_sha:
            last_commit_sha = newest_commit_sha
            print_commit(commit, user_id, newest_commit_sha)
            my_leaderboard.score_add_commit(commit['author']['name'],
                                            newest_commit_sha)
            pull_requests.update(config['pullrequests_repo'])
            song_to_play = get_song_name(commit['author']['name'])
            play_song(song_to_play)
    except:
        print "github doesn't answer"
        last_commit_sha = None
    sleep(10)
    go(last_commit_sha)


def heardEnter():
    i, o, e = select.select([sys.stdin], [], [], 0.001)
    print "bitch"
    for s in i:
        if s == sys.stdin:
            input = sys.stdin.readline()
            print input


if __name__ == '__main__':
    execfile("gitbeep.conf", config)
    try:
        last_commit = fetch_newest_commit(config['commit_repo'])
    except:
        last_commit = None

    go(last_commit)
