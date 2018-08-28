# -*- coding: utf-8  -*-
#
# Copyright (C) 2011-2018 Ben Kurtovic <ben.kurtovic@gmail.com>
# Released under the terms of the MIT License. See LICENSE for details.

from __future__ import print_function

import argparse
import os
import platform
import sys

from colorama import init as color_init, Fore, Style

from . import __version__
from .config import (get_default_config_path, get_bookmarks, add_bookmarks,
                     delete_bookmarks, list_bookmarks, clean_bookmarks)
from .update import update_bookmarks, update_directories, run_command

def _decode(path):
    """Decode the given string using the system's filesystem encoding."""
    if sys.version_info.major > 2:
        return path
    return path.decode(sys.getfilesystemencoding())

def main():
    """Parse arguments and then call the appropriate function(s)."""
    parser = argparse.ArgumentParser(
        description="Easily update multiple git repositories at once.",
        epilog="""
            Both relative and absolute paths are accepted by all arguments.
            Direct bug reports and feature requests to
            https://github.com/earwig/git-repo-updater.""",
        add_help=False)

    group_u = parser.add_argument_group("updating repositories")
    group_b = parser.add_argument_group("bookmarking")
    group_a = parser.add_argument_group("advanced")
    group_m = parser.add_argument_group("miscellaneous")

    group_u.add_argument(
        'directories_to_update', nargs="*", metavar="path", type=_decode,
        help="""update this repository, or all repositories it contains
        (if not a repo directly)""")
    group_u.add_argument(
        '-u', '--update', action="store_true", help="""update all bookmarks
        (default behavior when called without arguments)""")
    group_u.add_argument(
        '-t', '--depth', dest="max_depth", metavar="n", type=int, default=3,
        help="""max recursion depth when searching for repos in subdirectories
        (default: 3; use 0 for no recursion, or -1 for unlimited)""")
    group_u.add_argument(
        '-c', '--current-only', action="store_true", help="""only fetch the
        remote tracked by the current branch instead of all remotes""")
    group_u.add_argument(
        '-f', '--fetch-only', action="store_true",
        help="only fetch remotes, don't try to fast-forward any branches")
    group_u.add_argument(
        '-p', '--prune', action="store_true", help="""after fetching, delete
        remote-tracking branches that no longer exist on their remote""")

    group_b.add_argument(
        '-a', '--add', dest="bookmarks_to_add", nargs="+", metavar="path",
        type=_decode, help="add directory(s) as bookmarks")
    group_b.add_argument(
        '-d', '--delete', dest="bookmarks_to_del", nargs="+", metavar="path",
        type=_decode,
        help="delete bookmark(s) (leaves actual directories alone)")
    group_b.add_argument(
        '-l', '--list', dest="list_bookmarks", action="store_true",
        help="list current bookmarks")
    group_b.add_argument(
        '-n', '--clean', '--cleanup', dest="clean_bookmarks",
        action="store_true", help="delete any bookmarks that don't exist")
    group_b.add_argument(
        '-b', '--bookmark-file', nargs="?", metavar="path", type=_decode,
        help="use a specific bookmark config file (default: {0})".format(
            get_default_config_path()))

    group_a.add_argument(
        '-e', '--exec', '--batch', dest="command", metavar="command",
        help="run a shell command on all repos")

    group_m.add_argument(
        '-h', '--help', action="help", help="show this help message and exit")
    group_m.add_argument(
        '-v', '--version', action="version",
        version="gitup {0} (Python {1})".format(
            __version__, platform.python_version()))

    # TODO: deprecated arguments, for removal in v1.0:
    parser.add_argument(
        '-m', '--merge', action="store_true", help=argparse.SUPPRESS)
    parser.add_argument(
        '-r', '--rebase', action="store_true", help=argparse.SUPPRESS)

    color_init(autoreset=True)
    args = parser.parse_args()

    print(Style.BRIGHT + "gitup" + Style.RESET_ALL + ": the git-repo-updater")
    print()

    # TODO: remove in v1.0
    if args.merge or args.rebase:
        print(Style.BRIGHT + Fore.YELLOW + "Warning:", "--merge and --rebase "
              "are deprecated. Branches are only updated if they\ntrack an "
              "upstream branch and can be safely fast-forwarded. Use "
              "--fetch-only to\navoid updating any branches.\n")

    if args.bookmark_file:
        args.bookmark_file = os.path.expanduser(args.bookmark_file)

    acted = False
    if args.bookmarks_to_add:
        add_bookmarks(args.bookmarks_to_add, args.bookmark_file)
        acted = True
    if args.bookmarks_to_del:
        delete_bookmarks(args.bookmarks_to_del, args.bookmark_file)
        acted = True
    if args.list_bookmarks:
        list_bookmarks(args.bookmark_file)
        acted = True
    if args.clean_bookmarks:
        clean_bookmarks(args.bookmark_file)
        acted = True

    if args.command:
        if args.directories_to_update:
            run_command(args.directories_to_update, args)
        if args.update or not args.directories_to_update:
            run_command(get_bookmarks(args.bookmark_file), args)
    else:
        if args.directories_to_update:
            update_directories(args.directories_to_update, args)
            acted = True
        if args.update or not acted:
            update_bookmarks(get_bookmarks(args.bookmark_file), args)

def run():
    """Thin wrapper for main() that catches KeyboardInterrupts."""
    try:
        main()
    except KeyboardInterrupt:
        print("Stopped by user.")
