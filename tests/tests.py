#!/usr/bin/env python
from subprocess import Popen, PIPE
import os
import re
import sys
import unittest


class Base(unittest.TestCase):

    commands = ['../bin/vcprompt']

    def data(self, field):
        """
        Returns the value for the given ``field`` from the
        'tests/data' directory for each repository.
        """
        location = os.path.abspath(__file__).rsplit('/', 1)[0]
        location = os.path.join(location, 'data', self.repository, field)
        return open(location).read().strip()

    def get_repository(self):
        """
        Returns the full path to the repository on disk.
        """
        location = os.path.abspath(__file__).rsplit('/', 1)[0]
        location = os.path.join(location, 'repositories/')
        location = os.path.join(location, self.repository)
        return location

    def revert(self):
        """
        Reverts the repository back to it's original state.
        """
        command = 'cd %s && %s' % (self.get_repository(),
                                   self.revert_command)
        proc = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
        proc.communicate()

    def stage(self, file):
        """
        Stages a file
        """
        command = 'cd %s && %s %s' % (self.get_repository(), self.stage_command, file.name)
        proc = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
        proc.communicate()

    def touch(self, fn):
        """
        Creates a new file.
        """
        f = open(fn, 'w')
        f.write('foo')
        f.close()

    def vcprompt(self, environment=False, *args, **kwargs):
        """
        A convenience method for forking out to vcprompt.

        Keyword arguments are treated as option/value pairs to be passed
        to vcprompt.

        Returns the output from the call to vcprompt.
        """
        # unset any environment variables
        for k in os.environ.keys():
            if k.startswith('VCPROMPT'):
                del os.environ[k]

        commands = list(self.commands)
        if 'path' not in kwargs.keys():
            commands += ['--path', self.get_repository()]
        for key, value in kwargs.items():
            key = key.replace('_', '-')
            commands.append("--%s" % key)
            commands.append(value)
        process = Popen(commands, stdout=PIPE)
        output = process.communicate()[0]
        return output.decode("utf-8").strip()


class BaseTest(object):

    def test_format_all(self, string='%s:%n:%r:%h:%b'):
        """
        Tests that all formatting arguments are working correctly.
        """
        output = self.vcprompt(format=string)
        expected = ':'.join([self.data('system'),
                             self.data('system'),
                             self.data('revision'),
                             self.data('hash'),
                             self.data('branch')])
        self.assertEqual(output, expected)

    def test_format_branch(self, string='%b'):
        """
        Tests that the correct branch name is returned.
        """
        output = self.vcprompt(format=string)
        self.assertEqual(output, self.data('branch'))

    def test_format_revision(self, string='%r'):
        """
        Tests that the correct revision ID or hash is returned.
        """
        output = self.vcprompt(format=string)
        self.assertEqual(output, self.data('revision'))

    def test_format_hash(self, string='%h'):
        """
        Tests that the correct hash or revision ID is returned.
        """
        self.assertEqual(self.vcprompt(format=string),
                          self.data('hash'))

    def test_format_modified(self, string='%m'):
        """
        Tests for modified files in the repository.
        """
        output = self.vcprompt(format=string)
        self.assertEqual(output, '')

        f = open(os.path.join(self.get_repository(), 'quotes.txt'), 'w')
        f.write('foo')
        f.close()

        output = self.vcprompt(format=string)
        self.assertEqual(output, '+')

        self.revert()

        output = self.vcprompt(format=string)
        self.assertEqual(output, '')

    def test_format_system(self, string='%s'):
        """
        Tests that the '%s' argument correctly returns the system name.
        """
        output = self.vcprompt(format=string)
        self.assertEqual(output, self.data('system'))

    def test_format_system_alt(self, string='%n'):
        """
        Tests that the '%m' argument correctly returns the system name.
        """
        return self.test_format_system(string=string)

    def test_format_untracked_files(self, string="%u"):
        """
        Tests for any untracked files in the repository.
        """
        output = self.vcprompt(format=string)
        self.assertEqual(output, '')

        file = os.path.join(self.get_repository(), 'untracked_file')
        self.touch(file)

        output = self.vcprompt(format=string)
        self.assertEqual(output, '?')

        os.remove(file)

        output = self.vcprompt(format=string)
        self.assertEqual(output, '')

    def test_format_relative_root(self, string='%P'):
        """
        Tests the '%p' format token (relative root of the repository).
        """
        self.assertEqual(self.vcprompt(format=string), self.repository)

    def test_format_root_directory(self, string='%p'):
        """
        Tests the '%P' format token (root of the repository)
        """
        self.assertEqual(self.vcprompt(format=string), '.')
        path = os.path.join(self.get_repository(), 'foo', 'bar')
        self.assertEqual(self.vcprompt(format=string, path=path), 'foo/bar')

    def test_modified_format_chars(self, string='%m%u'):
        """
        Tests for changing the characters used in
        staged/modified/untracked output.
        """
        chars = {
            'modified': 'm',
            'untracked': 'u',
        }

        if hasattr(self, 'stage_command'):
            string = '%a' + string
            chars['staged'] = 'a'

        output = self.vcprompt(format=string, **chars)
        self.assertEqual(output, '')

        untracked = os.path.join(self.get_repository(), 'untracked_file')
        self.touch(untracked)

        if hasattr(self, 'stage_command'):
            witticism = open(os.path.join(self.get_repository(), 'witticism.txt'), 'w')
            witticism.write('The 100/50 rule: We are 100% responsible and at least'
                '50% to blame\n')
            witticism.close()
            self.stage(witticism)

        quotes = open(os.path.join(self.get_repository(), 'quotes.txt'), 'w')
        quotes.write('foo bar baz\n')
        quotes.close()

        output = self.vcprompt(format=string, **chars)
        self.assertEqual(output, string.replace('%', ''))

        os.remove(untracked)
        self.revert()

        output = self.vcprompt(format=string, **chars)
        self.assertEqual(output, '')


class Bazaar(Base, BaseTest):

    revert_command = 'bzr revert --no-backup'
    repository = 'bzr'


class Darcs(Base, BaseTest):

    revert_command = 'darcs revert -a'
    repository = 'darcs'


class Fossil(Base, BaseTest):

    revert_command = 'fossil revert'
    repository = 'fossil'


class Git(Base, BaseTest):

    revert_command = 'git reset -q --hard HEAD && git clean -f'
    stage_command = 'git add'
    repository = 'git'


class Mercurial(Base, BaseTest):

    revert_command = 'hg revert -a --no-backup'
    repository = 'hg'


class Subversion(Base, BaseTest):

    revert_command = 'svn revert -R .'
    repository = 'svn'

    def test_format_root_directory(self, string='%p'):
        """
        Tests the '%P' format token (root of the repository)
        """
        self.assertEqual(self.vcprompt(format=string), '.')
        # subversion < 1.7 litters every directory with ".svn"
        # directories so either '.' or 'foo/bar' could be correct
        # depending on which version is available.
        # Rather than try to determine which version is installed, we
        # just treat both results as correct
        path = os.path.join(self.get_repository(), 'foo', 'bar')
        self.assertTrue(self.vcprompt(format=string, path=path) in ['.', 'foo/bar'])



if __name__ == '__main__':
    unittest.main()
