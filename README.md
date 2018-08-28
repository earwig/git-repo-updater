__gitup__ (the _git-repo-updater_)

gitup is a tool for updating multiple git repositories at once. It is smart
enough to handle several remotes, dirty working directories, diverged local
branches, detached HEADs, and more. It was originally created to manage a large
collection of projects and deal with sporadic internet access.

gitup should work on OS X, Linux, and Windows. You should have the latest
version of git and either Python 2.7 or Python 3 installed.

# Installation

With [Homebrew](http://brew.sh/):

    brew install gitup

## From source

First:

    git clone git://github.com/earwig/git-repo-updater.git
    cd git-repo-updater

Then, to install for everyone:

    sudo python setup.py install

or for just yourself (make sure you have `~/.local/bin` in your PATH):

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

To add bookmarks, either of these will work:

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

You can control how deep gitup will look for repositories in a given directory,
if that directory is not a git repo by itself, with the `--depth` (or `-t`)
option. `--depth 0` will disable recursion entirely, meaning the provided paths
must be repos by themselves. `--depth 1` will descend one level (this is the
old behavior from pre-0.5 gitup). `--depth -1` will recurse indefinitely,
which is not recommended. The default is `--depth 3`.

By default, gitup will fetch all remotes in a repository. Pass `--current-only`
(or `-c`) to make it fetch only the remote tracked by the current branch.

Also by default, gitup will try to fast-forward all branches that have
upstreams configured. It will always skip branches where this is not possible
(e.g. dirty working directory or a merge/rebase is required). Pass
`--fetch-only` (or `-f`) to skip this step and only fetch remotes.

After fetching, gitup will _keep_ remote-tracking branches that no longer exist
upstream. Pass `--prune` (or `-p`) to delete them, or set `fetch.prune` or
`remote.<name>.prune` in your git config to do this by default.

For a full list of all command arguments and abbreviations:

    gitup --help
