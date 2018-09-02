# -*- coding: utf-8  -*-
#
# Copyright (C) 2011-2018 Ben Kurtovic <ben.kurtovic@gmail.com>
# Released under the terms of the MIT License. See LICENSE for details.

def run_tests(args=None):
    import pytest
    if args is None:
        args = ["-v", "-rxw"]
    return pytest.main(args)
