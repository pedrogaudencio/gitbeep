import requests
import json
from time import sleep
import subprocess
import shlex

invenio_repo = 'https://api.github.com/repos/jirikuncar/invenio/commits'
imperial_march = 'beepmarch.sh'

song_dict = {'Pedro Gaudencio': '',
             'Guillaume Lastecoueres': '',
             'Jan Age Lavik': '',
            }


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
    return song_dict['name']


def print_commit(commit):
    committer = '%s\n%s just got merged in pu!\033[0m\n\n' % (bcolors.OKGREEN, commit['author']['name'])
    message = '%s' % commit['message']
    print committer, message, '\n'


def play_song(sheet_paper):
    play_command = 'bash %s' % sheet_paper
    proc = subprocess.Popen(shlex.split(play_command), stdout=subprocess.PIPE)
    proc.communicate()


def go(last_commit_sha):
    newest_commit_sha, commit = fetch_last_commit(invenio_repo)
    if newest_commit_sha != last_commit_sha:
        last_commit_sha = newest_commit_sha
        print_commit(commit)
        #song_to_play = check_committer(commit['author']['name'])
        song_to_play = imperial_march
        play_song(song_to_play)
    sleep(60)
    go(last_commit_sha)


if __name__ == '__main__':
    last_commit = fetch_last_commit(invenio_repo)
    go(last_commit)
