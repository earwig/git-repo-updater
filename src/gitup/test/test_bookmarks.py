# -*- coding: utf-8  -*-
#
# Copyright (C) 2011-2018 Ben Kurtovic <ben.kurtovic@gmail.com>
# Released under the terms of the MIT License. See LICENSE for details.

import os

from gitup import config


def test_empty_list(tmpdir, capsys):
    config_path = tmpdir / "config"
    config.list_bookmarks(config_path)
    captured = capsys.readouterr()
    assert captured.out == "You have no bookmarks to display.\n"


def test_clean_bookmarks_preserves_comments(tmpdir, capsys):
    """Comments in the bookmarks file must survive a cleanup."""
    repo_dir = tmpdir / "repo"
    os.makedirs(os.fspath(repo_dir))
    missing_dir = tmpdir / "missing"

    config_path = tmpdir / "config"
    comment = "# a comment line"
    lines = [comment, os.fspath(repo_dir), os.fspath(missing_dir)]
    with open(os.fspath(config_path), "wb") as handle:
        handle.write("\n".join(lines).encode("utf8"))

    config.clean_bookmarks(config_path)

    remaining = config_path.read_binary().decode("utf8").split("\n")
    assert comment in remaining
    assert os.fspath(repo_dir) in remaining
    assert os.fspath(missing_dir) not in remaining

    captured = capsys.readouterr()
    assert "Deleted bookmarks:" in captured.out
    assert os.fspath(missing_dir) in captured.out
