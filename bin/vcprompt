#!/usr/bin/env python
"""
Usage: vcprompt [options]

Version control information in your prompt.

Options:
  -f, --format FORMAT        The format string to use.
  -p, --path PATH            The path to run vcprompt on.
  -d, --max-depth DEPTH      The maximum number of directories to traverse.
  -s, --systems SYSTEMS      The version control systems to use.
  -u, --unknown UNKNOWN      The "unknown" value.
  -v, --version              Show program's version number and exit
  -h, --help                 Show this help message and exit

VCS-specific formatting:
  These options can be used for VCS-specific prompt formatting.

  --format-bzr FORMAT        Bazaar
  --format-cvs FORMAT        CVS
  --format-darcs FORMAT      Darcs
  --format-fossil FORMAT     Fossil
  --format-git FORMAT        Git
  --format-hg FORMAT         Mercurial
  --format-svn FORMAT        Subversion

Internal options:
  These options are used internally or for testing. Use of these is not
  recommended.

  --values OPTIONS         Prints the values of the given `OPTIONS` to stdout.
  --without-environment    Ignore any environment variables and fall back to
                           just the provided (or default) values. If used, this
                           option must come before any other provided options.
"""

from __future__ import with_statement
from subprocess import Popen, PIPE
import optparse
import os
import re
import sqlite3
import sys

__version__ = (0, 1, 5)


# check to make sure the '--without-environment' flag is called first
# this could be done in a callback, but we'd have to keep a note of every
# option which is affected by this flag
if '--without-environment' in sys.argv and \
   sys.argv[1] != '--without-environment':
    output = "The '--without-environment' option must come before any "
    print "%s other options." % output
    sys.exit(1)

# we need to get this in early because callbacks are always called after
# every other option is already set, regardless of when the callback option
# is actually used in the script
if len(sys.argv) > 1 and sys.argv[1] == '--without-environment':
    for k in os.environ.keys():
        if k.startswith('VCPROMPT'):
            del os.environ[k]
    del sys.argv[1]


DEPTH = os.environ.get('VCPROMPT_DEPTH', 0)
FORMAT = os.environ.get('VCPROMPT_FORMAT', '%s:%b')
UNKNOWN = os.environ.get('VCPROMPT_UNKNOWN', '(unknown)')
SYSTEMS = []


def helper(*args, **kwargs):
    """
    Prints the module's docstring.

    Doing this kills two birds with one stone: it adds PEP 257
    compliance and allows us to stop using optparse's built-in
    help flag.

    """
    print __doc__.strip()
    sys.exit(0)


def sorted_alpha(sortme, unique=True):
    """
    Sorts a string alphabetically, but does (kind of) the opposite of
    the built-in ``sorted`` function.

    Sorted order is:

      * lowercase
      * uppercase
      * digits
      * punctuation

    Example:

    >>> sorted_alpha("aSD??fc?!")
    afcSD?!

    """
    upper, lower, digit, punctuation, passed = ([], [], [], [], [])
    passed = []
    for char in sortme:
        # skip duplicates
        if unique and char in passed:
            continue

        if char.isupper():
            upper.append(char)
        elif char.islower():
            lower.append(char)
        elif char.isdigit():
            digit.append(char)
        else:
            punctuation.append(char)

        passed.append(char)

    return ''.join(lower + upper + digit + punctuation)


def systems():
    """Prints all available systems to stdout."""
    for system in SYSTEMS:
        name = getattr(system, 'name', system.__name__)
        desc = getattr(system, 'description', '')
        output = "%s: %s" % (name, desc)
        print output
    sys.exit(0)


def values(option, opt, value, parser, *args, **kwargs):
    """
    Prints the given values to stdout.

    This function is *private* and should not be relied on.
    """
    for option in parser.rargs:
        if option == 'SYSTEMS':
            systems()
        if option in globals().keys():
            print globals()[option]
    sys.exit(0)


def vcs(name, description):
    """
    Adds the given ``name`` and ``description`` as attributes on the
    wrapped function.

    Arguments:

        ``name``
            The display name for the system. E.g. "Mercurial" or
            "Subversion".

         ``description``
             The description for the system. E.g.:
             "The fast version continue system".

    """

    def wrapped(function):
        function.name = name
        function.description = name
        SYSTEMS.append(function)
        return function
    return wrapped


def version(*args):
    """
    Convenience function for printing a version number.
    """
    print 'vcprompt %s' % '.'.join(map(str, __version__))
    sys.exit(0)


