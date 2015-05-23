__gitup__ (the _git-repo-updater_)

gitup is a tool designed to update a large number of git repositories at once.
It is smart enough to handle multiple remotes, branches, dirty working
directories, and more, hopefully providing a great way to get everything
up-to-date for short periods of internet access between long periods of none.

gitup should work on OS X, Linux, and Windows. You should have the latest
version of git and at least Python 2.7 installed.

# Installation

With [Homebrew](http://brew.sh/):

    brew install pr0d1r2/contrib/gitup && brew link gitup

## From source

First:

    git clone git://github.com/earwig/git-repo-updater.git
    cd git-repo-updater

Then, to install for everyone:

    sudo python setup.py install

...or for just yourself (make sure you have `~/.local/bin` in your PATH):

    python setup.py install --user

Finally, simply delete the `git-repo-updater` directory, and you're done!

__Note:__ If you are using Windows, you may wish to add a macro so you can
invoke gitup in any directory. Note that `C:\python27\` refers to the
directory where Python is installed:

    DOSKEY gitup=c:\python27\python.exe c:\python27\Scripts\gitup $*

# Usage

There are two ways to update repos: you can pass them as command arguments,
or save them as "bookmarks".

For example:

    gitup ~/repos/foo ~/repos/bar ~/repos/baz

will automatically pull to the `foo`, `bar`, and `baz` git repositories.
Additionally, you can just type:

    gitup ~/repos

to automatically update all git repositories in that directory.

To add a bookmark (or bookmarks), either of these will work:

    gitup --add ~/repos/foo ~/repos/bar ~/repos/baz
    gitup --add ~/repos

Then, to update all of your bookmarks, just run gitup without args:

    gitup

Delete a bookmark:

    gitup --delete ~/repos

View your current bookmarks:

    gitup --list

You can mix and match bookmarks and command arguments:

    gitup --add ~/repos/foo ~/repos/bar
    gitup ~/repos/baz            # update 'baz' only
    gitup                        # update 'foo' and 'bar' only
    gitup ~/repos/baz --update   # update all three!

Update all git repositories in your current directory:

    gitup .

By default, gitup will fetch all remotes in a repository. Pass `--current-only`
(or `-c`) to make it only fetch the remote tracked by the current branch.

gitup will _merge_ upstream branches by default unless `pull.rebase` or
`branch.<name>.rebase` is specified in git's config. Pass `--rebase` or `-r` to
make it always _rebase_ (like doing `git pull --rebase=preserve`). Pass
`--merge` or `-m` to make it always merge.

For a list of all command arguments and abbreviations:

    gitup --help

Finally, all paths can be either absolute (e.g. `/path/to/repo`) or relative
(e.g. `../my/repo`).
