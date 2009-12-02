#!/usr/bin/env python
import os
import re
import sys
from subprocess import Popen, PIPE

UNKNOWN = "(unknown)"
SYSTEMS = []


def vcs(function):
    SYSTEMS.append(function)
    return function


@vcs
def bzr(path):
    file = '.bzr/branch/last-revision'
    if not os.path.exists(os.path.join(path, file)):
        return None
    with open(file, 'r') as f:
        line = f.read().split(' ', 1)[0]
        return 'bzr:r' + (line or UNKNOWN)


@vcs
def hg(path):
    file = '.hg/branch'
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
    if not os.path.exists(os.path.join(path, '.svn')):
        return None
    _p = Popen(['svnversion', path], stdout=PIPE)
    revision = _p.communicate()[0]
    if not revision:
        revision = UNKNOWN
    return 'svn:r' + revision


def vcprompt(path=None):
    path = path or os.getcwd()
    count = 0
    while path:
        if count > 0:
            path = path.rsplit('/', 1)[0]
        if not path:
            path = '/'

        # get vcs
        prompt = ''
        for vcs in SYSTEMS:
            prompt = vcs(path)
            if prompt:
                return prompt
        count += 1


if __name__ == '__main__':
    sys.stdout.write(vcprompt())
