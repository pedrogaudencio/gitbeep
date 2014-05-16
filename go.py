import requests
import json
from time import sleep, time
import subprocess
import shlex
from os import path
import math
from score import Leaderboard
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

global_time = time()

my_leaderboard = Leaderboard()




def fetch_last_commit(repo):
    r = requests.get(repo)

    if r.ok:
        repoItem = json.loads(r.text or r.content)
        return repoItem[0]['sha'], repoItem[0]['commit']


def check_committer(name):
    if name not in config['individual']:
        return config['music']
    return config['individual']['name']


def format_duration(delay):
    days = math.floor(delay / 86400)
    delay -= 86400 * days
    hours = math.floor(delay / 3600)
    delay -= 3600 * hours
    minutes = math.floor(delay / 60)
    delay -= 60 * minutes
    delay = math.floor(delay)
    return " {0} days, {1} hours, {2} minutes, {3} seconds".format(int(days),
                                                                   int(hours),
                                                                   int(minutes),
                                                                   int(delay))


def print_commit(commit):

    committer = '%s\n%s just got merged in pu!\033[0m\n\n' % (
        bcolors.OKGREEN, commit['author']['name'])
    message = '%s' % commit['message']
    time_to_merge_something = "It took {0}  to merge something.".format(
        format_duration(time() - global_time))
    line = 0

    lines_to_print =  committer + message +  '\n\n\n' + time_to_merge_something
    lines_to_print = lines_to_print.split('\n')
    for i in lines_to_print:
        stdscr.addstr(line, 0, i)
        stdscr.refresh()
        line = line + 1
    # print committer, message, '\n', '\n', '\n', time_to_merge_something


def play_song(music):
    play_command = 'mpg123 -q %s' % path.join(config['song_folder'], music)
    proc = subprocess.Popen(shlex.split(play_command), stdout=subprocess.PIPE)
    proc.communicate()


def go(last_commit_sha):
    try:
        newest_commit_sha, commit = fetch_last_commit(config['repository'])
        if newest_commit_sha != last_commit_sha:
            last_commit_sha = newest_commit_sha
            print_commit(commit)
            my_leaderboard.score_add_commit(commit['author']['name'],
                                            newest_commit_sha)
            song_to_play = check_committer(commit['author']['name'])
            play_song(song_to_play)
            global_time = time()
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
        last_commit = fetch_last_commit(config['repository'])
    except:
        last_commit = None


    go(last_commit)

