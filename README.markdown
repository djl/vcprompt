vcprompt
========

Version control information in your prompt.

Heavily inspired by Greg Ward's [vcprompt][vcprompt]

[vcprompt]: http://vc.gerg.ca/hg/vcprompt/



Installing
----------

Download vcprompt, make it executable and add it to your prompt:

    $ curl -sL https://github.com/xvzf/vcprompt/raw/master/bin/vcprompt > ~/bin/vcprompt
    $ chmod 755 ~/bin/vcprompt
    $ export PS1="$(vcprompt) $PS1"



Basic customizing
-----------------

`vcprompt`'s output can be customized to your liking by using the
`-f/--format` option. For example:

    $ vcprompt --format "%s:%b"


If not given, the formatting string defaults to `%s:%b`, that is the
current system and the branch. For example:

    git:master


A partial list of arguments are as follows:

* `%s` - the VCS system in use
* `%r` - the current revision (or hash if no revision number is present)
* `%h` - the current hash (or revision number if no hash is present)
* `%b` - the current branch name (or directory where the repository exists)
* `%m` - shows "+" if a file has been modified
* `%u` - shows "?" if any untracked files are present



Requirements
------------

* Python 2.4+
* Python 3.0+ (with 2to3)

Warning! Python 2.4 is experimental at best but should work for the most part.
Expect it to break or change in the future.

Fossil support requires the SQLite3 module to be installed (built in on
Python 2.5+).


Testing
-------

To run the tests, use the provided Makefile:

    make test


A few notes on testing:

* Tests have to fetch remote repositories, so network access is required
* Fetching remote repositories requires each VCS to be installed
