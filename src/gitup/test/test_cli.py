# -*- coding: utf-8  -*-
#
# Copyright (C) 2011-2018 Ben Kurtovic <ben.kurtovic@gmail.com>
# Released under the terms of the MIT License. See LICENSE for details.

import platform
import subprocess
import sys

from gitup import __version__


def run_cli(*args):
    cmd = [sys.executable, "-m", "gitup"] + list(args)
    output = subprocess.check_output(cmd)
    return output.strip().decode("utf8")


def test_cli_version():
    """make sure we're using the right version of gitup"""
    output = run_cli("-v")
    expected = "gitup {} (Python {})".format(__version__, platform.python_version())
    assert output == expected


def test_cli_rejects_depth_below_minus_one():
    """--depth values below -1 were silently treated as unlimited."""
    cmd = [sys.executable, "-m", "gitup", "--depth", "-2"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 2
    assert "--depth must be -1 (unlimited) or greater" in proc.stderr
