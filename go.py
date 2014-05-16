import requests
import json
from time import sleep
import subprocess
import shlex
from os import path
from score import Leaderboard
from pullrequests import PRCalc

config = {}
my_leaderboard = Leaderboard()
pull_requests = PRCalc()


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
        return repoItem[0]['sha'], repoItem[0]['commit'], repoItem[0]['author']['id']


def check_committer(name):
    if name not in config['individual']:
        return config['music']
    return config['individual']['name']


def print_commit(commit, user_id, sha):
    committer = '%s\n%s just got merged in pu!%s\n\n' % (
        bcolors.OKGREEN, commit['author']['name'], bcolors.ENDC)
    message = '%s' % commit['message']
    merging_time = pull_requests.get_frustration_time(user_id,
                                                      sha,
                                                      commit['author']['date'])
    merging_timep = '%sI took %s to get merged.%s' % (bcolors.OKBLUE, merging_time, bcolors.ENDC)
    print committer, message, '\n\n', merging_timep, '\n\n'


def play_song(music):
    play_command = 'mpg123 -q %s' % path.join(config['song_folder'], music)
    proc = subprocess.Popen(shlex.split(play_command), stdout=subprocess.PIPE)
    proc.communicate()


def go(last_commit_sha):
    newest_commit_sha, commit, user_id = fetch_last_commit(config['commit_repo'])
    if newest_commit_sha != last_commit_sha:
        last_commit_sha = newest_commit_sha
        print_commit(commit, user_id, newest_commit_sha)
        my_leaderboard.score_add_commit(commit['author']['name'], newest_commit_sha)
        pull_requests.update_pullrequests(config['pullrequests_repo'])
        song_to_play = check_committer(commit['author']['name'])
        play_song(song_to_play)
    sleep(60)
    go(last_commit_sha)


if __name__ == '__main__':
    execfile("gitbeep.conf", config)
    last_commit = fetch_last_commit(config['commit_repo'])
    go(last_commit)
