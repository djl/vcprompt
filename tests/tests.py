#!/usr/bin/env python
from __future__ import with_statement
import os
import re
import sys
import subprocess
import unittest


class Base(unittest.TestCase):

    commands = ['../bin/vcprompt', '--without-environment']

    def file(self, path):
        file = os.path.join(self.repository, path)
        return file

    def repo(self, vcs):
        location = os.path.abspath(__file__).rsplit('/', 1)[0]
        location = os.path.join(location, 'repositories/')
        location = os.path.join(location, vcs)
        return location

    def unknown(self):
        commands = Base.commands + ['--values', 'UNKNOWN']
        process = subprocess.Popen(commands, stdout=subprocess.PIPE)
        output = process.communicate()[0].strip()
        return output

    def vcprompt(self, environment=False, *args, **kwargs):
        commands = Base.commands + ['--path', self.repository]
        for key, value in kwargs.items():
            key = key.replace('_', '-')
            commands.append("--%s" % key)
            commands.append(value)
        process = subprocess.Popen(commands, stdout=subprocess.PIPE)
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


class Bazaar(Base, BaseTest):

    def revision(self):
        with open(self.file('.bzr/branch/last-revision'), 'r') as f:
            for line in f:
                return line.strip().split()[0]

    def setUp(self):
        self.repository = self.repo('bzr')

    def test_format_branch(self, string='%b'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, 'bzr')

    def test_format_revision(self, string='%r'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, self.revision())

    def test_format_hash(self, string='%h'):
        with open(self.file('.bzr/branch/last-revision'), 'r') as f:
            for line in f:
                return line.strip().rsplit('-', 1)[0][:7]

    def test_format_system(self, string='%s'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, 'bzr')

    def test_format_all(self, string='%s:%r'):
        output = self.vcprompt(format=string)
        expected = 'bzr:%s' % (self.revision())
        self.assertEquals(output, expected)


class Darcs(Base, BaseTest):

    def hash(self):
        with open(self.file('_darcs/hashed_inventory'), 'r') as f:
            for line in f:
                return line.strip().split('\n')[0].split('-')[-1][:7]

    def setUp(self):
        self.repository = self.repo('darcs')

    def test_format_branch(self, string='%b'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, 'darcs')

    def test_format_revision(self, string='%r'):
        return self.test_format_hash(string)

    def test_format_hash(self, string='%h'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, self.hash())

    def test_format_system(self, string='%s'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, 'darcs')

    def test_format_all(self, string='%s:%b:%r'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, 'darcs:darcs:%s' % self.hash())


class Fossil(Base, BaseTest):

    def hash(self):
        with open(self.file('manifest.uuid'), 'r') as f:
            for line in f:
                return line.strip()[:7]

    def setUp(self):
        self.repository = self.repo('fossil')
        self.repository_file = 'fossil'
        self.open()

    def tearDown(self):
        self.close()

    def open(self):
        with open('/dev/null', 'w') as devnull:
            command = "cd %s && fossil open %s" % (self.repository,
                                                   self.repository_file)
            subprocess.Popen(command, shell=True, stdout=devnull,
                             stderr=devnull)

    def close(self):
        command = "cd %s && fossil close" % self.repository
        subprocess.Popen(command, shell=True)

    def test_format_system(self, string='%s'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, 'fossil')

    def test_format_branch(self, string='%b'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, 'trunk')

    def test_format_hash(self, string='%h'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, self.hash())

    def test_format_revision(self, string='%r'):
        return self.test_format_hash(string=string)


class Git(Base, BaseTest):

    def _hash_or_branch(self, get='hash'):
        branch = hash = self.unknown()
        # get the branch name
        with open(os.path.join(self.repository, '.git/HEAD'), 'r') as f:
            for line in f:
                if re.match('^ref', line):
                    branch = line.strip().split('/')[-1]
                    break

        # open the branch file, grab the hash
        if branch != self.unknown():
            with open(self.file('.git/refs/heads/%s' % branch), 'r') as bf:
                for bfline in bf:
                    hash = bfline.strip()[:7]
                    break
        return locals()[get]

    def branch(self):
        return self._hash_or_branch('branch')

    def hash(self):
        return self._hash_or_branch('hash')

    def setUp(self):
        self.repository = self.repo('git')

    def test_format_branch(self, string='%b'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, self.branch())

    def test_format_revision(self, string='%r'):
        return self.test_format_hash(string)

    def test_format_hash(self, string='%h'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, self.hash())

    def test_format_system(self, string='%s'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, 'git')

    def test_format_all(self, string='%s:%b:%r'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, 'git:%s:%s' % (self.branch(),
                                                 self.hash()))


class Mercurial(Base, BaseTest):

    def _branch_hash_revision(self, get='branch'):
        count = 0
        with open(self.file('.hg/branchheads.cache'), 'r') as f:
            for line in f:
                line = line.strip()
                hash, revision_branch = line.split()
                hash = hash[:7]
                if count > 0:
                    branch = revision_branch
                else:
                    revision = revision_branch
                count += 1
            return locals()[get]

    def branch(self):
        return self._branch_hash_revision('branch')

    def hash(self):
        return self._branch_hash_revision('hash')

    def revision(self):
        return self._branch_hash_revision('revision')

    def setUp(self):
        self.repository = self.repo('hg')

    def test_format_branch(self, string="%b"):
        output = self.vcprompt(format=string)
        self.assertEquals(output, 'default')

    def test_format_revision(self, string="%r"):
        output = self.vcprompt(format=string)
        self.assertEquals(output, self.revision())

    def test_format_hash(self, string="%h"):
        output = self.vcprompt(format=string)
        self.assertEquals(output, self.hash())

    def test_format_system(self, string="%s"):
        output = self.vcprompt(format=string)
        self.assertEquals(output, 'hg')

    def test_format_all(self, string='%s:%b:%r:%h'):
        output = self.vcprompt(format=string)
        expected = 'hg:%s:%s:%s' % (self.branch(),
                                    self.revision(),
                                    self.hash())
        self.assertEquals(output, expected)


class Subversion(Base, BaseTest):

    def setUp(self):
        self.repository = self.repo('svn')

    def test_depth_limited(self):
        return self.test_depth()

    def test_format_branch(self, string="%b"):
        output = self.vcprompt(format=string)
        self.assertEquals(output, self.unknown())

    def test_format_revision(self, string='%r'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, '2')

    def test_format_hash(self, string='%h'):
        return self.test_format_revision(string)

    def test_format_system(self, string='%s'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, 'svn')

    def test_format_all(self, string='%s:%b:%h'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, "svn:%s:2" % self.unknown())


if __name__ == '__main__':
    unittest.main()
