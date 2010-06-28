help:
	@echo 'Commonly used make targets:'
	@echo '  fetch-repositories   - fetch repositories required for testing'
	@echo '  test                 - run tests'

fetch-git:
	@echo "Cloning Git repository..."
	@git submodule update --init > /dev/null 2>&1

fetch-bzr:
	@echo "Branching Bazaar repository..."
	@if [ -d tests/repositories/bzr ]; then rm -rf tests/repositories/bzr; fi
	@bzr branch lp:~davidlogie/vcprompt-quotes/trunk tests/repositories/bzr > /dev/null 2>&1

fetch-hg:
	@echo "Cloning Mercurial repository..."
	@if [ -d tests/repositories/hg ]; then rm -rf tests/repositories/hg; fi
	@hg clone http://xvzf@bitbucket.org/xvzf/quotes tests/repositories/hg > /dev/null 2>&1

fetch-svn:
	@echo "Checking out SVN repository..."
	@if [ -d tests/repositories/svn ]; then rm -rf tests/repositories/svn; fi
	@svn checkout http://svn.github.com/xvzf/quotes.git tests/repositories/svn > /dev/null 2>&1

fetch-repositories: fetch-bzr fetch-git fetch-hg fetch-svn

test:
	@cd tests && python tests.py

.PHONY: fetch-bzr fetch-git fetch-hg fetch-svn fetch-repositories help test
