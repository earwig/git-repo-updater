__gitup__ (the _git-repo-updater_)

[![ci](https://github.com/earwig/git-repo-updater/actions/workflows/ci.yml/badge.svg)](https://github.com/earwig/git-repo-updater/actions/workflows/ci.yml)

gitup is a tool for updating multiple git repositories at once. It is smart
enough to handle several remotes, dirty working directories, diverged local
branches, detached HEADs, and more. It was originally created to manage a large
collection of projects and deal with sporadic internet access.

gitup works on macOS, Linux, and Windows. You should have a recent version of
git and Python 3.9+ installed.

# Installation

With [uv](https://docs.astral.sh/uv/):

    uv tool install gitup

With [pipx](https://pipx.pypa.io/stable/):

    pipx install gitup

With [pip](https://github.com/pypa/pip/):

    pip install gitup

With [Homebrew](http://brew.sh/):

    brew install gitup

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
