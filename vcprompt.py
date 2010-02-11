#!/usr/bin/env python
from __future__ import with_statement

__version__ = (0, 1, 0)

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
if 'VCPROMPT_UNKNOWN' in list(os.environ.keys()):
    if os.environ['VCPROMPT_UNKNOWN']:
        UNKNOWN = os.environ['VCPROMPT_UNKNOWN']


def vcs(function):
    """Simple decorator which adds the wrapped function to SYSTEMS variable"""
    SYSTEMS.append(function)
    return function


def vcprompt(path='.', string=FORMAT):
    paths = os.path.abspath(path).split('/')

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

    branch = hash = UNKNOWN

    # local revision number
    if re.search('%(r|h)', string):
        with open(file, 'r') as f:
            hash = f.read().strip().split(' ', 1)[0]

    # branch
    # TODO figure out something more correct
    string = string.replace('%b', os.path.basename(path))
    string = string.replace('%h', hash)
    string = string.replace('%r', hash)
    string = string.replace('%s', 'bzr')
    return string


@vcs
def cvs(path, string):
    # Stabbing in the dark here
    # TODO make this not suck
    file = os.path.join(path, 'CVS/')
    if not os.path.exists(file):
        return None

    branch = revision = UNKNOWN

    string = string.replace('%s', 'cvs')
    string = string.replace('%b', branch)
    string = string.replace('%r', revision)
    return string


@vcs
def fossil(path, string):
    # In my five minutes of playing with Fossil this looks OK
    file = os.path.join(path, '_FOSSIL_')
    if not os.path.exists(file):
        return None

    branch = hash = UNKNOWN

    # all this just to get the repository file :(
    repository = None
    try:
        query = "SELECT value FROM vvar where name = 'repository'"
        conn = sqlite3.connect(file)
        c = conn.cursor()
        c.execute(query)
        repository = c.fetchone()[0]
    except sqlite3.OperationalError:
        pass
    finally:
        conn.close()

    if repository:
        # get the hash. we need this to get the current trunk
        _rid = None
        if re.search('%(b|h|r)', string):
            try:
                query = """SELECT uuid, rid FROM blob ORDER BY rid DESC LIMIT 1"""
                conn = sqlite3.connect(repository)
                c = conn.cursor()
                c.execute(query)
                hash, _rid = c.fetchone()
                hash = hash[:7]
            except sqlite3.OperationalError:
                pass
            finally:
                conn.close()

           # now we grab the branch
            try:
                query = """SELECT value FROM tagxref WHERE rid = %d and value is not NULL LIMIT 1 """ % _rid
                conn = sqlite3.connect(repository)
                c = conn.cursor()
                c.execute(query)
                branch = c.fetchone()[0]
            except sqlite3.OperationalError:
                pass
            finally:
                conn.close()


    # parse out formatting string
    string = string.replace('%b', branch)
    string = string.replace('%h', hash)
    string = string.replace('%r', hash)
    string = string.replace('%s', 'fossil')
    return string


@vcs
def git(path, string):
    file = os.path.join(path, '.git/')
    if not os.path.exists(file):
        return None

    branch = hash = UNKNOWN
    # the current branch is required to get the hash
    if re.search("%(b|r|h)", string):
        branch_file = os.path.join(file, 'HEAD')
        with open(branch_file, 'r') as f:
            line = f.read()

            # check if we're currently running on a branch
            if re.match('^ref: refs/heads/', line.strip()):
                branch = (line.split('/')[-1] or UNKNOWN).strip()
            # we're running with a detached head (submodule?)
            else:
                branch = os.listdir(os.path.join(file, 'refs/heads'))[0]


        # hash/revision
        hash = UNKNOWN
        if re.search("%(r|h)", string):
            hash_file = os.path.join(file, 'refs/heads/%s' % branch)
            with open(hash_file, 'r') as f:
                hash = f.read().strip()[0:7]


    # formatting
    string = string.replace("%b", branch)
    string = string.replace("%h", hash)
    string = string.replace("%r", hash)
    string = string.replace("%s", 'git')
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

    branch = revision = hash = UNKNOWN

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
        revision = str(change.rev())

        # hash
        hash = binascii.b2a_hex(change.node())[0:7]

    if '%b' in string:
        with open(file, 'r') as f:
            branch = f.read().strip()

    # formatting
    string = string.replace('%b', branch)
    string = string.replace('%h', hash)
    string = string.replace('%r', revision)
    string = string.replace('%s', 'hg')
    return string


@vcs
def svn(path, string):
    file = os.path.join(path, '.svn/entries')
    if not os.path.exists(file):
        return None

    branch = revision = UNKNOWN

    # revision/hash
    if re.search('%(r|h)', string):
        revision = UNKNOWN
        pattern = "^Revision:"
        command = "svn info %s" % path
        pipe = Popen(command, shell=True, stdout=PIPE,
                     stderr=open('/dev/null', 'w'))
        for line in pipe.communicate()[0].split('\n'):
            match = re.match('^Revision: (?P<revision>\d+)', line)
            if match:
                revision = match.group('revision')

    # branch
    if '%b' in string:
        command = """svn info %s |
                     grep '^URL:' |
                     egrep -o '(tags|branches)/[^/]+|trunk' |
                     egrep -o '[^/]+$'""" % path
        branch = Popen(command, shell=True, stdout=PIPE,
                       stderr=open('/dev/null', 'w')).communicate()[0]
        if not branch:
            branch = UNKNOWN


    # formatting
    string = string.replace('%r', revision)
    string = string.replace('%h', revision)
    string = string.replace('%b', branch)
    string = string.replace("%s", "svn")
    return string


if __name__ == '__main__':
    string = FORMAT
    if len(sys.argv) > 1:
        string = sys.argv[1]
    else:
        if 'VCPROMPT_FORMAT' in list(os.environ.keys()):
            if os.environ['VCPROMPT_FORMAT']:
                string = os.environ['VCPROMPT_FORMAT']
    sys.stdout.write(vcprompt('.', string))
