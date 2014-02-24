# -*- coding: utf-8  -*-
#
# Copyright (C) 2011-2014 Ben Kurtovic <ben.kurtovic@gmail.com>
# See the LICENSE file for details.

import re

__all__ = ["out", "bold", "red", "green", "yellow", "blue"]

# Text formatting functions:
bold = lambda t: _style_text(t, "bold")
red = lambda t: _style_text(t, "red")
green = lambda t: _style_text(t, "green")
yellow = lambda t: _style_text(t, "yellow")
blue = lambda t: _style_text(t, "blue")

def _style_text(text, effect):
    """Give a text string a certain effect, such as boldness, or a color."""
    ansi = {  # ANSI escape codes to make terminal output fancy
        "reset": "\x1b[0m",
        "bold": "\x1b[1m",
        "red": "\x1b[1m\x1b[31m",
        "green": "\x1b[1m\x1b[32m",
        "yellow": "\x1b[1m\x1b[33m",
        "blue": "\x1b[1m\x1b[34m",
    }

    try:  # Pad text with effect, unless effect does not exist
        return ansi[effect] + text + ansi["reset"]
    except KeyError:
        return text

def out(indent, msg):
    """Print a message at a given indentation level."""
    width = 4  # Amount to indent at each level
    if indent == 0:
        spacing = "\n"
    else:
        spacing = " " * width * indent
    msg = re.sub(r"\s+", " ", msg)  # Collapse multiple spaces into one
    print(spacing + msg)
