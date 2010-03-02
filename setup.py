"""
vcprompt
========

vcprompt is a small utility for displaying information about
version control repositories in your prompt (or anywhere).


Features
--------

vcprompt is aware of the following version control systems:

- Bazaar
- CVS
- Darcs
- Fossil
- Git
- Mercurial
- Subversion
"""
import commands
from distutils.core import setup

setup(
    name='vcprompt',
    version=commands.getoutput('./bin/vcprompt --version'),
    author='David Logie',
    author_email='david@davidlogie.com',
    url='http://github.com/xvzf/vcprompt',
    scripts=['bin/vcprompt'],
    license='BSD',
    description='Version control information in your prompt (or anywhere!).',
    long_description=__doc___,
    classifiers=[
        'Development Status :: 3 - Alpha'
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Version Control',
      ],
)
