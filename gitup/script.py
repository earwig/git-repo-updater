# -*- coding: utf-8  -*-
#
# Copyright (C) 2011-2015 Ben Kurtovic <ben.kurtovic@gmail.com>
# Released under the terms of the MIT License. See LICENSE for details.

from __future__ import print_function

import argparse
import os

from colorama import init as color_init, Fore, Style

from . import __version__
from .config import (get_default_config_path, get_bookmarks, add_bookmarks,
                     delete_bookmarks, list_bookmarks)
from .update import update_bookmarks, update_directories

def main():
    """Parse arguments and then call the appropriate function(s)."""
    parser = argparse.ArgumentParser(
        description="Easily update multiple git repositories at once.",
        epilog="""
            Both relative and absolute paths are accepted by all arguments.
            Direct bug reports and feature requests to:
            https://github.com/earwig/git-repo-updater.""",
        add_help=False)

    group_u = parser.add_argument_group("updating repositories")
    group_b = parser.add_argument_group("bookmarking")
    group_m = parser.add_argument_group("miscellaneous")

    group_u.add_argument(
        'directories_to_update', nargs="*", metavar="path",
        help="""update all repositories in this directory (or the directory
                itself, if it is a repo)""")
    group_u.add_argument(
        '-u', '--update', action="store_true", help="""update all bookmarks
        (default behavior when called without arguments)""")
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
        help="add directory(s) as bookmarks")
    group_b.add_argument(
        '-d', '--delete', dest="bookmarks_to_del", nargs="+", metavar="path",
        help="delete bookmark(s) (leaves actual directories alone)")
    group_b.add_argument(
        '-l', '--list', dest="list_bookmarks", action="store_true",
        help="list current bookmarks")
    group_b.add_argument(
        '-b', '--bookmark-file', nargs="?", metavar="path",
        help="use a specific bookmark config file (default: {0})".format(
            get_default_config_path()))

    group_m.add_argument(
        '-h', '--help', action="help", help="show this help message and exit")
    group_m.add_argument(
        '-v', '--version', action="version",
        version="gitup " + __version__)

    # TODO: deprecated arguments, for removal in v1.0:
    parser.add_argument(
        '-m', '--merge', action="store_true", help=argparse.SUPPRESS)
    parser.add_argument(
        '-r', '--rebase', action="store_true", help=argparse.SUPPRESS)

    color_init(autoreset=True)
    args = parser.parse_args()
    update_args = args.current_only, args.fetch_only, args.prune

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
    if args.directories_to_update:
        update_directories(args.directories_to_update, update_args)
        acted = True
    if args.update or not acted:
        update_bookmarks(get_bookmarks(args.bookmark_file), update_args)

def run():
    """Thin wrapper for main() that catches KeyboardInterrupts."""
    try:
        main()
    except KeyboardInterrupt:
        print("Stopped by user.")
