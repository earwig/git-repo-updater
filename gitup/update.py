# -*- coding: utf-8  -*-
#
# Copyright (C) 2011-2014 Ben Kurtovic <ben.kurtovic@gmail.com>
# See the LICENSE file for details.

from __future__ import print_function

import os

from colorama import Fore, Style
from git import Repo, exc
from git.util import RemoteProgress

__all__ = ["update_bookmarks", "update_directories"]

BOLD = Style.BRIGHT
RED = Fore.RED + BOLD
GREEN = Fore.GREEN + BOLD
BLUE = Fore.BLUE + BOLD
RESET = Style.RESET_ALL

INDENT1 = " " * 3
INDENT2 = " " * 7
ERROR = RED + "Error:" + RESET

class _ProgressMonitor(RemoteProgress):
    """Displays relevant output during the fetching process."""

    def __init__(self, verbose):
        super(_ProgressMonitor, self).__init__()
        self._verbose = verbose

    def update(self, op_code, cur_count, max_count=None, message=''):
        """Called whenever progress changes. Overrides default behavior."""
        if self._verbose:
            if op_code & self.COUNTING:
                print(" ({0})".format(cur_count), end="")
            elif op_code & (self.COMPRESSING | self.RECEIVING):
                if op_code & self.BEGIN:
                    print("\b, ", end="")
                if op_code & self.END:
                    end = ")"
                else:
                    end = "\b" * (1 + len(cur_count) + len(max_count))
                print("{0}/{1}".format(cur_count, max_count), end=end)
        elif op_code & self.BEGIN:
                print(".", end="")


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

def _format_fetch_result(results):
    """Format and print the results of a verbose fetch."""
    info = [("NEW_HEAD", "new branches"), ("NEW_TAG", "new tags"),
            ("FAST_FORWARD", "updates"), ("ERROR", "errors")]
    rlist = []
    for attr, desc in info:
        names = [res.name for res in results if res.flags & getattr(res, attr)]
        if names:
            rlist.append("{0} ({1})".format(desc, ", ".join(names)))
    print(":", (", ".join(rlist) if rlist else "up to date") + ".")

def _fetch_remotes(remotes, verbose):
    """Fetch a list of remotes, displaying progress info along the way."""
    if verbose:
        for remote in remotes:
            print(INDENT2, "Fetching", remote.name, end="")
            result = remote.fetch(progress=_ProgressMonitor(True))
            _format_fetch_result(result)
    else:
        print(INDENT2, "Fetching:", end=" ")
        for i, remote in enumerate(remotes):
            print(remote.name, end="")
            remote.fetch(progress=_ProgressMonitor(False))
            if i < len(remotes) - 1:
                print(", ", end="")
        print(".")

def _is_up_to_date(repo, branch, upstream):
    """Return whether *branch* is up-to-date with its *upstream*."""
    base = repo.git.merge_base(branch.commit, upstream.commit)
    return repo.commit(base) == upstream.commit

def _rebase(repo, name):
    """Rebase the current HEAD of *repo* onto the branch *name*."""
    print(" rebasing...", end="")
    try:
        res = repo.git.rebase(name)
    except exc.GitCommandError as err:
        msg = err.stderr.replace("\n", " ").strip()
        if "unstaged changes" in msg:
            print(" error:", "unstaged changes.")
        elif "uncommitted changes" in msg:
            print(" error:", "uncommitted changes.")
        else:
            try:
                repo.git.rebase("--abort")
            except exc.GitCommandError:
                pass
            print(" error:", msg if msg else "rebase conflict")
    else:
        print(" done.")

def _merge(repo, name):
    """Merge the branch *name* into the current HEAD of *repo*."""
    print(" merging...", end="")
    try:
        repo.git.merge(name)
    except exc.GitCommandError as err:
        msg = err.stderr.replace("\n", " ").strip()
        if "local changes" in msg and "would be overwritten" in msg:
            print(" error:", "uncommitted changes.")
        else:
            try:
                repo.git.merge("--abort")
            except exc.GitCommandError:
                pass
            print(" error:", msg if msg else "merge conflict")
    else:
        print(" done.")

def _update_branch(repo, branch, merge, rebase, stasher=None):
    """Update a single branch."""
    print(INDENT2, "Updating", branch, end="...")
    upstream = branch.tracking_branch()
    if not upstream:
        print(" skipped: no upstream is tracked.")
        return

    try:
        branch.commit, upstream.commit
    except ValueError:
        print(" skipped: branch contains no revisions.")
        return
    if _is_up_to_date(repo, branch, upstream):
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

    _fetch_remotes(remotes, verbose)

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
