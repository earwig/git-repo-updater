# -*- coding: utf-8  -*-
#
# Copyright (C) 2011-2014 Ben Kurtovic <ben.kurtovic@gmail.com>
# See the LICENSE file for details.

import ConfigParser as configparser
import os

from .output import out, bold, yellow

__all__ = ["get_bookmarks", "add_bookmarks", "delete_bookmarks",
           "list_bookmarks"]

_config_filename = os.path.join(os.path.expanduser("~"), ".gitup")

def _load_config_file():
    """Read the config file and return a SafeConfigParser() object."""
    config = configparser.SafeConfigParser()
    # Don't lowercase option names, because we are storing paths there:
    config.optionxform = str
    config.read(_config_filename)
    return config

def _save_config_file(config):
    """Save config changes to the config file specified by _config_filename."""
    with open(_config_filename, "wb") as config_file:
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

    out(0, yellow("Added bookmarks:"))

    for path in paths:
        path = os.path.abspath(path)  # Convert relative to absolute path
        if config.has_option("bookmarks", path):
            out(1, "'{0}' is already bookmarked.".format(path))
        else:
            path_name = os.path.split(path)[1]
            config.set("bookmarks", path, path_name)
            out(1, bold(path))

    _save_config_file(config)

def delete_bookmarks(paths):
    """Remove a list of paths from the bookmark config file."""
    config = _load_config_file()

    if config.has_section("bookmarks"):
        out(0, yellow("Deleted bookmarks:"))
        for path in paths:
            path = os.path.abspath(path)  # Convert relative to absolute path
            config_was_changed = config.remove_option("bookmarks", path)
            if config_was_changed:
                out(1, bold(path))
            else:
                out(1, "'{0}' is not bookmarked.".format(path))
        _save_config_file(config)

    else:
        out(0, "There are no bookmarks to delete!")

def list_bookmarks():
    """Print all of our current bookmarks."""
    bookmarks = get_bookmarks()
    if bookmarks:
        out(0, yellow("Current bookmarks:"))
        for bookmark_path, bookmark_name in bookmarks:
            out(1, bookmark_path)
    else:
        out(0, "You have no bookmarks to display.")
