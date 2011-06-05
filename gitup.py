#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
gitup: the git repository updater
"""

import argparse
import ConfigParser as configparser
import os
import re
import shlex
import subprocess

__author__ = "Ben Kurtovic"
__copyright__ = "Copyright (c) 2011 by Ben Kurtovic"
__license__ = "MIT License"
__version__ = "0.1"
__email__ = "ben.kurtovic@verizon.net"

config_filename = os.path.join(os.path.expanduser("~"), ".gitup")

ansi = { # ANSI escape codes to make terminal output colorful
    "reset": "\x1b[0m",
    "bold": "\x1b[1m",
    "red": "\x1b[1m\x1b[31m",
    "green": "\x1b[1m\x1b[32m",
    "yellow": "\x1b[1m\x1b[33m",
    "blue": "\x1b[1m\x1b[34m",
}

def out(indent, msg):
    """Print a message at a given indentation level."""
    width = 4 # amount to indent at each level
    if indent == 0:
        spacing = "\n"
    else:
        spacing = " " * width * indent
    msg = re.sub("\s+", " ", msg) # collapse multiple spaces into one
    print spacing + msg

def exec_shell(command):
    """Execute a shell command and get the output."""
    command = shlex.split(command)
    result = subprocess.check_output(command, stderr=subprocess.STDOUT)
    if result:
        result = result[:-1] # strip newline if command returned anything
    return result

def directory_is_git_repo(directory_path):
    """Check if a directory is a git repository."""
    if os.path.isdir(directory_path):
        git_subfolder = os.path.join(directory_path, ".git")
        if os.path.isdir(git_subfolder): # check for path/to/repository/.git
            return True
    return False

def get_tail_name(path):
    """Return the name of the right-most directory in a path. Uses
    os.path.split, but corrects for an error when the path ends with a /."""
    if path.endswith("/"):
        return os.path.split(path[:-1])[1]
    return os.path.split(path)[1]

def update_repository(repo_path, repo_name):
    """Update a single git repository by pulling from the remote."""
    out(1, "{}{}{}:".format(ansi['bold'], repo_name, ansi['reset']))
    
    os.chdir(repo_path) # cd into our folder so git commands target the correct
                        # repo
    
    try:
        dry_fetch = exec_shell("git fetch --dry-run") # check if there is
                                                      # anything to pull, but
                                                      # don't do it yet
    except subprocess.CalledProcessError:
        out(2, """{}Error:{} cannot fetch; do you have a remote repository
                configured correctly?""".format(ansi['red'], ansi['reset']))
        return
    
    try:
        last = exec_shell("git log -n 1 --pretty=\"%ar\"") # last commit time
    except subprocess.CalledProcessError:
        last = "never" # couldn't get a log, so no commits
    
    if not dry_fetch: # no new changes to pull
        out(2, "{}No new changes.{} Last commit was {}.".format(ansi['blue'],
                ansi['reset'], last))
        
    else: # stuff has happened!
        out(2, "There are new changes upstream...")
        status = exec_shell("git status")
    
        if status.endswith("nothing to commit (working directory clean)"):
            out(2, "{}Pulling new changes...{}".format(ansi['green'],
                    ansi['reset']))
            result = exec_shell("git pull")
            out(2, "The following changes have been made since {}:".format(
                    last))
            print result
        
        else:
            out(2, """{}Warning:{} You have uncommitted changes in this
                    repository!""".format(ansi['red'], ansi['reset']))
            out(2, "Ignoring.")

def update_directory(dir_path, dir_name, is_bookmark=False):
    """First, make sure the specified object is actually a directory, then
    determine whether the directory is a git repo on its own or a directory
    of git repositories. If the former, update the single repository; if the
    latter, update all repositories contained within."""
    if is_bookmark:
        dir_source = "Bookmark" # where did we get this directory from?
    else:
        dir_source = "Directory"
    
    try:
        os.listdir(dir_path) # test if we can access this directory
    except OSError:
        out(0, "{}Error:{} cannot enter {} '{}{}{}'; does it exist?".format(
        ansi['red'], ansi['reset'], dir_source.lower(), ansi['bold'], dir_path,
        ansi['reset']))
        return
    
    if not os.path.isdir(dir_path):
        if os.path.exists(dir_path):
            error_message = "is not a directory"
        else:
            error_message = "does not exist"
            
        out(0, "{}Error{}: {} '{}{}{}' {}!".format(ansi['red'], ansi['reset'],
                dir_source, ansi['bold'], dir_path, ansi['reset'],
                error_message))
        return
    
    if directory_is_git_repo(dir_path):
        out(0, "{} '{}{}{}' is a git repository:".format(dir_source,
                ansi['bold'], dir_path, ansi['reset']))
        update_repository(dir_path, dir_name)
        
    else:
        repositories = []
        
        dir_contents = os.listdir(dir_path) # get potential repos in directory
        for item in dir_contents:
            repo_path = os.path.join(dir_path, item)
            repo_name = os.path.join(dir_name, item)
            if directory_is_git_repo(repo_path): # filter out non-repositories
                repositories.append((repo_path, repo_name))
        
        repo_count = len(repositories)
        if repo_count == 1:
            pluralize = "repository"
        else:
            pluralize = "repositories"
            
        out(0, "{} '{}{}{}' contains {} git {}:".format(dir_source,
                ansi['bold'], dir_path, ansi['reset'], repo_count, pluralize))

        for repo_path, repo_name in repositories:
            update_repository(repo_path, repo_name)

def update_directories(paths):
    """Update a list of directories supplied by command arguments."""
    for path in paths:
        path = os.path.abspath(path) # convert relative to absolute path
        update_directory(path, get_tail_name(path), is_bookmark=False)

def update_bookmarks():
    """Loop through and update all bookmarks."""
    try:
        bookmarks = load_config_file().items("bookmarks")
    except configparser.NoSectionError:
        bookmarks = []
    
    if bookmarks:
        for bookmark_path, bookmark_name in bookmarks:
            update_directory(bookmark_path, bookmark_name, is_bookmark=True)
    else:
        out(0, """You don't have any bookmarks configured! Get help with
                'gitup -h'.""")

def load_config_file():
    """Read the file storing our config options from config_filename and return
    the resulting SafeConfigParser() object."""
    config = configparser.SafeConfigParser()
    config.optionxform = str # don't lowercase option names, because we are
                             # storing paths there
    config.read(config_filename)
    return config

def save_config_file(config):
    """Save our config changes to the config file specified by
    config_filename."""
    with open(config_filename, "wb") as config_file:
        config.write(config_file)

def add_bookmarks(paths):
    """Add a list of paths as bookmarks to the config file."""
    config = load_config_file()
    if not config.has_section("bookmarks"):
        config.add_section("bookmarks")
    
    out(0, "{}Added bookmarks:{}".format(ansi['yellow'], ansi['reset']))
    for path in paths:
        path = os.path.abspath(path) # convert relative to absolute path
        if config.has_option("bookmarks", path):
            out(1, "'{}' is already bookmarked.".format(path))
        else:
            config.set("bookmarks", path, get_tail_name(path))
            out(1, "{}{}{}".format(ansi['bold'], path, ansi['reset']))
    
    save_config_file(config)

def delete_bookmarks(paths):
    """Remove a list of paths from the bookmark config file."""
    config = load_config_file()
    
    if config.has_section("bookmarks"):
        out(0, "{}Deleted bookmarks:{}".format(ansi['yellow'], ansi['reset']))
        for path in paths:
            path = os.path.abspath(path) # convert relative to absolute path
            config_was_changed = config.remove_option("bookmarks", path)
            if config_was_changed:
                out(1, "{}{}{}".format(ansi['bold'], path, ansi['reset']))
            else:
                out(1, "'{}' is not bookmarked.".format(path))
        save_config_file(config)
    
    else:
        out(0, "There are no bookmarks to delete!")

def list_bookmarks():
    """Print all of our current bookmarks."""
    config = load_config_file()
    try:
        bookmarks = config.items("bookmarks")
    except configparser.NoSectionError:
        bookmarks = []
    
    if bookmarks:
        out(0, "{}Current bookmarks:{}".format(ansi['yellow'], ansi['reset']))
        for bookmark_path, bookmark_name in bookmarks:
            out(1, bookmark_path)
    else:
        out(0, "You have no bookmarks to display.")

def main():
    """Parse arguments and then call the appropriate function(s)."""
    parser = argparse.ArgumentParser(description="""Easily pull to multiple git
            repositories at once.""", epilog="""Both relative and absolute
            paths are accepted by all arguments. Questions? Comments? Email the
            author at {}.""".format(__email__), add_help=False)
    
    group_u = parser.add_argument_group("updating repositories")
    group_b = parser.add_argument_group("bookmarking")
    group_m = parser.add_argument_group("miscellaneous")
    
    group_u.add_argument('directories_to_update', nargs="*", metavar="path",
            help="""update all repositories in this directory (or the directory
            itself, if it is a repo)""")
    
    group_u.add_argument('-u', '--update', action="store_true", help="""update
            all bookmarks (default behavior when called without arguments)""")
    
    group_b.add_argument('-a', '--add', dest="bookmarks_to_add", nargs="+",
            metavar="path", help="add directory(s) as bookmarks")
    
    group_b.add_argument('-d', '--delete', dest="bookmarks_to_del", nargs="+",
            metavar="path",
            help="delete bookmark(s) (leaves actual directories alone)")
    
    group_b.add_argument('-l', '--list', dest="list_bookmarks",
            action="store_true", help="list current bookmarks")
    
    group_m.add_argument('-h', '--help', action="help",
            help="show this help message and exit")
    
    group_m.add_argument('-v', '--version', action="version",
            version="gitup version "+__version__)
    
    args = parser.parse_args()
    
    print "{}gitup{}: the git-repo-updater".format(ansi['bold'], ansi['reset'])
    
    if args.bookmarks_to_add:
        add_bookmarks(args.bookmarks_to_add)

    if args.bookmarks_to_del:
        delete_bookmarks(args.bookmarks_to_del)
    
    if args.list_bookmarks:
        list_bookmarks()
    
    if args.directories_to_update:
        update_directories(args.directories_to_update)
    
    if args.update:
        update_bookmarks()
    
    if not any(vars(args).values()): # if they did not tell us to do anything,
        update_bookmarks()           # automatically update bookmarks

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        out(0, "Stopped by user.")
