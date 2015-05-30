# -*- coding: utf-8  -*-
#
# Copyright (C) 2011-2015 Ben Kurtovic <ben.kurtovic@gmail.com>
# See the LICENSE file for details.

from __future__ import print_function

import ConfigParser as configparser
import os

from colorama import Fore, Style

__all__ = ["get_bookmarks", "add_bookmarks", "delete_bookmarks",
           "list_bookmarks"]

YELLOW = Fore.YELLOW + Style.BRIGHT
RED = Fore.RED + Style.BRIGHT

INDENT1 = " " * 3

def _ensure_dirs(path):
    """Ensure the directories within the given pathname exist."""
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):  # Race condition, meh...
        os.makedirs(dirname)

def _get_config_path():
    """Return the path to the configuration file."""
    xdg_cfg = os.environ.get("XDG_CONFIG_HOME") or os.path.join("~", ".config")
    return os.path.join(os.path.expanduser(xdg_cfg), "gitup", "config.ini")

def _migrate_old_config_path():
    """Migrate the old config location (~/.gitup) to the new one."""
    old_path = os.path.expanduser(os.path.join("~", ".gitup"))
    if os.path.exists(old_path):
        new_path = _get_config_path()
        _ensure_dirs(new_path)
        os.rename(old_path, new_path)

def _load_config_file():
    """Read the config file and return a SafeConfigParser() object."""
    _migrate_old_config_path()
    config = configparser.SafeConfigParser()
    # Don't lowercase option names, because we are storing paths there:
    config.optionxform = str
    config.read(_get_config_path())
    return config

def _save_config_file(config):
    """Save config changes to the config file returned by _get_config_path."""
    _migrate_old_config_path()
    cfg_path = _get_config_path()
    _ensure_dirs(cfg_path)
    with open(cfg_path, "wb") as config_file:
        config.write(config_file)

def get_bookmarks():
    """Get a list of all bookmarks, or an empty list if there are none."""
    config = _load_config_file()
    try:
        return config.items("bookmarks")
    except configparser.NoSectionError:
        return []

def add_bookmarks(paths):
    """Add a list of paths as bookmarks to the config file."""
    config = _load_config_file()
    if not config.has_section("bookmarks"):
        config.add_section("bookmarks")

    added, exists = [], []
    for path in paths:
        path = os.path.abspath(path)
        if config.has_option("bookmarks", path):
            exists.append(path)
        else:
            path_name = os.path.split(path)[1]
            config.set("bookmarks", path, path_name)
            added.append(path)
    _save_config_file(config)

    if added:
        print(YELLOW + "Added bookmarks:")
        for path in added:
            print(INDENT1, path)
    if exists:
        print(RED + "Already bookmarked:")
        for path in exists:
            print(INDENT1, path)

def delete_bookmarks(paths):
    """Remove a list of paths from the bookmark config file."""
    config = _load_config_file()

    deleted, notmarked = [], []
    if config.has_section("bookmarks"):
        for path in paths:
            path = os.path.abspath(path)
            config_was_changed = config.remove_option("bookmarks", path)
            if config_was_changed:
                deleted.append(path)
            else:
                notmarked.append(path)
        _save_config_file(config)
    else:
        notmarked = [os.path.abspath(path) for path in paths]

    if deleted:
        print(YELLOW + "Deleted bookmarks:")
        for path in deleted:
            print(INDENT1, path)
    if notmarked:
        print(RED + "Not bookmarked:")
        for path in notmarked:
            print(INDENT1, path)

def list_bookmarks():
    """Print all of our current bookmarks."""
    bookmarks = get_bookmarks()
    if bookmarks:
        print(YELLOW + "Current bookmarks:")
        for bookmark_path, _ in bookmarks:
            print(INDENT1, bookmark_path)
    else:
        print("You have no bookmarks to display.")
