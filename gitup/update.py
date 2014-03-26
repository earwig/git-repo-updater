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

def _update_repository(repo):
    """Update a single git repository by pulling from the remote."""
    print(INDENT1, BOLD + os.path.split(repo.working_dir)[1] + ":")

    try:
        # Check if there is anything to pull, but don't do it yet:
        dry_fetch = _exec_shell("git fetch --dry-run")
    except subprocess.CalledProcessError:
        print(INDENT2, RED + "Error:" + RESET, "cannot fetch;",
              "do you have a remote repository configured correctly?")
        return

    try:
        last_commit = _exec_shell("git log -n 1 --pretty=\"%ar\"")
    except subprocess.CalledProcessError:
        last_commit = "never"  # Couldn't get a log, so no commits

    if not dry_fetch:  # No new changes to pull
        print(INDENT2, BLUE + "No new changes." + RESET,
              "Last commit was {0}.".format(last_commit))

    else:  # Stuff has happened!
        print(INDENT2, "There are new changes upstream...")
        status = _exec_shell("git status")

        if status.endswith("nothing to commit, working directory clean"):
            print(INDENT2, GREEN + "Pulling new changes...")
            result = _exec_shell("git pull")
            if last_commit == "never":
                print(INDENT2, "The following changes have been made:")
            else:
                print(INDENT2, "The following changes have been made since",
                      last_commit + ":")
            print(result)

        else:
            print(INDENT2, RED + "Warning:" + RESET,
                  "you have uncommitted changes in this repository!")
            print(INDENT2, "Ignoring.")

def _update_subdirectories(path, long_name):
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
    for repo in sorted(repos):
        _update_repository(repo)

def _update_directory(path, is_bookmark=False):
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
        print(RED + "Error:" + RESET, long_name, "doesn't exist!")
    except exc.InvalidGitRepositoryError:
        if os.path.isdir(path):
            _update_subdirectories(path, long_name)
        else:
            print(RED + "Error:" + RESET, long_name, "isn't a repository!")
    else:
        long_name = (dir_type.capitalize() + ' "' + BOLD + repo.working_dir +
                     RESET + '"')
        print(long_name, "is a git repository:")
        _update_repository(repo)

def update_bookmarks(bookmarks):
    """Loop through and update all bookmarks."""
    if bookmarks:
        for path, name in bookmarks:
            _update_directory(path, is_bookmark=True)
    else:
        print("You don't have any bookmarks configured! Get help with 'gitup -h'.")

def update_directories(paths):
    """Update a list of directories supplied by command arguments."""
    for path in paths:
        _update_directory(os.path.abspath(path), is_bookmark=False)
