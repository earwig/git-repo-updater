# -*- coding: utf-8  -*-
#
# Copyright (C) 2011-2014 Ben Kurtovic <ben.kurtovic@gmail.com>
# See the LICENSE file for details.

from __future__ import print_function

import os

from colorama import Fore, Style
from git import Repo, exc

__all__ = ["update_bookmarks", "update_directories"]

BOLD = Style.BRIGHT
RED = Fore.RED + BOLD
GREEN = Fore.GREEN + BOLD
BLUE = Fore.BLUE + BOLD
RESET = Style.RESET_ALL

INDENT1 = " " * 3
INDENT2 = " " * 7
ERROR = RED + "Error:" + RESET

class _Stasher(object):
    """Manages the stash state of a given repository."""

    def __init__(self, repo):
        self._repo = repo
        self._clean = self._stashed = False

    def clean(self):
        """Ensure the working directory is clean, so we can do checkouts."""
        if not self._clean:
            res = self._repo.git.stash("--all")
            self._clean = True
            if res != "No local changes to save":
                self._stashed = True

    def restore(self):
        """Restore the pre-stash state."""
        if self._stashed:
            self._repo.git.stash("pop", "--index")


def _read_config(repo, attr):
    """Read an attribute from git config."""
    try:
        return repo.git.config("--get", attr)
    except exc.GitCommandError:
        return None

def _fetch_remote(remote):
    """Fetch a given remote, and display progress info along the way."""
    print(INDENT2, "Fetching", remote.name, end="...")
    remote.fetch()  ### TODO: show progress
    print(" done.")

def _rebase(repo, name):
    """Rebase the current HEAD of *repo* onto the branch *name*."""
    print(" rebasing...", end="")
    try:
        res = repo.git.rebase(name)
    except exc.GitCommandError as err:
        if "unstaged changes" in err.stderr:
            print(" error:", "unstaged changes.")
        elif "uncommitted changes" in err.stderr:
            print(" error:", "uncommitted changes.")
        else:
            try:
                repo.git.rebase("--abort")
            except exc.GitCommandError:
                pass
            print(" error:", err.stderr.replace("\n", " "))
    else:
        print(" done.")

def _merge(repo, name):
    """Merge the branch *name* into the current HEAD of *repo*."""
    print(" merging...", end="")
    try:
        repo.git.merge(name)
    except exc.GitCommandError as err:
        print(err)
        ### TODO: etc
    else:
        print(" done.")

def _update_branch(repo, branch, merge, rebase, stasher=None):
    """Update a single branch."""
    print(INDENT2, "Updating", branch, end="...")
    upstream = branch.tracking_branch()
    if not upstream:
        print(" skipped: no upstream is tracked.")
        return
    if branch.commit == upstream.commit:  ### TODO: a better check is possible
        print(" up to date.")
        return
    if stasher:
        stasher.clean()
    branch.checkout()
    config_attr = "branch.{0}.rebase".format(branch.name)
    if not merge and (rebase or _read_config(repo, config_attr)):
        _rebase(repo, upstream.name)
    else:
        _merge(repo, upstream.name)

def _update_repository(repo, current_only=False, rebase=False, merge=False,
                       verbose=False):
    """Update a single git repository by fetching remotes and rebasing/merging.

    The specific actions depend on the arguments given. We will fetch all
    remotes if *current_only* is ``False``, or only the remote tracked by the
    current branch if ``True``. By default, we will merge unless
    ``pull.rebase`` or ``branch.<name>.rebase`` is set in config; *rebase* will
    cause us to always rebase with ``--preserve-merges``, and *merge* will
    cause us to always merge. If *verbose* is set, additional information is
    printed out for the user.
    """
    print(INDENT1, BOLD + os.path.split(repo.working_dir)[1] + ":")

    active = repo.active_branch
    if current_only:
        ref = active.tracking_branch()
        if not ref:
            print(INDENT2, ERROR, "no remote tracked by current branch.")
            return
        remotes = [repo.remotes[ref.remote_name]]
    else:
        remotes = repo.remotes
    if not remotes:
        print(INDENT2, ERROR, "no remotes configured to pull from.")
        return

    for remote in remotes:
        _fetch_remote(remote)

    rebase = rebase or _read_config(repo, "pull.rebase")
    _update_branch(repo, active, merge, rebase)
    branches = set(repo.heads) - {active}
    if branches:
        stasher = _Stasher(repo)
        try:
            for branch in sorted(branches, key=lambda b: b.name):
                _update_branch(repo, branch, merge, rebase, stasher)
        finally:
            active.checkout()
            stasher.restore()

def _update_subdirectories(path, long_name, update_args):
    """Update all subdirectories that are git repos in a given directory."""
    repos = []
    for item in os.listdir(path):
        try:
            repo = Repo(os.path.join(path, item))
        except (exc.InvalidGitRepositoryError, exc.NoSuchPathError):
            continue
        repos.append(repo)

    suffix = "ies" if len(repos) != 1 else "y"
    print(long_name[0].upper() + long_name[1:],
          "contains {0} git repositor{1}:".format(len(repos), suffix))
    for repo in sorted(repos, key=lambda r: os.path.split(r.working_dir)[1]):
        _update_repository(repo, *update_args)

def _update_directory(path, update_args, is_bookmark=False):
    """Update a particular directory.

    Determine whether the directory is a git repo on its own, a directory of
    git repositories, or something invalid. If the first, update the single
    repository; if the second, update all repositories contained within; if the
    third, print an error.
    """
    dir_type = "bookmark" if is_bookmark else "directory"
    long_name = dir_type + ' "' + BOLD + path + RESET + '"'

    try:
        repo = Repo(path)
    except exc.NoSuchPathError:
        print(ERROR, long_name, "doesn't exist!")
    except exc.InvalidGitRepositoryError:
        if os.path.isdir(path):
            _update_subdirectories(path, long_name, update_args)
        else:
            print(ERROR, long_name, "isn't a repository!")
    else:
        long_name = (dir_type.capitalize() + ' "' + BOLD + repo.working_dir +
                     RESET + '"')
        print(long_name, "is a git repository:")
        _update_repository(repo, *update_args)

def update_bookmarks(bookmarks, update_args):
    """Loop through and update all bookmarks."""
    if bookmarks:
        for path, name in bookmarks:
            _update_directory(path, update_args, is_bookmark=True)
    else:
        print("You don't have any bookmarks configured! Get help with 'gitup -h'.")

def update_directories(paths, update_args):
    """Update a list of directories supplied by command arguments."""
    for path in paths:
        full_path = os.path.abspath(path)
        _update_directory(full_path, update_args, is_bookmark=False)
