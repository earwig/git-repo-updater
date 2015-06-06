# -*- coding: utf-8  -*-
#
# Copyright (C) 2011-2015 Ben Kurtovic <ben.kurtovic@gmail.com>
# Released under the terms of the MIT License. See LICENSE for details.

from __future__ import print_function

import os

from colorama import Fore, Style
from git import RemoteReference as RemoteRef, Repo, exc
from git.util import RemoteProgress

__all__ = ["update_bookmarks", "update_directories"]

BOLD = Style.BRIGHT
BLUE = Fore.BLUE + BOLD
GREEN = Fore.GREEN + BOLD
RED = Fore.RED + BOLD
YELLOW = Fore.YELLOW + BOLD
RESET = Style.RESET_ALL

INDENT1 = " " * 3
INDENT2 = " " * 7
ERROR = RED + "Error:" + RESET

class _ProgressMonitor(RemoteProgress):
    """Displays relevant output during the fetching process."""

    def __init__(self):
        super(_ProgressMonitor, self).__init__()
        self._started = False

    def update(self, op_code, cur_count, max_count=None, message=''):
        """Called whenever progress changes. Overrides default behavior."""
        if op_code & (self.COMPRESSING | self.RECEIVING):
            cur_count = str(int(cur_count))
            if max_count:
                max_count = str(int(max_count))
            if op_code & self.BEGIN:
                print("\b, " if self._started else " (", end="")
                if not self._started:
                    self._started = True
            if op_code & self.END:
                end = ")"
            elif max_count:
                end = "\b" * (1 + len(cur_count) + len(max_count))
            else:
                end = "\b" * len(cur_count)
            if max_count:
                print("{0}/{1}".format(cur_count, max_count), end=end)
            else:
                print(str(cur_count), end=end)


def _fetch_remotes(remotes):
    """Fetch a list of remotes, displaying progress info along the way."""
    def _get_name(ref):
        """Return the local name of a remote or tag reference."""
        return ref.remote_head if isinstance(ref, RemoteRef) else ref.name

    info = [("NEW_HEAD", "new branch", "new branches"),
            ("NEW_TAG", "new tag", "new tags"),
            ("FAST_FORWARD", "branch update", "branch updates")]
    up_to_date = BLUE + "up to date" + RESET

    for remote in remotes:
        print(INDENT2, "Fetching", BOLD + remote.name, end="")

        if not remote.config_reader.has_option("fetch"):
            print(":", YELLOW + "skipped:", "no configured refspec.")
            continue

        try:
            results = remote.fetch(progress=_ProgressMonitor())
        except exc.GitCommandError as err:
            msg = err.command[0].replace("Error when fetching: ", "")
            if not msg.endswith("."):
                msg += "."
            print(":", RED + "error:", msg)
            return
        except AssertionError:  # Seems to be the result of a bug in GitPython
            # This happens when git initiates an auto-gc during fetch:
            print(":", RED + "error:", "something went wrong in GitPython,",
                  "but the fetch might have been successful.")
            return
        rlist = []
        for attr, singular, plural in info:
            names = [_get_name(res.ref)
                     for res in results if res.flags & getattr(res, attr)]
            if names:
                desc = singular if len(names) == 1 else plural
                colored = GREEN + desc + RESET
                rlist.append("{0} ({1})".format(colored, ", ".join(names)))
        print(":", (", ".join(rlist) if rlist else up_to_date) + ".")

def _update_branch(repo, branch, is_active=False):
    """Update a single branch."""
    print(INDENT2, "Updating", BOLD + branch.name, end=": ")
    upstream = branch.tracking_branch()
    if not upstream:
        print(YELLOW + "skipped:", "no upstream is tracked.")
        return

    try:
        branch.commit, upstream.commit
    except ValueError:
        print(YELLOW + "skipped:", "branch has no revisions.")
        return

    base = repo.git.merge_base(branch.commit, upstream.commit)
    if repo.commit(base) == upstream.commit:
        print(BLUE + "up to date", end=".\n")
        return

    if is_active:
        try:
            repo.git.merge(upstream.name, ff_only=True)
            print(GREEN + "done", end=".\n")
        except exc.GitCommandError as err:
            msg = err.stderr
            if "local changes" in msg and "would be overwritten" in msg:
                print(YELLOW + "skipped:", "uncommitted changes.")
            else:
                print(YELLOW + "skipped:", "not possible to fast-forward.")
    else:
        status = repo.git.merge_base(
            branch.commit, upstream.commit, is_ancestor=True,
            with_extended_output=True, with_exceptions=False)[0]
        if status != 0:
            print(YELLOW + "skipped:", "not possible to fast-forward.")
        else:
            repo.git.branch(branch.name, upstream.name, force=True)
            print(GREEN + "done", end=".\n")

def _update_repository(repo, current_only=False, fetch_only=False):
    """Update a single git repository by fetching remotes and rebasing/merging.

    The specific actions depend on the arguments given. We will fetch all
    remotes if *current_only* is ``False``, or only the remote tracked by the
    current branch if ``True``. If *fetch_only* is ``False``, we will also
    update all fast-forwardable branches that are tracking valid upstreams.
    """
    print(INDENT1, BOLD + os.path.split(repo.working_dir)[1] + ":")

    try:
        active = repo.active_branch
    except TypeError:  # Happens when HEAD is detached
        active = None
    if current_only:
        if not active:
            print(INDENT2, ERROR,
                  "--current-only doesn't make sense with a detached HEAD.")
            return
        ref = active.tracking_branch()
        if not ref:
            print(INDENT2, ERROR, "no remote tracked by current branch.")
            return
        remotes = [repo.remotes[ref.remote_name]]
    else:
        remotes = repo.remotes

    if not remotes:
        print(INDENT2, ERROR, "no remotes configured to fetch.")
        return
    _fetch_remotes(remotes)

    if not fetch_only:
        for branch in sorted(repo.heads, key=lambda b: b.name):
            _update_branch(repo, branch, branch == active)

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
