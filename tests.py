from __future__ import with_statement
import os
import sys
import subprocess
import unittest


class Base(unittest.TestCase):
    def repo(self, vcs):
        location = os.path.abspath(__file__).rsplit('/', 1)[0]
        location = os.path.join(location, 'tests/repositories/')
        location = os.path.join(location, vcs)
        return location

    def unknown(self):
        process = subprocess.Popen('./bin/vcprompt --values UNKNOWN'.split(),
                                   stdout=subprocess.PIPE)
        output = process.communicate()[0].strip()
        return output

    def vcprompt(self, *args, **kwargs):
        commands = ['./bin/vcprompt', '--path', self.repository]
        for key, value in kwargs.items():
            key = key.replace('_', '-')
            commands.append("--%s" % key)
            commands.append(value)
        process = subprocess.Popen(commands, stdout=subprocess.PIPE)
        return process.communicate()[0]


class Bazaar(Base):
    def setUp(self):
        self.repository = self.repo('bzr')

    def test_format_branch(self, string='%b'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, 'bzr')

    def test_format_revision(self, string='%r'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, '1')

    def test_format_hash(self, string='%h'):
        self.test_format_revision(string)

    def test_format_system(self, string='%s'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, 'bzr')

    def test_format_all(self, string='%s:%r'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, 'bzr:1')


class Darcs(Base):
    def setUp(self):
        self.repository = self.repo('darcs')

    def test_format_branch(self, string='%b'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, 'darcs')

    def test_format_revision(self, string='%r'):
        return self.test_format_hash(string)

    def test_format_hash(self, string='%h'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, '4b13fbf')

    def test_format_system(self, string='%s'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, 'darcs')

    def test_format_all(self, string='%s:%b:%r'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, 'darcs:darcs:4b13fbf')


class Fossil(Base):
    def setUp(self):
        self.repository = self.repo('fossil')
        self.repository_file = 'fossil'
        self.repository_db = os.path.join(self.repository,
                                          '_FOSSIL')
        if not self.is_open():
            self.open()

    def tearDown(self):
        if self.is_open():
            self.close()

    def is_open(self):
        return os.path.exists(self.repository_db)

    def open(self):
        with open('/dev/null', 'w') as devnull:
            command = "cd %s && fossil open %s" % (self.repository,
                                                   self.repository_file)
            subprocess.Popen(command, shell=True, stdout=devnull,
                             stderr=devnull)

    def close(self):
        with open('/dev/null', 'w') as devnull:
            command = "cd %s && fossil close" % self.repository
            subprocess.Popen(command, shell=True, stdout=devnull,
                             stderr=devnull)

    def test_format_system(self, string='%s'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, 'fossil')

    def test_format_branch(self, string='%b'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, 'trunk')

    def test_format_hash(self, string='%h'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, '4103d09')

    def test_format_revision(self, string='%r'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, '4103d09')


class Git(Base):
    def setUp(self):
        self.repository = self.repo('git')

    def test_format_branch(self, string='%b'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, 'master')

    def test_format_revision(self, string='%r'):
        return self.test_format_hash(string)

    def test_format_hash(self, string='%h'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, 'eae51cf')

    def test_format_system(self, string='%s'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, 'git')

    def test_format_all(self, string='%s:%b:%r'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, 'git:master:eae51cf')


class Mercurial(Base):
    def setUp(self):
        self.repository = self.repo('hg')

    def test_format_branch(self, string="%b"):
        output = self.vcprompt(format=string)
        self.assertEquals(output, 'default')

    def test_format_revision(self, string="%r"):
        output = self.vcprompt(format=string)
        self.assertEquals(output, '0')

    def test_format_hash(self, string="%h"):
        output = self.vcprompt(format=string)
        self.assertEquals(output, '8ada0a9')

    def test_format_system(self, string="%s"):
        output = self.vcprompt(format=string)
        self.assertEquals(output, 'hg')

    def test_format_all(self, string='%s:%b:r%r:%h'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, 'hg:default:r0:8ada0a9')


class Subversion(Base):
    def setUp(self):
        self.repository = self.repo('svn')

    def test_format_branch(self, string="%b"):
        output = self.vcprompt(format=string)
        self.assertEquals(output, self.unknown())

    def test_format_revision(self, string='%r'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, '0')

    def test_format_hash(self, string='%h'):
        return self.test_format_revision(string)

    def test_format_system(self, string='%s'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, 'svn')

    def test_format_all(self, string='%s:%b:%h'):
        output = self.vcprompt(format=string)
        self.assertEquals(output, "svn:%s:0" % self.unknown())


if __name__ == '__main__':
    unittest.main()
