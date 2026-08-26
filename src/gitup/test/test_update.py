# -*- coding: utf-8  -*-
#
# Copyright (C) 2011-2026 Ben Kurtovic <ben.kurtovic@gmail.com>
# Released under the terms of the MIT License. See LICENSE for details.

import os
import re
import subprocess
from types import SimpleNamespace

import pytest
from git import Repo
from git.exc import GitCommandError

from gitup.update import _update_branch, _update_repository

ANSI = re.compile(r"\x1b\[[0-9;]*m")

GIT = [
    "git",
    "-c",
    "user.name=gitup-test",
    "-c",
    "user.email=gitup-test@example.com",
    "-c",
    "commit.gpgsign=false",
    "-c",
    "init.defaultBranch=main",
]


def _plain(text):
    return ANSI.sub("", text)


def _git(cwd, *args):
    try:
        subprocess.check_output(
            GIT + list(args),
            cwd=os.fspath(cwd),
            stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as err:
        output = err.output.decode("utf8", errors="replace") if err.output else ""
        raise AssertionError(
            "git {0} failed:\n{1}".format(" ".join(args), output)
        ) from err


def _write(path, contents):
    path.write_text(contents, encoding="utf8")


def _fetch_args(**overrides):
    args = SimpleNamespace(current_only=False, fetch_only=False, prune=False)
    for key, value in overrides.items():
        setattr(args, key, value)
    return args


@pytest.fixture
def tracking_repos(tmp_path):
    """A clone with a slash-named tracking branch checked out in a worktree.

    The worktree branch is behind ``origin`` after setup; ``main`` stays
    checked out in the clone.
    """
    origin = tmp_path / "origin.git"
    _git(tmp_path, "init", "--bare", "-b", "main", os.fspath(origin))

    clone = tmp_path / "clone"
    _git(tmp_path, "clone", os.fspath(origin), os.fspath(clone))
    _write(clone / "README", "base\n")
    _git(clone, "add", "README")
    _git(clone, "commit", "-m", "init")
    _git(clone, "push", "-u", "origin", "main")

    branch = "wip/382-eliminate-tautological-expects"
    _git(clone, "branch", branch)
    _git(clone, "push", "-u", "origin", branch)

    worktree = tmp_path / "wt-382"
    _git(clone, "worktree", "add", os.fspath(worktree), branch)

    pusher = tmp_path / "pusher"
    _git(tmp_path, "clone", "-b", branch, os.fspath(origin), os.fspath(pusher))
    _write(pusher / "README", "upstream\n")
    _git(pusher, "add", "README")
    _git(pusher, "commit", "-m", "advance feature")
    _git(pusher, "push")

    _git(clone, "fetch", "origin")

    extra = "done/386-presentation-size"
    _git(clone, "branch", extra, "main")
    _git(clone, "push", "-u", "origin", extra)
    _write(pusher / "EXTRA", "extra\n")
    _git(pusher, "checkout", "-B", extra, "origin/main")
    _git(pusher, "add", "EXTRA")
    _git(pusher, "commit", "-m", "advance extra")
    _git(pusher, "push", "-u", "origin", extra)
    _git(clone, "fetch", "origin")

    return SimpleNamespace(
        origin=origin,
        clone=clone,
        worktree=worktree,
        branch=branch,
        extra=extra,
    )


def _head(path):
    return Repo(os.fspath(path)).head.commit.hexsha


def test_worktree_branch_force_update_does_not_raise(tracking_repos):
    repo = Repo(os.fspath(tracking_repos.clone))
    branch = repo.heads[tracking_repos.branch]

    try:
        _update_branch(repo, branch, is_active=False)
    except GitCommandError as err:
        pytest.fail("updating a worktree branch raised GitCommandError: {0}".format(err))


def test_worktree_branch_is_fast_forwarded_in_its_worktree(tracking_repos, capsys):
    repo = Repo(os.fspath(tracking_repos.clone))
    branch = repo.heads[tracking_repos.branch]
    expected = repo.remotes.origin.refs[tracking_repos.branch].commit.hexsha

    _update_branch(repo, branch, is_active=False)
    out = _plain(capsys.readouterr().out)

    assert "done" in out
    assert _head(tracking_repos.worktree) == expected
    assert repo.heads[tracking_repos.branch].commit.hexsha == expected


def test_dirty_worktree_is_skipped_not_crashed(tracking_repos, capsys):
    repo = Repo(os.fspath(tracking_repos.clone))
    branch = repo.heads[tracking_repos.branch]
    before = _head(tracking_repos.worktree)
    _write(tracking_repos.worktree / "README", "local dirty\n")

    _update_branch(repo, branch, is_active=False)
    out = _plain(capsys.readouterr().out)

    assert "skipped" in out
    assert "uncommitted changes" in out
    assert _head(tracking_repos.worktree) == before


def test_later_branches_still_update_when_a_worktree_branch_needs_ff(
    tracking_repos, capsys
):
    repo = Repo(os.fspath(tracking_repos.clone))
    expected_extra = repo.remotes.origin.refs[tracking_repos.extra].commit.hexsha
    expected_wt = repo.remotes.origin.refs[tracking_repos.branch].commit.hexsha

    _update_repository(repo, "clone", _fetch_args())
    out = _plain(capsys.readouterr().out)

    assert "Error" not in out or "no remotes" not in out
    assert repo.heads[tracking_repos.extra].commit.hexsha == expected_extra
    assert _head(tracking_repos.worktree) == expected_wt
