#!/usr/bin/env python
from __future__ import with_statement
import os
import re
import sqlite3
import sys
from subprocess import Popen, PIPE

UNKNOWN = "(unknown)"
SYSTEMS = []


def vcs(function):
    SYSTEMS.append(function)
    return function


@vcs
def bzr(path):
    file = os.path.join(path, '.bzr/branch/last-revision')
    if not os.path.exists(os.path.join(path, file)):
        return None
    with open(file, 'r') as f:
        line = f.read().split(' ', 1)[0]
        return 'bzr:r' + (line or UNKNOWN)


@vcs
def fossil(path):
    # In my five minutes of playing with Fossil this looks OK
    file = os.path.join(path, '_FOSSIL_')
    if not os.path.exists(file):
        return None

    repo = UNKNOWN
    conn = sqlite3.connect(file)
    c = conn.cursor()
    repo = c.execute("""SELECT * FROM
                        vvar WHERE
                        name = 'repository' """)
    repo = repo.fetchone()[1].split('/')[-1]
    return "fossil:" + repo


@vcs
def hg(path):
    file = os.path.join(path, '.hg/branch')
    if not os.path.exists(os.path.join(path, file)):
        return None
    with open(file, 'r') as f:
        line = f.read()
        return 'hg:' + (line or UNKNOWN)


@vcs
def git(path):
    prompt = "git:"
    branch = UNKNOWN
    file = os.path.join(path, '.git/HEAD')
    if not os.path.exists(file):
        return None

    with open(file, 'r') as f:
        line = f.read()
        if re.match('^ref: refs/heads/', line.strip()):
            branch = (line.split('/')[-1] or UNKNOWN)
    return prompt + branch


@vcs
def svn(path):
    # I'm not too keen on calling an external script
    # TODO find a way to do this in pure Python without the svn bindings
    revision = UNKNOWN
    if not os.path.exists(os.path.join(path, '.svn')):
        return None
    _p = Popen(['svnversion', path], stdout=PIPE)
    revision = _p.communicate()[0]
    return 'svn:r' + revision


def vcprompt(path=None):
    path = path or os.getcwd()
    looped = end = False

    while True:
        if looped:
            path = path.rsplit('/', 1)[0]
        else:
            looped = True
        if not path:
            if not end:
                end = True
                path = '/'
            else:
                return ""

        # get vcs
        prompt = ''
        for vcs in SYSTEMS:
            prompt = vcs(path)
            if prompt:
                return prompt


if __name__ == '__main__':
    sys.stdout.write(vcprompt())
