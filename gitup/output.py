# -*- coding: utf-8  -*-
#
# Copyright (C) 2011-2014 Ben Kurtovic <ben.kurtovic@gmail.com>
# See the LICENSE file for details.

import re

__all__ = ["out", "bold", "red", "green", "yellow", "blue"]

# Text formatting functions:
bold = lambda t: "\x1b[1m" + t + "\x1b[0m"
red = lambda t: "\x1b[1m\x1b[31m" + t + "\x1b[0m"
green = lambda t: "\x1b[1m\x1b[32m" + t + "\x1b[0m"
yellow = lambda t: "\x1b[1m\x1b[33m" + t + "\x1b[0m"
blue = lambda t: "\x1b[1m\x1b[34m" + t + "\x1b[0m"

def out(indent, msg):
    """Print a message at a given indentation level."""
    width = 4  # Amount to indent at each level
    if indent == 0:
        spacing = "\n"
    else:
        spacing = " " * width * indent
    msg = re.sub(r"\s+", " ", msg)  # Collapse multiple spaces into one
    print(spacing + msg)
