# -*- coding: utf-8  -*-
#
# Copyright (C) 2011-2015 Ben Kurtovic <ben.kurtovic@gmail.com>
# Released under the terms of the MIT License. See LICENSE for details.

import sys

from setuptools import setup, find_packages

if sys.hexversion < 0x02070000:
    exit("Please upgrade to Python 2.7 or greater: <http://python.org/>.")

from gitup import __version__

with open('README.md') as fp:
    long_desc = fp.read()

setup(
    name = "gitup",
    packages = find_packages(),
    entry_points = {"console_scripts": ["gitup = gitup.script:run"]},
    install_requires = ["GitPython >= 1.0.1", "colorama >= 0.3.3"],
    version = __version__,
    author = "Ben Kurtovic",
    author_email = "ben.kurtovic@gmail.com",
    description = "Easily pull to multiple git repositories at once",
    long_description = long_desc,
    license = "MIT License",
    keywords = "git repository pull update",
    url = "http://github.com/earwig/git-repo-updater",
    classifiers = [
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: Software Development :: Version Control"
    ]
)
