# -*- coding: utf-8  -*-
#
# Copyright (C) 2011-2014 Ben Kurtovic <ben.kurtovic@gmail.com>
# See the LICENSE file for details.

from __future__ import print_function

import argparse

from . import __version__, __email__
from .config import (get_bookmarks, add_bookmarks, delete_bookmarks,
                     list_bookmarks)
from .output import out, bold
from .update import update_bookmarks, update_directories

def main():
    """Parse arguments and then call the appropriate function(s)."""
    parser = argparse.ArgumentParser(
        description="""Easily pull to multiple git repositories at once.""",
        epilog="""
            Both relative and absolute paths are accepted by all arguments.
            Questions? Comments? Email the author at {0}.""".format(__email__),
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
    group_b.add_argument(
        '-a', '--add', dest="bookmarks_to_add", nargs="+", metavar="path",
        help="add directory(s) as bookmarks")
    group_b.add_argument(
        '-d', '--delete', dest="bookmarks_to_del", nargs="+", metavar="path",
        help="delete bookmark(s) (leaves actual directories alone)")
    group_b.add_argument(
        '-l', '--list', dest="list_bookmarks", action="store_true",
        help="list current bookmarks")
    group_m.add_argument(
        '-h', '--help', action="help", help="show this help message and exit")
    group_m.add_argument(
        '-v', '--version', action="version",
        version="gitup version " + __version__)

    args = parser.parse_args()
    print(bold("gitup") + ": the git-repo-updater")

    if args.bookmarks_to_add:
        add_bookmarks(args.bookmarks_to_add)
    if args.bookmarks_to_del:
        delete_bookmarks(args.bookmarks_to_del)
    if args.list_bookmarks:
        list_bookmarks()
    if args.directories_to_update:
        update_directories(args.directories_to_update)
    if args.update:
        update_bookmarks(get_bookmarks())

    # If they did not tell us to do anything, automatically update bookmarks:
    if not any(vars(args).values()):
        update_bookmarks(get_bookmarks())

def run():
    """Thin wrapper for main() that catches KeyboardInterrupts."""
    try:
        main()
    except KeyboardInterrupt:
        out(0, "Stopped by user.")
