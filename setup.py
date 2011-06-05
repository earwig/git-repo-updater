from distutils.core import setup
import os
import sys

if sys.hexversion < 0x02070000:
    exit("Please upgrade to Python 2.7 or greater: <http://python.org/>.")

remove_py_extension = True # install script as "gitup" instead of "gitup.py"

if os.path.exists("gitup"):
    remove_py_extension = False
else:
    os.rename("gitup.py", "gitup")

desc = "Easily and intelligently pull to multiple git projects at once."

with open('README.md') as file:
    long_desc = file.read()

try:
    setup(
        name = "gitup",
        version = "0.1",
        scripts = ['gitup'],
        author = "Ben Kurtovic",
        author_email = "ben.kurtovic@verizon.net",
        description = desc,
        long_description = long_desc,
        license = "MIT License",
        keywords = "git project repository pull update",
        url = "http://github.com/earwig/git-repo-updater",
        classifiers = ["Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Version Control"
        ]
    )
    
finally:
    if remove_py_extension:
        os.rename("gitup", "gitup.py") # restore file location
