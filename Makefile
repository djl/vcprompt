help:
	@echo 'Commonly used make targets:'
	@echo '  fetch-repositories   - fetch repositories required for testing'
	@echo '  test                 - run tests'

test:
	@cd tests && python tests.py

revert:
	@cd tests/repositories/bzr && bzr revert --no-backup > /dev/null 2>&1
	@cd tests/repositories/darcs && darcs revert -a > /dev/null 2>&1
	@cd tests/repositories/fossil && fossil revert > /dev/null 2>&1
	@cd tests/repositories/git && git reset -q --hard HEAD > /dev/null 2>&1
	@cd tests/repositories/hg && hg revert -a --no-backup > /dev/null 2>&1
	@cd tests/repositories/svn && svn revert -R . > /dev/null 2>&1

fetch-bzr:
	@echo "Fetching Bazaar repository..."
	@if [ -d tests/repositories/bzr ]; then rm -rf tests/repositories/bzr; fi
	@bzr branch lp:~davidlogie/vcprompt-quotes/trunk tests/repositories/bzr > /dev/null 2>&1

fetch-darcs:
	@echo "Fetching Darcs repository..."
	@if [ -d tests/repositories/darcs ]; then rm -rf tests/repositories/darcs; fi
	@darcs get http://patch-tag.com/r/davidlogie/quotes tests/repositories/darcs > /dev/null 2>&1

fetch-git:
	@echo "Fetching Git repository..."
	@git submodule update --init > /dev/null 2>&1

fetch-hg:
	@echo "Fetching Mercurial repository..."
	@if [ -d tests/repositories/hg ]; then rm -rf tests/repositories/hg; fi
	@hg clone https://bitbucket.org/xvzf/quotes tests/repositories/hg > /dev/null 2>&1

fetch-svn:
	@echo "Fetching out SVN repository..."
	@if [ -d tests/repositories/svn ]; then rm -rf tests/repositories/svn; fi
	@svn checkout http://svn.github.com/xvzf/quotes.git tests/repositories/svn > /dev/null 2>&1

fetch-repositories: fetch-bzr fetch-darcs fetch-git fetch-hg fetch-svn

update-bzr:
	@echo "Updating Bazaar repository..."
	@cd tests/repositories/bzr && bzr pull > /dev/null 2>&1

update-darcs:
	@echo "Updating Darcs repository..."
	@cd tests/repositories/darcs && darcs pull -a > /dev/null 2>&1

update-git:
	@echo "Updating Git repository..."
	@git submodule update > /dev/null 2>&1

update-hg:
	@echo "Updating Mercurial repository..."
	@cd tests/repositories/hg && hg pull -u

update-svn:
	@echo "Updating SVN repository..."
	@cd tests/repositories/svn && svn up

update-repositories: update-bzr update-darcs update-git update-hg update-svn

.PHONY: help test $(wildcard fetch-*) $(wildcard update-*)
