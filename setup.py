# -*- coding: utf-8  -*-
#
# Copyright (C) 2011-2018 Ben Kurtovic <ben.kurtovic@gmail.com>
# Released under the terms of the MIT License. See LICENSE for details.

import sys

from setuptools import setup, find_packages

from gitup import __version__

with open('README.md') as fp:
    long_desc = fp.read()

setup(
    name = "gitup",
    packages = find_packages(),
    entry_points = {"console_scripts": ["gitup = gitup.cli:run"]},
    install_requires = ["GitPython >= 2.1.8", "colorama >= 0.3.9"],
    version = __version__,
    author = "Ben Kurtovic",
    author_email = "ben.kurtovic@gmail.com",
    description = "Easily update multiple git repositories at once",
    long_description = long_desc,
    long_description_content_type = "text/markdown",
    license = "MIT License",
    keywords = "git repository pull update",
    url = "https://github.com/earwig/git-repo-updater",
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Version Control :: Git"
    ]
)
