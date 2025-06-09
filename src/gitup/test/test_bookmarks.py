# -*- coding: utf-8  -*-
#
# Copyright (C) 2011-2018 Ben Kurtovic <ben.kurtovic@gmail.com>
# Released under the terms of the MIT License. See LICENSE for details.

from __future__ import print_function, unicode_literals

from gitup import config

def test_empty_list(tmpdir, capsys):
    config_path = tmpdir / "config"
    config.list_bookmarks(config_path)
    captured = capsys.readouterr()
    assert captured.out == "You have no bookmarks to display.\n"
