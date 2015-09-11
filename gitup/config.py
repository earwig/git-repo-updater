# -*- coding: utf-8  -*-
#
# Copyright (C) 2011-2015 Ben Kurtovic <ben.kurtovic@gmail.com>
# Released under the terms of the MIT License. See LICENSE for details.

from __future__ import print_function

import os

try:
    import configparser
except ImportError:  # Python 2
    import ConfigParser as configparser

from colorama import Fore, Style

__all__ = ["get_default_config_path", "get_bookmarks", "add_bookmarks",
           "delete_bookmarks", "list_bookmarks"]

YELLOW = Fore.YELLOW + Style.BRIGHT
RED = Fore.RED + Style.BRIGHT

INDENT1 = " " * 3

def _ensure_dirs(path):
    """Ensure the directories within the given pathname exist."""
    dirname = os.path.dirname(path)
    if dirname and not os.path.exists(dirname):  # Race condition, meh...
        os.makedirs(dirname)

def _migrate_old_config_path():
    """Migrate the old config location (~/.gitup) to the new one."""
    old_path = os.path.expanduser(os.path.join("~", ".gitup"))
    if os.path.exists(old_path):
        new_path = get_default_config_path()
        _ensure_dirs(new_path)
        os.rename(old_path, new_path)

def _load_config_file(config_path=None):
    """Read the config file and return a SafeConfigParser() object."""
    _migrate_old_config_path()
    config = configparser.SafeConfigParser()
    # Don't lowercase option names, because we are storing paths there:
    config.optionxform = lambda opt: opt
    config.read(config_path or get_default_config_path())
    return config

def _save_config_file(config, config_path=None):
    """Save config changes to the given config file."""
    _migrate_old_config_path()
    cfg_path = config_path or get_default_config_path()
    _ensure_dirs(cfg_path)
    with open(cfg_path, "w") as config_file:
        config.write(config_file)

def get_default_config_path():
    """Return the default path to the configuration file."""
    xdg_cfg = os.environ.get("XDG_CONFIG_HOME") or os.path.join("~", ".config")
    return os.path.join(os.path.expanduser(xdg_cfg), "gitup", "config.ini")

def get_bookmarks(config_path=None):
    """Get a list of all bookmarks, or an empty list if there are none."""
    config = _load_config_file(config_path)
    try:
        return [path for path, _ in config.items("bookmarks")]
    except configparser.NoSectionError:
        return []

def add_bookmarks(paths, config_path=None):
    """Add a list of paths as bookmarks to the config file."""
    config = _load_config_file(config_path)
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

    deleted, notmarked = [], []
    if config.has_section("bookmarks"):
        for path in paths:
            path = os.path.abspath(path)
            config_was_changed = config.remove_option("bookmarks", path)
            if config_was_changed:
                deleted.append(path)
            else:
                notmarked.append(path)
        _save_config_file(config, config_path)
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

def list_bookmarks(config_path=None):
    """Print all of our current bookmarks."""
    bookmarks = get_bookmarks(config_path=config_path)
    if bookmarks:
        print(YELLOW + "Current bookmarks:")
        for bookmark_path in bookmarks:
            print(INDENT1, bookmark_path)
    else:
        print("You have no bookmarks to display.")
