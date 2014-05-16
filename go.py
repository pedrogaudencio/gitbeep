import requests
import json
from time import sleep
import subprocess
import shlex
from os import path

config = {}


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


def fetch_last_commit(repo):
    r = requests.get(repo)

    if(r.ok):
        repoItem = json.loads(r.text or r.content)
        return repoItem[0]['sha'], repoItem[0]['commit']


def check_committer(name):
    if name not in config['individual']:
        return config['music']
    return config['individual']['name']


def print_commit(commit):
    committer = '%s\n%s just got merged in pu!\033[0m\n\n' % (bcolors.OKGREEN, commit['author']['name'])
    message = '%s' % commit['message']
    print committer, message, '\n'


def play_song(music):
    play_command = 'mpg123 -q %s' % path.join(config['song_folder'], music)
    proc = subprocess.Popen(shlex.split(play_command), stdout=subprocess.PIPE)
    proc.communicate()


def go(last_commit_sha):
    newest_commit_sha, commit = fetch_last_commit(config['repository'])
    if newest_commit_sha != last_commit_sha:
        last_commit_sha = newest_commit_sha
        print_commit(commit)
        #song_to_play = check_committer(commit['author']['name'])
        song_to_play = config['music']
        play_song(song_to_play)
    sleep(60)
    go(last_commit_sha)


if __name__ == '__main__':
    execfile("gitbeep.conf", config)
    last_commit = fetch_last_commit(config['repository'])
    go(last_commit)
