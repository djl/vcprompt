from __future__ import with_statement
import os
import sys
import subprocess
import unittest
import vcprompt


class Base(unittest.TestCase):
    def repo(self, vcs):
        location = os.path.abspath(__file__).rsplit('/', 1)[0]
        location = os.path.join(location, 'tests/repositories/')
        location = os.path.join(location, vcs)
        return location


class TestGit(Base):
    def setUp(self):
        self.repository = self.repo('git')

    def test_format_branch(self, string='%b'):
        string = vcprompt.vcprompt(self.repository, string)
        self.assertEquals(string, 'master')

    def test_format_revision(self, string='%r'):
        return self.test_format_hash(string)

    def test_format_hash(self, string='%h'):
        string = vcprompt.vcprompt(self.repository, string)
        self.assertEquals(string, 'eae51cf')

    def test_format_system(self, string='%s'):
        string = vcprompt.vcprompt(self.repository, string)
        self.assertEquals(string, 'git')

    def test_format_all(self, string='%s:%b:%r'):
        string = vcprompt.vcprompt(self.repository, string)
        self.assertEquals(string, 'git:master:eae51cf')


class TestMecurial(Base):
    def setUp(self):
        self.repository = self.repo('hg')

    def test_format_branch(self, string="%b"):
        string = vcprompt.vcprompt(self.repository, string)
        self.assertEquals(string, 'default')

    def test_format_revision(self, string="%r"):
        string = vcprompt.vcprompt(self.repository, string)
        self.assertEquals(string, '0')

    def test_format_hash(self, string="%h"):
        string = vcprompt.vcprompt(self.repository, string)
        self.assertEquals(string, '8ada0a9')

    def test_format_system(self, string="%s"):
        string = vcprompt.vcprompt(self.repository, string)
        self.assertEquals(string, 'hg')

    def test_format_all(self, string='%s:%b:r%r:%h'):
        string = vcprompt.vcprompt(self.repository, string)
        self.assertEquals(string, 'hg:default:r0:8ada0a9')


class TestBazaar(Base):
    def setUp(self):
        self.repository = self.repo('bzr')

    def test_format_branch(self, string='%b'):
        string = vcprompt.vcprompt(self.repository, string)
        self.assertEquals(string, 'bzr')

    def test_format_revision(self, string='%r'):
        string = vcprompt.vcprompt(self.repository, string)
        self.assertEquals(string, '1')

    def test_format_hash(self, string='%h'):
        # bzr doesn't seem to have a concept of 'global' hash/identifier
        # just return ``test_format_revision`` for now
        self.test_format_revision(string)

    def test_format_system(self, string='%s'):
        string = vcprompt.vcprompt(self.repository, string)
        self.assertEquals(string, 'bzr')

    def test_format_all(self, string='%s:%r'):
        string = vcprompt.vcprompt(self.repository, string)
        self.assertEquals(string, 'bzr:1')



class TestSubversion(Base):
    def setUp(self):
        self.repository = self.repo('svn')

    def test_format_branch(self, string="%b"):
        string = vcprompt.vcprompt(self.repository, string)
        self.assertEquals(string, vcprompt.UNKNOWN)

    def test_format_revision(self, string='%r'):
        string = vcprompt.vcprompt(self.repository, string)
        self.assertEquals(string, '0')

    def test_format_hash(self, string='%h'):
        return self.test_format_revision(string)

    def test_format_system(self, string='%s'):
        string = vcprompt.vcprompt(self.repository, string)
        self.assertEquals(string, 'svn')

    def test_format_all(self, string='%s:%b:%h'):
        string = vcprompt.vcprompt(self.repository, string)
        self.assertEquals(string, "svn:%s:0" % vcprompt.UNKNOWN)


class TestFossil(Base):
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
        string = vcprompt.vcprompt(self.repository, string)
        self.assertEquals(string, 'fossil')

    def test_format_branch(self, string='%b'):
        string = vcprompt.vcprompt(self.repository, string)
        self.assertEquals(string, 'trunk')

    def test_format_hash(self, string='%h'):
        string = vcprompt.vcprompt(self.repository, string)
        self.assertEquals(string, '4103d09')

    def test_format_revision(self, string='%r'):
        string = vcprompt.vcprompt(self.repository, string)
        self.assertEquals(string, '4103d09')


if __name__ == '__main__':
    unittest.main()