def vcprompt(path, formats, unknown, *args, **kwargs):
    """
    Returns a formatted version control string for use in a shell prompt
    or elsewhere.

    Arguments:

        ``path``
            A path for vcprompt to check for version control systems

            Defaults to the current working directory.

        ``formats``
            A dictionary mapping version control systems to formatting
            strings to use for said system.

            The default format key should be named 'default'.

         ``unknown``
             The string to use for when ``vcprompt`` cannot determine a
             value.

    Keyword Arguments:

        ``depth``
           The maximum number of directories that ``vcprompt`` will traverse
           in order to find a version control system.

           Defaults to 0 (no limit).


       ``systems``

           A list of systems for ``vcprompt`` to search for over the given
           ``path``.

           Defaults to all systems.

    """

    paths = os.path.abspath(os.path.expanduser(path)).split('/')
    depth = kwargs.get('depth', 0)
    systems = kwargs.get('systems', None)
    prompt = None
    count = 0

    while paths:
        path = '/'.join(paths)
        paths.pop()
        for vcs in SYSTEMS:
            if not systems or systems and vcs.__name__ in systems:
                format = formats[vcs.__name__] or formats['default']
                prompt = vcs(path, format, unknown)
                if prompt:
                    return prompt
        if depth:
            if count == depth:
                break
            count += 1
    return ''


def main():
    # parser
    parser = optparse.OptionParser()

    # dump the provided --help option
    parser.remove_option('--help')

    # our own --help flag
    parser.add_option('-h', '--help', action='callback', callback=helper)

    # format
    parser.add_option('-f', '--format', dest='format', default=FORMAT)

    # path
    parser.add_option('-p', '--path', dest='path', default='.')

    # max depth
    parser.add_option('-d', '--max-depth', dest='depth', type='int',
                      default=DEPTH)
    # systems
    parser.add_option('-s', '--systems', dest='systems', action='append')

    # unknown
    parser.add_option('-u', '--unknown', dest='unknown', default=UNKNOWN)

    # version
    parser.add_option('-v', '--version', action='callback', callback=version)

    # values
    parser.add_option('--values', dest='values', action='callback',
                      callback=values)

    # vcs-specific formatting
    for system in SYSTEMS:
        default = 'VCPROMPT_FORMAT_%s' % system.__name__.upper()
        default = os.environ.get(default, None)
        dest = 'format-%s' % system.__name__
        flag = '--%s' % dest
        parser.add_option(flag, dest=dest, default=default)


    # parse!
    options, args = parser.parse_args()

    # break out formats into their own dictionary
    formats = {}
    for k, v in options.__dict__.items():
        if k.startswith('format'):
            k = k.split('format-')[-1]
            if k == 'format':
                k = 'default'
            formats[k] = v

    output = vcprompt(depth=options.depth, formats=formats, path=options.path,
                      systems=options.systems, unknown=options.unknown)

    return output


@vcs('Bazaar', 'The Bazaar version control system')
def bzr(path, string, unknown):
    file = os.path.join(path, '.bzr/branch/last-revision')
    if not os.path.exists(file):
        return None

    branch = revision = hash = status = unknown

    # local revision or global hash
    if re.search('%(r|h)', string):
        with open(file, 'r') as f:
            for line in f:
                line = line.strip()
                revision = line.split()[0]
                hash = line.rsplit('-', 1)[0][:7]
                break


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

            status = sorted_alpha(status)

    # formatting
    string = string.replace('%b', os.path.basename(path))
    string = string.replace('%h', hash)
    string = string.replace('%r', revision)
    string = string.replace('%i', status)
    string = string.replace('%s', 'bzr')
    return string


@vcs('CVS', 'Concurrent Versions System.')
def cvs(path, string, unknown):
    # Stabbing in the dark here
    # TODO make this not suck
    file = os.path.join(path, 'CVS/')
    if not os.path.exists(file):
        return None

    branch = revision = status = unknown

    string = string.replace('%s', 'cvs')
    string = string.replace('%b', branch)
    string = string.replace('%i', status)
    string = string.replace('%h', revision)
    string = string.replace('%r', revision)
    return string


@vcs('Darcs', 'Distributed. Interactive. Smart.')
def darcs(path, string, unknown):
    # It's almost a given that everything in here is
    # going to be wrong
    file = os.path.join(path, '_darcs/hashed_inventory')
    if not os.path.exists(file):
        return None

    hash = branch = status = unknown

    # hash
    if re.search('%(h|r)', string):
        with open(file, 'r') as f:
            for line in f:
                size, hash = line.strip().split('-')
                hash = hash[:7]
                break

    # branch
    # darcs doesn't have in-repo local branching (yet), so just use
    # the directory name for now
    # see also: http://bugs.darcs.net/issue555
    branch = os.path.basename(path)

    # status
    if '%i' in string:
        status = ''
        command = 'darcs whatsnew -l'
        process = Popen(command.split(), stdout=PIPE, stderr=PIPE)
        output = process.communicate()[0]
        returncode = process.returncode

        if not returncode:
            for line in output.split('\n'):
                code = line.split(' ')[0]
                status = '%s%s' % (status, code)
            status = sorted_alpha(status)

    # formatting
    string = string.replace('%b', branch)
    string = string.replace('%h', hash)
    string = string.replace('%r', hash)
    string = string.replace('%i', status)
    string = string.replace('%s', 'darcs')
    return string


