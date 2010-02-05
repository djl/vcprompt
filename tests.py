import os
import unittest
import vcprompt


class Base(unittest.TestCase):
    def repo(self, vcs):
        return './tests/repositories/%s' % vcs


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


if __name__ == '__main__':
    unittest.main()
