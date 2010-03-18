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
        process = subprocess.Popen('./bin/vcprompt --values unknown'.split(),
                                stdout=subprocess.PIPE)
        output = process.communicate()[0].strip()
        return output

    def vcprompt(self, path, string):
        command = './bin/vcprompt --path %s --format %s' % (path, string)
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        return process.communicate()[0]


class Bazaar(Base):
    def setUp(self):
        self.repository = self.repo('bzr')

    def test_format_branch(self, string='%b'):
        string = self.vcprompt(self.repository, string)
        self.assertEquals(string, 'bzr')

    def test_format_revision(self, string='%r'):
        string = self.vcprompt(self.repository, string)
        self.assertEquals(string, '1')

    def test_format_hash(self, string='%h'):
        self.test_format_revision(string)

    def test_format_system(self, string='%s'):
        string = self.vcprompt(self.repository, string)
        self.assertEquals(string, 'bzr')

    def test_format_all(self, string='%s:%r'):
        string = self.vcprompt(self.repository, string)
        self.assertEquals(string, 'bzr:1')


class Darcs(Base):
    def setUp(self):
        self.repository = self.repo('darcs')

    def test_format_branch(self, string='%b'):
        string = self.vcprompt(self.repository, string)
        self.assertEquals(string, 'darcs')

    def test_format_revision(self, string='%r'):
        return self.test_format_hash(string)

    def test_format_hash(self, string='%h'):
        string = self.vcprompt(self.repository, string)
        self.assertEquals(string, '4b13fbf')

    def test_format_system(self, string='%s'):
        string = self.vcprompt(self.repository, string)
        self.assertEquals(string, 'darcs')

    def test_format_all(self, string='%s:%b:%r'):
        string = self.vcprompt(self.repository, string)
        self.assertEquals(string, 'darcs:darcs:4b13fbf')


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
        string = self.vcprompt(self.repository, string)
        self.assertEquals(string, 'fossil')

    def test_format_branch(self, string='%b'):
        string = self.vcprompt(self.repository, string)
        self.assertEquals(string, 'trunk')

    def test_format_hash(self, string='%h'):
        string = self.vcprompt(self.repository, string)
        self.assertEquals(string, '4103d09')

    def test_format_revision(self, string='%r'):
        string = self.vcprompt(self.repository, string)
        self.assertEquals(string, '4103d09')


class Git(Base):
    def setUp(self):
        self.repository = self.repo('git')

    def test_format_branch(self, string='%b'):
        string = self.vcprompt(self.repository, string)
        self.assertEquals(string, 'master')

    def test_format_revision(self, string='%r'):
        return self.test_format_hash(string)

    def test_format_hash(self, string='%h'):
        string = self.vcprompt(self.repository, string)
        self.assertEquals(string, 'eae51cf')

    def test_format_system(self, string='%s'):
        string = self.vcprompt(self.repository, string)
        self.assertEquals(string, 'git')

    def test_format_all(self, string='%s:%b:%r'):
        string = self.vcprompt(self.repository, string)
        self.assertEquals(string, 'git:master:eae51cf')


class Mercurial(Base):
    def setUp(self):
        self.repository = self.repo('hg')

    def test_format_branch(self, string="%b"):
        string = self.vcprompt(self.repository, string)
        self.assertEquals(string, 'default')

    def test_format_revision(self, string="%r"):
        string = self.vcprompt(self.repository, string)
        self.assertEquals(string, '0')

    def test_format_hash(self, string="%h"):
        string = self.vcprompt(self.repository, string)
        self.assertEquals(string, '8ada0a9')

    def test_format_system(self, string="%s"):
        string = self.vcprompt(self.repository, string)
        self.assertEquals(string, 'hg')

    def test_format_all(self, string='%s:%b:r%r:%h'):
        string = self.vcprompt(self.repository, string)
        self.assertEquals(string, 'hg:default:r0:8ada0a9')


class Subversion(Base):
    def setUp(self):
        self.repository = self.repo('svn')

    def test_format_branch(self, string="%b"):
        string = self.vcprompt(self.repository, string)
        self.assertEquals(string, self.unknown())

    def test_format_revision(self, string='%r'):
        string = self.vcprompt(self.repository, string)
        self.assertEquals(string, '0')

    def test_format_hash(self, string='%h'):
        return self.test_format_revision(string)

    def test_format_system(self, string='%s'):
        string = self.vcprompt(self.repository, string)
        self.assertEquals(string, 'svn')

    def test_format_all(self, string='%s:%b:%h'):
        string = self.vcprompt(self.repository, string)
        self.assertEquals(string, "svn:%s:0" % self.unknown())


if __name__ == '__main__':
    unittest.main()
