# -*- coding: utf-8  -*-
#
# Copyright (C) 2011-2018 Ben Kurtovic <ben.kurtovic@gmail.com>
# Released under the terms of the MIT License. See LICENSE for details.

from __future__ import print_function

from glob import glob
import os
import pipes
import re
import shlex

from colorama import Fore, Style
from git import RemoteReference as RemoteRef, Repo, exc
from git.util import RemoteProgress

__all__ = ["update_bookmarks", "update_directories", "run_command"]

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


def _fetch_remotes(remotes, prune):
    """Fetch a list of remotes, displaying progress info along the way."""
    def _get_name(ref):
        """Return the local name of a remote or tag reference."""
        return ref.remote_head if isinstance(ref, RemoteRef) else ref.name

    # TODO: missing branch deleted (via --prune):
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
            results = remote.fetch(progress=_ProgressMonitor(), prune=prune)
        except exc.GitCommandError as err:
            # We should have to do this ourselves, but GitPython doesn't give
            # us a sensible way to get the raw stderr...
            msg = re.sub(r"\s+", " ", err.stderr).strip()
            msg = re.sub(r"^stderr: *'(fatal: *)?", "", msg).strip("'")
            if not msg:
                command = " ".join(pipes.quote(arg) for arg in err.command)
                msg = "{0} failed with status {1}.".format(command, err.status)
            elif not msg.endswith("."):
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
        branch.commit
    except ValueError:
        print(YELLOW + "skipped:", "branch has no revisions.")
        return
    try:
        upstream.commit
    except ValueError:
        print(YELLOW + "skipped:", "upstream does not exist.")
        return

    try:
        base = repo.git.merge_base(branch.commit, upstream.commit)
    except exc.GitCommandError as err:
        print(YELLOW + "skipped:", "can't find merge base with upstream.")
        return

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

def _update_repository(repo, repo_name, args):
    """Update a single git repository by fetching remotes and rebasing/merging.

    The specific actions depend on the arguments given. We will fetch all
    remotes if *args.current_only* is ``False``, or only the remote tracked by
    the current branch if ``True``. If *args.fetch_only* is ``False``, we will
    also update all fast-forwardable branches that are tracking valid
    upstreams. If *args.prune* is ``True``, remote-tracking branches that no
    longer exist on their remote after fetching will be deleted.
    """
    print(INDENT1, BOLD + repo_name + ":")

    try:
        active = repo.active_branch
    except TypeError:  # Happens when HEAD is detached
        active = None
    if args.current_only:
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
    _fetch_remotes(remotes, args.prune)

    if not args.fetch_only:
        for branch in sorted(repo.heads, key=lambda b: b.name):
            _update_branch(repo, branch, branch == active)

def _run_command(repo, repo_name, args):
    """Run an arbitrary shell command on the given repository."""
    print(INDENT1, BOLD + repo_name + ":")

    cmd = shlex.split(args.command)
    try:
        out = repo.git.execute(
            cmd, with_extended_output=True, with_exceptions=False)
    except exc.GitCommandNotFound as err:
        print(INDENT2, ERROR, err)
        return

    for line in out[1].splitlines() + out[2].splitlines():
        print(INDENT2, line)

def _dispatch(base_path, callback, args):
    """Apply a callback function on each valid repo in the given path.

    Determine whether the directory is a git repo on its own, a directory of
    git repositories, a shell glob pattern, or something invalid. If the first,
    apply the callback on it; if the second or third, apply the callback on all
    repositories contained within; if the last, print an error.

    The given args are passed directly to the callback function after the repo.
    """
    def _collect(paths, max_depth):
        """Return all valid repo paths in the given paths, recursively."""
        if max_depth == 0:
            return []

        valid = []
        for path in paths:
            try:
                Repo(path)
                valid.append(path)
            except exc.InvalidGitRepositoryError:
                if not os.path.isdir(path):
                    continue
                children = [os.path.join(path, it) for it in os.listdir(path)]
                valid += _collect(children, max_depth - 1)
            except exc.NoSuchPathError:
                continue
        return valid

    def _get_basename(base, path):
        """Return a reasonable name for a repo path in the given base."""
        if path.startswith(base + os.path.sep):
            return path.split(base + os.path.sep, 1)[1]
        prefix = os.path.commonprefix([base, path])
        while not base.startswith(prefix + os.path.sep):
            old = prefix
            prefix = os.path.split(prefix)[0]
            if prefix == old:
                break  # Prevent infinite loop, but should be almost impossible
        return path.split(prefix + os.path.sep, 1)[1]

    base = os.path.expanduser(base_path)
    max_depth = args.max_depth
    if max_depth >= 0:
        max_depth += 1

    try:
        Repo(base)
        valid = [base]
    except exc.NoSuchPathError:
        paths = glob(base)
        if not paths:
            print(ERROR, BOLD + base, "doesn't exist!")
            return
        valid = _collect(paths, max_depth)
    except exc.InvalidGitRepositoryError:
        if not os.path.isdir(base) or args.max_depth == 0:
            print(ERROR, BOLD + base, "isn't a repository!")
            return
        valid = _collect([base], max_depth)

    base = os.path.abspath(base)
    suffix = "" if len(valid) == 1 else "s"
    print(BOLD + base, "({0} repo{1}):".format(len(valid), suffix))

    valid = [os.path.abspath(path) for path in valid]
    paths = [(_get_basename(base, path), path) for path in valid]
    for name, path in sorted(paths):
        callback(Repo(path), name, args)

def update_bookmarks(bookmarks, args):
    """Loop through and update all bookmarks."""
    if not bookmarks:
        print("You don't have any bookmarks configured! Get help with 'gitup -h'.")
        return

    for path in bookmarks:
        _dispatch(path, _update_repository, args)

def update_directories(paths, args):
    """Update a list of directories supplied by command arguments."""
    for path in paths:
        _dispatch(path, _update_repository, args)

def run_command(paths, args):
    """Run an arbitrary shell command on all repos."""
    for path in paths:
        _dispatch(path, _run_command, args)
