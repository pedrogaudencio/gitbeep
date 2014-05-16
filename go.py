import requests
import json
from time import sleep
import subprocess
import shlex
from os import path
from score import Leaderboard
from pullrequests import PRCalc
import select
import sys
import logging
from colors import bcolors
import curses
import signal
import sys


def signal_handler(signal, frame):
    curses.nocbreak();
    stdscr.keypad(0);
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


def fetch_last_commit(repo):
    r = requests.get(repo)

    if r.ok:
        repoItem = json.loads(r.text or r.content)
        return repoItem[0]['sha'], repoItem[0]['commit'], repoItem[0]['author']['id']


def check_committer(name):
    if name not in config['individual']:
        return config['music']
    return config['individual']['name']


def print_commit(commit, user_id, sha):
    committer = '%s\n%s just got merged!%s\n\n' % (
        bcolors.OKGREEN, commit['author']['name'], bcolors.ENDC)
    message = '%s' % commit['message']
    merging_time = pull_requests.get_frustration_time(user_id,
                                                      sha,
                                                      commit['author']['date'])
    merging_timep = '%sI took %s to get merged.%s' % (bcolors.OKBLUE, merging_time, bcolors.ENDC)
    line = 0

    lines_to_print =  committer + message +  '\n\n\n' + merging_timep
    lines_to_print = lines_to_print.split('\n')
    for i in lines_to_print:
        stdscr.addstr(line, 0, i)
        stdscr.refresh()
        line = line + 1


def play_song(music):
    play_command = 'mpg123 -q %s' % path.join(config['song_folder'], music)
    proc = subprocess.Popen(shlex.split(play_command), stdout=subprocess.PIPE)
    proc.communicate()


def go(last_commit_sha):
    try:
        newest_commit_sha, commit, user_id = fetch_last_commit(config['repository'])
        if newest_commit_sha != last_commit_sha:
            last_commit_sha = newest_commit_sha
            print_commit(commit, user_id, newest_commit_sha)
            my_leaderboard.score_add_commit(commit['author']['name'],
                                            newest_commit_sha)
            pull_requests.update_pullrequests(config['pullrequests_repo'])
            song_to_play = check_committer(commit['author']['name'])
            play_song(song_to_play)
    except:
        print "github doesn't answer"
        last_commit_sha = None
    sleep(1)
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
        last_commit = fetch_last_commit(config['commit_repo'])
    except:
        last_commit = None

    go(last_commit)
