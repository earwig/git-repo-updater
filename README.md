__gitup__ (the _git-repo-updater_)

gitup is a tool designed to pull to a large number of git repositories at once.
It is smart enough to ignore projects with dirty working directories, and
provides a great way to get everything up-to-date for those short periods of
internet access between long periods of none.

gitup works on both OS X and Linux. You should have the latest version of git
and at least Python 2.7 installed.

# Installation

First:

    git clone git://github.com/earwig/git-repo-updater.git
    cd git-repo-updater

Then, to install for everyone:

    sudo python setup.py install

...or for just yourself (make sure you have `~/.local/bin` in your PATH):

    python setup.py install --user

Finally, simply delete the `git-repo-updater` directory, and you're done!

# Usage

There are two ways to update projects: you can pass them as command arguments,
or save them as "bookmarks".

For example:

    gitup ~/projects/foo ~/projects/bar ~/projects/baz

...will automatically pull to the `foo`, `bar`, and `baz` git repositories if
their working directories are clean (to avoid merge conflicts). Additionally,
you can just type:

    gitup ~/projects

...to automatically update all git repositories in that directory.

To add a bookmark (or bookmarks), either of these will work:

    gitup --add ~/projects/foo ~/projects/bar ~/projects/baz
    gitup --add ~/projects

Then, to update (pull to) all of your bookmarks, just run gitup without args:

    gitup

Deleting a bookmark is as easy as adding one:

    gitup --delete ~/projects

Want to view your current bookmarks? Simple:

    gitup --list

You can mix and match bookmarks and command arguments:

    gitup --add ~/projects/foo ~/projects/bar
    gitup ~/projects/baz            # update 'baz' only
    gitup                           # update 'foo' and 'bar' only
    gitup ~/projects/baz --update   # update all three!

Want to update all git projects in your current directory?

    gitup .

For a list of all command arguments and abbreviations:

    gitup --help

Finally, all paths can be either absolute (e.g. /path/to/project) or relative
(e.g. ../my/project).
