#!/usr/bin/env python
from subprocess import Popen, PIPE
import ConfigParser
import os
import re
import sys
import unittest


class Base(unittest.TestCase):

    commands = ['../bin/vcprompt', '--without-environment']

    def __init__(self, *args, **kwargs):
        self.cfg = ConfigParser.ConfigParser()
        self.cfg.read('tests.cfg')
        super(Base, self).__init__(*args, **kwargs)

    def config(self, field):
        return self.cfg.get(self.__class__.__name__.lower(), field)

    def file(self, path):
        file = os.path.join(self.repository, path)
        return file

    def repo(self, vcs):
        location = os.path.abspath(__file__).rsplit('/', 1)[0]
        location = os.path.join(location, 'repositories/')
        location = os.path.join(location, vcs)
        return location

    def revert(self):
        command = 'cd %s && %s' % (self.repository,
                                   self.revert_command)
        Popen(command, stdout=PIPE, stderr=PIPE, shell=True)

    def touch(self, file):
        try:
            try:
                f = open(file, 'w')
            except IOError:
                pass
        finally:
            f.close()

    def unknown(self):
        commands = self.commands + ['--values', 'UNKNOWN']
        process = Popen(commands, stdout=PIPE)
        output = process.communicate()[0].strip()
        return output

    def vcprompt(self, environment=False, *args, **kwargs):
        commands = Base.commands + ['--path', self.repository]
        for key, value in kwargs.items():
            key = key.replace('_', '-')
            commands.append("--%s" % key)
            commands.append(value)
        process = Popen(commands, stdout=PIPE)
        return process.communicate()[0].strip()



class BaseTest(object):

    def test_depth(self, path='foo/bar/baz', depth='0', format='%s'):
        path = os.path.join(self.repository, path)
        output = self.vcprompt(path=path, max_depth=depth, format=format)
        self.assertEquals(output, self.repository.rsplit('/')[-1])

    def test_depth_limited(self, path='foo/bar/baz', depth='2'):
        path = os.path.join(self.repository, path)
        output = self.vcprompt(path=path, max_depth=depth)
        self.assertEquals(output, '')

    def test_format_all(self, string='%s:%n:%r:%h:%b'):
        output = self.vcprompt(format=string)
        expected = ':'.join([self.config('system'),
                             self.config('system'),
                             self.config('revision'),
                             self.config('hash'),
                             self.config('branch')])
        self.assertEquals(output, expected)

    def test_format_branch(self, string='%b'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, self.config('branch'))

    def test_format_revision(self, string='%r'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, self.config('revision'))

    def test_format_hash(self, string='%h'):
        self.assertEquals(self.vcprompt(format=string),
                          self.config('hash'))

    def test_format_modified(self, string='%m'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, '')

        try:
            try:
                f = open(self.file('quotes.txt'), 'a')
                f.write('foo')
            except IOError:
                self.fail()
        finally:
            f.close()

        output = self.vcprompt(format=string)
        self.assertEquals(output, '+')

        self.revert()

        output = self.vcprompt(format=string)
        self.assertEquals(output, '')


    def test_format_system(self, string='%s'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, self.config('system'))

    def test_format_system_alt(self, string='%n'):
        return self.test_format_system(string=string)

    def test_format_untracked_files(self, string="%u"):
        output = self.vcprompt(format=string)
        self.assertEquals(output, '')

        file = self.file('untracked_file')
        self.touch(file)

        output = self.vcprompt(format=string)
        self.assertEquals(output, '?')

        os.remove(file)

        output = self.vcprompt(format=string)
        self.assertEquals(output, '')


class Bazaar(Base, BaseTest):

    revert_command = 'bzr revert --no-backup'

    def setUp(self):
        self.repository = self.repo('bzr')



class Darcs(Base, BaseTest):

    revert_command = 'darcs revert -a'

    def setUp(self):
        self.repository = self.repo('darcs')


class Fossil(Base, BaseTest):

    revert_command = 'fossil revert'

    def setUp(self):
        self.repository = self.repo('fossil')
        self.repository_file = 'fossil'


class Git(Base, BaseTest):

    revert_command = 'git reset -q --hard HEAD'

    def setUp(self):
        self.repository = self.repo('git')


class Mercurial(Base, BaseTest):

    revert_command = 'hg revert -a --no-backup'

    def setUp(self):
        self.repository = self.repo('hg')


class Subversion(Base, BaseTest):

    revert_command = 'svn revert -R .'

    def setUp(self):
        self.repository = self.repo('svn')

    def test_depth_limited(self):
        return self.test_depth()


if __name__ == '__main__':
    unittest.main()
