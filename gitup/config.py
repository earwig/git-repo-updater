# -*- coding: utf-8  -*-
#
# Copyright (C) 2011-2016 Ben Kurtovic <ben.kurtovic@gmail.com>
# Released under the terms of the MIT License. See LICENSE for details.

from __future__ import print_function

from glob import glob
import os

from colorama import Fore, Style

from .migrate import run_migrations

__all__ = ["get_default_config_path", "get_bookmarks", "add_bookmarks",
           "delete_bookmarks", "list_bookmarks", "clean_bookmarks"]

YELLOW = Fore.YELLOW + Style.BRIGHT
RED = Fore.RED + Style.BRIGHT

INDENT1 = " " * 3

def _ensure_dirs(path):
    """Ensure the directories within the given pathname exist."""
    dirname = os.path.dirname(path)
    if dirname and not os.path.exists(dirname):  # Race condition, meh...
        os.makedirs(dirname)

def _load_config_file(config_path=None):
    """Read the config file and return a list of bookmarks."""
    run_migrations()
    cfg_path = config_path or get_default_config_path()

    try:
        with open(cfg_path, "rb") as config_file:
            paths = config_file.read().split(b"\n")
    except IOError:
        return []
    paths = [path.decode("utf8").strip() for path in paths]
    return [path for path in paths if path]

def _save_config_file(bookmarks, config_path=None):
    """Save the bookmarks list to the given config file."""
    run_migrations()
    cfg_path = config_path or get_default_config_path()
    _ensure_dirs(cfg_path)

    dump = b"\n".join(path.encode("utf8") for path in bookmarks)
    with open(cfg_path, "wb") as config_file:
        config_file.write(dump)

def _normalize_path(path):
    """Normalize the given path."""
    if path.startswith("~"):
        return os.path.normcase(os.path.normpath(path))
    return os.path.normcase(os.path.abspath(path))

def get_default_config_path():
    """Return the default path to the configuration file."""
    xdg_cfg = os.environ.get("XDG_CONFIG_HOME") or os.path.join("~", ".config")
    return os.path.join(os.path.expanduser(xdg_cfg), "gitup", "bookmarks")

def get_bookmarks(config_path=None):
    """Get a list of all bookmarks, or an empty list if there are none."""
    return _load_config_file(config_path)

def add_bookmarks(paths, config_path=None):
    """Add a list of paths as bookmarks to the config file."""
    config = _load_config_file(config_path)
    paths = [_normalize_path(path) for path in paths]

    added, exists = [], []
    for path in paths:
        if path in config:
            exists.append(path)
        else:
            config.append(path)
            added.append(path)
    _save_config_file(config, config_path)

    if added:
        print(YELLOW + "Added bookmarks:")
        for path in added:
            print(INDENT1, path)
    if exists:
        print(RED + "Already bookmarked:")
        for path in exists:
            print(INDENT1, path)

def delete_bookmarks(paths, config_path=None):
    """Remove a list of paths from the bookmark config file."""
    config = _load_config_file(config_path)
    paths = [_normalize_path(path) for path in paths]

    deleted, notmarked = [], []
    if config:
        for path in paths:
            if path in config:
                config.remove(path)
                deleted.append(path)
            else:
                notmarked.append(path)
        _save_config_file(config, config_path)
    else:
        notmarked = paths

    if deleted:
        print(YELLOW + "Deleted bookmarks:")
        for path in deleted:
            print(INDENT1, path)
    if notmarked:
        print(RED + "Not bookmarked:")
        for path in notmarked:
            print(INDENT1, path)

def list_bookmarks(config_path=None):
    """Print all of our current bookmarks."""
    bookmarks = _load_config_file(config_path)
    if bookmarks:
        print(YELLOW + "Current bookmarks:")
        for bookmark_path in bookmarks:
            print(INDENT1, bookmark_path)
    else:
        print("You have no bookmarks to display.")

def clean_bookmarks(config_path=None):
    """Delete any bookmarks that don't exist."""
    bookmarks = _load_config_file(config_path)
    if not bookmarks:
        print("You have no bookmarks to clean up.")
        return

    delete = [path for path in bookmarks
              if not (os.path.isdir(path) or glob(os.path.expanduser(path)))]
    if not delete:
        print("All of your bookmarks are valid.")
        return

    bookmarks = [path for path in bookmarks if path not in delete]
    _save_config_file(bookmarks, config_path)

    print(YELLOW + "Deleted bookmarks:")
    for path in delete:
        print(INDENT1, path)
