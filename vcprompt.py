#!/usr/bin/env python
from __future__ import with_statement
import binascii
import os
import re
import sqlite3
import sys
from subprocess import Popen, PIPE

FORMAT = "%s:%b"
SYSTEMS = []
REGEX = "/%(b|s|r)/"

UNKNOWN = "(unknown)"
if 'VCPROMPT_UNKNOWN' in os.environ.keys():
    if os.environ['VCPROMPT_UNKNOWN']:
        UNKNOWN = os.environ['VCPROMPT_UNKNOWN']



def vcs(function):
    """Simple decorator which adds the wrapped function to SYSTEMS variable"""
    SYSTEMS.append(function)
    return function


def vcprompt(path='.', string=FORMAT):
    paths = os.path.abspath(path).split()

    while paths:
        path = "/".join(paths)
        prompt = ''
        for vcs in SYSTEMS:
            prompt = vcs(path, string)
            if prompt:
                return prompt
        paths.pop()
    return ""


@vcs
def bzr(path, string):
    file = os.path.join(path, '.bzr/branch/last-revision')
    if not os.path.exists(file):
        return None

    # system
    string = string.replace('%s', 'bzr')

    # local revision number
    if '%r' in string:
        with open(file, 'r') as f:
            line = f.read().strip().split(' ', 1)[0]
            string = string.replace('%r', line)
    return string


@vcs
def cvs(path, string):
    # Stabbing in the dark here
    # TODO make this not suck
    file = os.path.join(path, 'CVS/')
    if not os.path.exists(file):
        return None
    string = string.replace('%s', 'cvs')
    string = string.replace('%b', UNKNOWN)
    return string


@vcs
def fossil(path, string):
    # In my five minutes of playing with Fossil this looks OK
    file = os.path.join(path, '_FOSSIL_')
    if not os.path.exists(file):
        return None

    branch = revision = UNKNOWN
    command = 'fossil info'
    pipe = Popen(command, shell=True, stdout=PIPE)
    for line in pipe.stdout:
        line = line.strip()

        # branch/tag
        if branch == UNKNOWN:
            match = re.match('^tags:(\s+)(?P<branch>\w+)', line)
            if match:
                branch = match.group('branch')

        # hash
        if revision == UNKNOWN:
            match = re.match('^checkout:(\s+)(?P<revision>\w+)', line)
            if match:
                revision = match.group('revision')[0:7]

    # branch
    string = string.replace('%b', branch)

    # hash/revision
    string = string.replace('%h', revision)
    string = string.replace('%r', revision)

    # system
    string = string.replace('%s', 'fossil')

    return string


@vcs
def hg(path, string):
    files = ['.hg/branch', '.hg/undo.branch']
    file = None
    for f in files:
        f = os.path.join(path, f)
        if os.path.exists(f):
            file = f
            break
    if not file:
        return None

    # local revision or global hash (revision ID)
    if re.search('%(r|h)', string):
        # we have dive into the Mercurial 'API' here
        try:
            from mercurial import ui, hg
        except ImportError:
            string = UNKNOWN
        repo = hg.repository(ui.ui(), path)
        change = repo.changectx('.')

        # revision
        rev = str(change.rev())
        string = string.replace('%r', rev)

        # hash
        hash = binascii.b2a_hex(change.node())[0:7]
        string = string.replace('%h', hash)

    if '%b' in string:
        with open(file, 'r') as f:
            branch = f.read().strip()
            string = string.replace('%b', branch)

    # system
    string = string.replace('%s', 'hg')

    return string

@vcs
def git(path, string):
    file = os.path.join(path, '.git/')
    if not os.path.exists(file):
        return None

    # the current branch is required to get the hash
    _branch = ""
    if re.search("%(b|r)", string):
        _file = os.path.join(file, 'HEAD')
        with open(_file, 'r') as f:
            line = f.read()
            if re.match('^ref: refs/heads/', line.strip()):
                _branch = (line.split('/')[-1] or UNKNOWN).strip()

        # branch
        string = string.replace("%b", _branch)

        # hash/revision
        if "%r" in string:
            _file = os.path.join(file, 'refs/heads/%s' % _branch)
            with open(_file, 'r') as f:
                hash = f.read().strip()[0:7]
                string = string.replace("%r", hash)


    # system
    if '%s' in string:
        string = string.replace("%s", 'git')

    return string


@vcs
def svn(path, string):
    file = os.path.join(path, '.svn/entries')
    if not os.path.exists(file):
        return None

    # revision/hash
    if re.search('%(r|h)', string):
        revision = UNKNOWN
        pattern = "^Revision:"
        command = """svn info %s""" % path
        pipe = Popen(command, shell=True, stdout=PIPE)
        for line in pipe.stdout:
            match = re.match('^Revision: (?P<revision>\d+)', line)
            if match:
                revision = match.group('revision')

        string = string.replace('%r', revision)
        string = string.replace('%h', revision)

    # branch
    if '%b' in string:
        command = """svn info %s |
                     grep '^URL:' |
                     egrep -o '(tags|branches)/[^/]+|trunk' |
                     egrep -o '[^/]+$'""" % path
        branch = Popen(command, shell=True, stdout=PIPE).stdout.read().strip()
        if not branch:
            branch = UNKNOWN
        string = string.replace('%b', branch)

    # system
    string = string.replace("%s", "svn")
    return string


if __name__ == '__main__':
    string = FORMAT
    if len(sys.argv) > 1:
        string = sys.argv[1]
    else:
        if 'VCPROMPT_FORMAT' in os.environ.keys():
            if os.environ['VCPROMPT_FORMAT']:
                string = os.environ['VCPROMPT_FORMAT']
    sys.stdout.write(vcprompt('.', string))
