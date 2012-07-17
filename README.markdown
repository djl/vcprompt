vcprompt
========

Version control information in your prompt.



INSTALL
-------

Download vcprompt, make it executable and add it to your prompt:

    $ curl -sL https://github.com/djl/vcprompt/raw/master/bin/vcprompt > ~/bin/vcprompt
    $ chmod 755 ~/bin/vcprompt

For bash, you'll want to do something like this:

    $ export PS1='\u@\h:\w \$(vcprompt)\$'

ZSH users should be aware that they will have to set the
`PROMPT_SUBST` option first:

    $ setopt prompt_subst
    $ export PS1='%n@%m:%~ $(vcprompt)$ '



OPTIONS
-------

* `-f, --format FORMAT`

  Passes a custom output format to `vcprompt`. Defaults to `%s:%b`.
  See below for more details.

* `-p, --path PATH`

  The path on which to run `vcprompt`. Defaults to the current
  directory.

* `-d, --max-depth`

  The maximum number of directories `vcprompt` should traverse while
  looking for version control systems.

* `-s, --systems`

  Prints all available version control systems to standard out.

* `-h, --help`

  Prints the help message and exists.

* `-v, --version`

  Prints the current version number and exits.


Each version control system also has it's own formatting option.
The options take the form of `--format-SYSTEM`.
The available options are currently:

* `--format-bzr`
* `--format-cvs`
* `--format-darcs`
* `--format-fossil`
* `--format-git`
* `--format-hg`
* `--format-svn`



FORMATS
-------

`vcprompt` comes with a number of formatting tokens. What follows is a list
of all the available tokens:

* `%s` or `%n`

  The "short name" of the version control system currently in
  use. E.g. `git`, `hg`, `svn`

* `%h`

  The hash of the repository. If no hash is available it will show the
  revision number instead.

* `%r`

  The revision number of the repository. If no revision number is
  available it will return the hash instead.

* `%b`

  The current branch. If branch is available it will be the directory
  where the version control system was first encountered.

* `%m`

  Displays a plus symbol (`+`) if there are any changes (which are not
  staged for commit, in systems that make such a distinction, i.e. git).

* `%a`

  Displays an asterisk (`*`) if there are any changes staged for commit
  (in systems that make such a distinction, i.e. git).

* `%u`

  Displays a question mark (`?`) if there are any untracked files.



REQUIREMENTS
------------

* Python 2.4 or later. Python >= 2.5 recommended.

  Python 2.4 is experimental at best but should work for the most
  part.  Expect it to break or change in the future.

  Use of Python 2.5 or later is recommended.

* Python 3 isn't supported yet but 2to3 produces a tiny diff which
  seems to work.

* Fossil support requires the SQLite3 module to be installed (built in
  on Python 2.5+).



TESTING
-------

To run the tests, use the provided Makefile:

    make test


A few notes on testing:

* Tests have to fetch remote repositories, so network access is required
* Fetching remote repositories requires each VCS to be installed


NOTES
-----

vcprompt was heavily inspired by Greg Ward's original
[implementation][vcprompt] in C.

This version of vcprompt attempts to stay mostly compatible with the
original although there may be some notable differences.

[vcprompt]: http://vc.gerg.ca/hg/vcprompt/
