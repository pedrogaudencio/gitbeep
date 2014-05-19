gitbeep
=======

It listens to a given repository, everytime there's a new commit it displays the author and commit message and plays a song of choice. Also, songs are costumizable for each author.


Installation
------------

Run `pip install -r requirements.txt`

Execution
---------

Run `python go.py`

Configure
---------

In `config.json`:

    commit_repo = 'https://api.github.com/repos/:username/:repository/commits'

    pullrequests_repo = 'https://api.github.com/repos/:username/:repository/pulls'

    song_folder = 'path/to/song/folder'

    music: 'song_of_choice.mp3'

    individual: {'Author 1': 'song1.mp3',
                 'Author 2': 'song2.mp3',
                 'Author 3': 'song3.mp3',
                }
