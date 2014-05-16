import requests
import json
from time import sleep, time
import subprocess
import shlex
from os import path
import math
from score import Leaderboard
config = {}


global_time = time()

my_leaderboard = Leaderboard()

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


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
    print committer, message, '\n', '\n', '\n', time_to_merge_something


def play_song(music):
    play_command = 'mpg123 -q %s' % path.join(config['song_folder'], music)
    proc = subprocess.Popen(shlex.split(play_command), stdout=subprocess.PIPE)
    proc.communicate()


def go(last_commit_sha):
    newest_commit_sha, commit = fetch_last_commit(config['repository'])
    if newest_commit_sha != last_commit_sha:
        last_commit_sha = newest_commit_sha
        print_commit(commit)
        my_leaderboard.score_add_commit(commit['author']['name'], newest_commit_sha)
        song_to_play = check_committer(commit['author']['name'])
        play_song(song_to_play)
        global_time = time()
    sleep(60)
    go(last_commit_sha)


if __name__ == '__main__':
    execfile("gitbeep.conf", config)
    last_commit = fetch_last_commit(config['repository'])
    go(last_commit)
