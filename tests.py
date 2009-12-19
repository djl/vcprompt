import os
import unittest
import vcprompt

def repo(vcs):
    return './tests/repositories/%s' % vcs

class TestGit(unittest.TestCase):
    def test_format_branch(self):
        string = vcprompt.vcprompt(path=repo('git'), string="%b")
        self.assertEquals(string, 'master')

    def test_format_revision(self):
        # revision == hash
        return self.test_format_hash()

    def test_format_hash(self):
        string = vcprompt.vcprompt(path=repo('git'), string='%r')
        self.assertEquals(string, 'eae51cf')

    def test_format_system(self):
        string = vcprompt.vcprompt(path=repo('git'), string='%s')
        self.assertEquals(string, 'git')


class TestMecurial(unittest.TestCase):
    def test_format_branch(self):
        pass

    def test_format_revision(self):
        pass

    def test_format_hash(self):
        pass


class TestBazaar(unittest.TestCase):
    def test_format_branch(self):
        pass

    def test_format_revision(self):
        pass

    def test_format_hash(self):
        pass


class TestSubversion(unittest.TestCase):
    def test_format_branch(self):
        pass

    def test_format_revision(self):
        pass

    def test_format_hash(self):
        return self.test_format_revision()


if __name__ == '__main__':
    unittest.main()

