# -*- coding: utf-8  -*-
#
# Copyright (C) 2011-2016 Ben Kurtovic <ben.kurtovic@gmail.com>
# Released under the terms of the MIT License. See LICENSE for details.

import os

try:
    from configparser import ConfigParser, NoSectionError
    PY3K = True
except ImportError:  # Python 2
    from ConfigParser import SafeConfigParser as ConfigParser, NoSectionError
    PY3K = False

__all__ = ["run_migrations"]

def _get_old_path():
    """Return the old default path to the configuration file."""
    xdg_cfg = os.environ.get("XDG_CONFIG_HOME") or os.path.join("~", ".config")
    return os.path.join(os.path.expanduser(xdg_cfg), "gitup", "config.ini")

def _migrate_old_path():
    """Migrate the old config location (~/.gitup) to the new one."""
    old_path = os.path.expanduser(os.path.join("~", ".gitup"))
    if not os.path.exists(old_path):
        return

    temp_path = _get_old_path()
    temp_dir = os.path.dirname(temp_path)
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    os.rename(old_path, temp_path)

def _migrate_old_format():
    """Migrate the old config file format (.INI) to our custom list format."""
    old_path = _get_old_path()
    if not os.path.exists(old_path):
        return

    config = ConfigParser(delimiters="=") if PY3K else ConfigParser()
    config.optionxform = lambda opt: opt
    config.read(old_path)

    try:
        bookmarks = [path for path, _ in config.items("bookmarks")]
    except NoSectionError:
        bookmarks = []
    if PY3K:
        bookmarks = [path.encode("utf8") for path in bookmarks]

    new_path = os.path.join(os.path.split(old_path)[0], "bookmarks")
    os.rename(old_path, new_path)

    with open(new_path, "wb") as handle:
        handle.write(b"\n".join(bookmarks))

def run_migrations():
    """Run any necessary migrations to ensure the config file is up-to-date."""
    _migrate_old_path()
    _migrate_old_format()