@vcs('Fossil', 'The Fossil version control system.')
def fossil(path, string, unknown):
    file = os.path.join(path, '_FOSSIL_')
    if not os.path.exists(file):
        return None

    branch = hash = status = unknown

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

    # we can grab the latest hash the manifest.uuid file
    manifest = os.path.join(path, 'manifest.uuid')
    if os.path.exists(manifest):
        with open(manifest, 'r') as f:
            for line in f:
                hash = line.strip()[:7]
                break

    # branch
    if hash != unknown:
        try:
            query = """SELECT value FROM tagxref WHERE rid =
                       (SELECT rid FROM blob WHERE uuid LIKE '%s%%')
                       AND value is not NULL LIMIT 1 """ % hash
            conn = sqlite3.connect(repository)
            c = conn.cursor()
            c.execute(query)
            branch = c.fetchone()[0]
        except (sqlite3.OperationalError, TypeError):
            pass
        finally:
            conn.close()

    # status
    if '%i' in string:
        # new files
        command = 'fossil extra'
        process = Popen(command.split(), stdout=PIPE)
        output = process.communicate()[0]
        returncode = process.returncode

        if not returncode and output:
            if status == unknown:
                status = ''
            status = "%s?" % status

        command = 'fossil changes'
        process = Popen(command.split(), stdout=PIPE)
        output = process.communicate()[0]
        returncode = process.returncode

        if not returncode:
            if status == unknown:
                status = ''
            headers = {'EDITED': 'M',
                       'MISSING': 'R'}
            for line in output.split('\n'):
                line = line.strip()
                if line:
                    status = "%s%s" % (status, line[0])

            status = sorted_alpha(status)

    # parse out formatting string
    string = string.replace('%b', branch)
    string = string.replace('%h', hash)
    string = string.replace('%r', hash)
    string = string.replace('%i', status)
    string = string.replace('%s', 'fossil')
    return string


@vcs('Git', 'The fast version control system.')
def git(path, string, unknown):
    file = os.path.join(path, '.git/')
    if not os.path.exists(file):
        return None

    branch = hash = status = unknown
    # the current branch is required to get the hash
    if re.search('%(b|r|h)', string):
        branch_file = os.path.join(file, 'HEAD')
        with open(branch_file, 'r') as f:
            for line in f:
                line = line.strip()
                if re.match('^ref: refs/heads/', line.strip()):
                    branch = (line.split('/')[-1] or unknown).strip()
                    break

        # hash/revision
        if re.search('%(r|h)', string) and branch != unknown:
            hash_file = os.path.join(file, 'refs/heads/%s' % branch)
            with open(hash_file, 'r') as f:
                for line in f:
                    hash = line.strip()[0:7]
                    break

    # status
    if '%i' in string:
        command = 'git status'
        process = Popen(command.split(), stdout=PIPE, stderr=PIPE)
        output = process.communicate()[0]
        returncode = process.returncode

        if not returncode:
            headers = {'modified': 'M',
                       'removed': 'D',
                       'renamed': 'R',
                       'Untracked': '?'}
            status = ''
            for line in output.split('\n'):
                # strip the hashes from the lines
                line = line[1:].strip()
                # ignore informational and blank lines
                if line and not line.startswith('('):
                    for key in headers.keys():
                        if line.startswith(key):
                            status += headers[key]
                            break
            status = sorted_alpha(status)

    # formatting
    string = string.replace('%b', branch)
    string = string.replace('%h', hash)
    string = string.replace('%r', hash)
    string = string.replace('%i', status)
    string = string.replace('%s', 'git')
    return string


@vcs('Mercurial', 'The Mercurial version control system.')
def hg(path, string, unknown):
    file = os.path.join(path, '.hg/branchheads.cache')
    if not os.path.exists(file):
        return None

    branch = revision = hash = status = unknown

    # changeset ID or global hash
    if re.search('%(r|h)', string):
        cache_file = os.path.join(path, '.hg/tags.cache')
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                for line in f:
                    revision, hash = line.strip().split()
                    hash = hash[:7]
                    break

    # branch
    if re.search('%(r|h|b)', string):
        count = 0
        with open(file, 'r') as f:
            for line in f:
                hash, revision_branch = line.split()
                hash = hash[:7]
                if count > 0:
                    branch = revision_branch
                    break
                else:
                    revision = revision_branch
                count += 1

    # status
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
            status = sorted_alpha(status)

    string = string.replace('%b', branch)
    string = string.replace('%h', hash)
    string = string.replace('%r', revision)
    string = string.replace('%i', status)
    string = string.replace('%s', 'hg')
    return string


@vcs('Subversion', 'The Subversion version control system.')
def svn(path, string, unknown):
    file = os.path.join(path, '.svn/entries')
    if not os.path.exists(file):
        return None

    branch = revision = status = unknown

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

            status = sorted_alpha(status)

    # formatting
    string = string.replace('%r', revision)
    string = string.replace('%h', revision)
    string = string.replace('%b', branch)
    string = string.replace('%i', status)
    string = string.replace('%s', 'svn')
    return string


if __name__ == '__main__':
    print main()
