import commands
from distutils.core import setup

setup(
    name='vcprompt',
    version=commands.getoutput('./bin/vcprompt --version'),
    author='David Logie',
    author_email='david@davidlogie.com',
    url='http://github.com/xvzf/vcprompt',
    scripts=['bin/vcprompt'],
    license='LICENSE',
    description='Version control information in your prompt (or anywhere!).',
    long_description=open('README').read(),
)
