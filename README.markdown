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

* `-s, --systems`

  Prints all available version control systems to standard out.

* `-t, --timeout`

  The maximum execution time in milliseconds.

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

You can customise the status symbols used with the following options:

* `-A, --staged`

  The symbol to print when changes have been staged. Defaults to `*`

* `-M, --modified`

  The symbol to print when files have been modified. Defaults to `+`

* `-U, --untracked`

  The symbol to print when there are untracked files. Defaults to `?`



FORMATS
-------

`vcprompt` comes with a number of formatting tokens. What follows is a
list of all the available tokens:

* `%s`, `%n`

  The "short name" of the version control system currently in
  use. E.g. `git`, `hg`, `svn`

* `%h`

  The hash of the repository. If no hash is available it will show the
  revision number instead.

* `%r`

  The revision number of the repository. If no revision number is
  available it will return the hash instead.

* `%b`

  The current branch (or basename of the repository if the branch name
  is unavailable).

* `%m`

  Displays a plus symbol (`+`) if there are any changes (which are not
  staged for commit, in systems that make such a distinction, i.e. git).

* `%a`

  Displays an asterisk (`*`) if there are any changes staged for commit
  (in systems that make such a distinction, i.e. git).

* `%u`

  Displays a question mark (`?`) if there are any untracked files.

* `%P`

  The name of the repository root directory (typically a project name).

* `%p`

  The relative path from the repository root directory to the current
  directory (or the directory specified by `--path`).



HACKING
-------

Before adding new functionality, think about whether this really needs
to be part of vcprompt. A good rule of thumb would be if the new
functionality is specific to a single VCS or is otherwise complex then
it probably doesn't belong in vcprompt.

If you still think your new feature is a good fit then try to follow
these guidelines:

* Confirm *all* existing tests pass
* Add tests for any new functionality
* If you've added a new feature document it in the README and docstring
* Do not update the version number



REQUIREMENTS
------------

* Python 2.4 or later (including Python 3).

* Support for Subversion >= 1.7 and Fossil requires the SQLite3 Python
  module to be installed (built in on Python 2.5+).



NOTES
-----

vcprompt was heavily inspired by Greg Ward's original
[implementation][vcprompt] in C.

This version of vcprompt attempts to stay mostly compatible with the
original although there may be some notable differences.

[vcprompt]: http://vc.gerg.ca/hg/vcprompt/
