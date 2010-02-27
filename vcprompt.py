#!/usr/bin/env python
from __future__ import with_statement

__version__ = (0, 1, 0)

import os
import re
import sqlite3
import sys
from subprocess import Popen, PIPE

FORMAT = '%s:%b'
SYSTEMS = []
UNKNOWN = '(unknown)'

if 'VCPROMPT_UNKNOWN' in list(os.environ.keys()):
    if os.environ['VCPROMPT_UNKNOWN']:
        UNKNOWN = os.environ['VCPROMPT_UNKNOWN']

if len(sys.argv) > 1:
    FORMAT = sys.argv[1]
else:
    if 'VCPROMPT_FORMAT' in list(os.environ.keys()):
        if os.environ['VCPROMPT_FORMAT']:
            FORMAT = os.environ['VCPROMPT_FORMAT']


def vcs(function):
    """Simple decorator which adds the wrapped function to SYSTEMS variable"""
    SYSTEMS.append(function)
    return function


def vcprompt(path='.', string=FORMAT):
    paths = os.path.abspath(path).split('/')
    prompt = None
    while paths:
        path = '/'.join(paths)
        paths.pop()
        if prompt:
            return prompt
        for vcs in SYSTEMS:
            prompt = vcs(path, string)
            if prompt:
                break
    return ''


@vcs
def bzr(path, string):
    file = os.path.join(path, '.bzr/branch/last-revision')
    if not os.path.exists(file):
        return None

    branch = hash = status = UNKNOWN

    # local revision number
    if re.search('%(r|h)', string):
        with open(file, 'r') as f:
            hash = f.read().strip().split(' ', 1)[0]


    # status
    if '%i' in string:
        command = 'bzr status'
        process = Popen(command.split(), stdout=PIPE)
        output = process.communicate()[0]
        returncode = process.returncode

        if not returncode:
            # the list of headers in 'bzr status' output
            headers = {'added': 'A',
                       'modified': 'M',
                       'removed': 'R',
                       'renamed': 'V',
                       'kind changed': 'K',
                       'unknown': '?'}
            headers_regex = '%s:' % '|'.join(headers.keys())

            status = ''
            for line in output.split('\n'):
                line = line.strip()
                if re.match(headers_regex, line):
                    header = line.split(':')[0]
                    status = '%s%s' % (status, headers[header])

            status = ''.join(sorted(set(status)))

    # branch
    # TODO figure out something more correct
    string = string.replace('%b', os.path.basename(path))
    string = string.replace('%h', hash)
    string = string.replace('%r', hash)
    string = string.replace('%i', status)
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
def darcs(path, string):
    # It's almost a given that everything in here is
    # going to be wrong
    file = os.path.join(path, '_darcs/hashed_inventory')
    if not os.path.exists(file):
        return None

    hash = branch = UNKNOWN
    # hash
    if re.search('%(h|r)', string):
        with open(file, 'r') as f:
            size, hash = f.read().strip().split('\n')[0].split('-')
            hash = hash[:7]

    string = string.replace('%b', branch)
    string = string.replace('%h', hash)
    string = string.replace('%r', hash)
    string = string.replace('%s', 'darcs')
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
                query = """SELECT uuid, rid FROM blob
                           ORDER BY rid DESC LIMIT 1"""
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
                query = """SELECT value FROM tagxref WHERE rid = %d and
                           value is not NULL LIMIT 1 """ % _rid
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

    branch = hash = status = UNKNOWN
    # the current branch is required to get the hash
    if re.search('%(b|r|h)', string):
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
        if re.search('%(r|h)', string):
            hash_file = os.path.join(file, 'refs/heads/%s' % branch)
            with open(hash_file, 'r') as f:
                hash = f.read().strip()[0:7]

    # status
    status = UNKNOWN
    if '%i' in string:
        command = 'git status --short'
        process = Popen(command.split(), stdout=PIPE, stderr=PIPE)
        output = process.communicate()[0]
        returncode = process.returncode

        # only process if ``git status`` has the --short option
        if not returncode:
            status = ''
            for line in output.split('\n'):
                code = line.strip().split(' ')[0]
                status = '%s%s' % (status, code)

    if status != UNKNOWN:
        status = ''.join(sorted(set(status)))

    # formatting
    string = string.replace('%b', branch)
    string = string.replace('%h', hash)
    string = string.replace('%r', hash)
    string = string.replace('%i', status)
    string = string.replace('%s', 'git')
    return string


@vcs
def hg(path, string):
    files = ['.hg/branch', '.hg/undo.branch' '.hg/bookmarks.current']
    file = None
    for f in files:
        f = os.path.join(path, f)
        if os.path.exists(f):
            file = f
            break
    if not file:
        return None

    branch = revision = hash = status = UNKNOWN

    # changeset ID or global hash
    if re.search('%(r|h)', string):
        cache_file = os.path.join(path, '.hg/tags.cache')
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                revision, hash = f.read().split()
                hash = hash[:7]

    # branch
    if '%b' in string:
        with open(file, 'r') as f:
            branch = f.read().strip()

    # status
    status = UNKNOWN
    if '%i' in string:
        command = 'hg status'
        process = Popen(command.split(), stdout=PIPE)
        output = process.communicate()[0]
        returncode = process.returncode
        if not returncode:
            status = ''
            for line in output.split('\n'):
                code = line.strip().split(' ')[0]
                status = '%s%s' % (status, code)

            # sort the string to make it all pretty like
            status = ''.join(sorted(set(status)))

    string = string.replace('%b', branch)
    string = string.replace('%h', hash)
    string = string.replace('%r', revision)
    string = string.replace('%i', status)
    string = string.replace('%s', 'hg')
    return string


@vcs
def svn(path, string):
    file = os.path.join(path, '.svn/entries')
    if not os.path.exists(file):
        return None

    branch = revision = status = UNKNOWN

    # branch
    command = 'svn info %s' % path
    process = Popen(command.split(), stdout=PIPE, stderr=PIPE)
    output = process.communicate()[0]
    returncode = process.returncode

    if not returncode:
        # compile some regexes
        branch_regex = re.compile('((tags|branches)|trunk)')
        revision_regex = re.compile('^Revision: (?P<revision>\d+)')

        for line in output.split('\n'):
            # branch
            if '%b' in string:
                if re.match('URL:', line):
                    matches = re.search(branch_regex, line)
                    if matches:
                        branch = matches.groups(0)[0]

            # revision/hash
            if re.search('%(r|h)', string):
                if re.match('Revision:', line):
                    matches = re.search(revision_regex, line)
                    if 'revision' in matches.groupdict():
                        revision = matches.group('revision')

    # status
    if '%i' in string:
        command = 'svn status'
        process = Popen(command, shell=True, stdout=PIPE)
        output = process.communicate()[0]
        returncode = process.returncode

        if not returncode:
            status = ''
            for line in output.split('\n'):
                code = line.strip().split(' ')[0]
                status = '%s%s' % (status, code)

            status = ''.join(sorted(set(status)))

    # formatting
    string = string.replace('%r', revision)
    string = string.replace('%h', revision)
    string = string.replace('%b', branch)
    string = string.replace('%i', status)
    string = string.replace('%s', 'svn')
    return string


if __name__ == '__main__':
    sys.stdout.write(vcprompt('.', FORMAT))
