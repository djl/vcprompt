SHELL  := bash
stdout := /dev/null

help:
	@echo 'Commonly used make targets:'
	@echo '  fetch-repositories   - fetch repositories required for testing'
	@echo '  test                 - run tests'

test: run_tests clean

run_tests:
	@cd tests && python tests.py

clean:
	-@cd tests/repositories/bzr && bzr revert --no-backup &>$(stdout)
	-@cd tests/repositories/darcs && darcs revert -a &>$(stdout)
	-@cd tests/repositories/fossil && fossil revert &>$(stdout)
	-@cd tests/repositories/git && [[ -d .git ]] && git reset -q --hard HEAD &>$(stdout)
	-@cd tests/repositories/hg && hg revert -a --no-backup &>$(stdout)
	-@cd tests/repositories/svn && svn revert -R . &>$(stdout)
	-@find . -name untracked_file | xargs rm

fetch-bzr:
	@echo "Fetching Bazaar repository..."
	@if [ -d tests/repositories/bzr ]; then rm -rf tests/repositories/bzr; fi
	@bzr branch lp:vcprompt-quotes tests/repositories/bzr &>$(stdout)

fetch-darcs:
	@echo "Fetching Darcs repository..."
	@if [ -d tests/repositories/darcs ]; then rm -rf tests/repositories/darcs; fi
	@darcs get http://darcs.djl.im/quotes tests/repositories/darcs &>$(stdout)

fetch-fossil:
	@echo "Fetching Fossil repository..."
	@cd tests/repositories/fossil && fossil open fossil &>$(stdout)

fetch-git:
	@echo "Fetching Git repository..."
	@git submodule update --init &>$(stdout)
	@cd tests/repositories/git && git checkout master &>$(stdout)

fetch-hg:
	@echo "Fetching Mercurial repository..."
	@if [ -d tests/repositories/hg ]; then rm -rf tests/repositories/hg; fi
	@hg clone https://bitbucket.org/xvzf/quotes tests/repositories/hg &>$(stdout)

fetch-svn:
	@echo "Fetching out SVN repository..."
	@if [ -d tests/repositories/svn ]; then rm -rf tests/repositories/svn; fi
	@svn checkout http://svn.github.com/djl/quotes.git tests/repositories/svn &>$(stdout)

fetch-repositories: fetch-bzr fetch-darcs fetch-fossil fetch-git fetch-hg fetch-svn

update-bzr:
	@echo "Updating Bazaar repository..."
	@cd tests/repositories/bzr && bzr pull &>$(stdout)

update-darcs:
	@echo "Updating Darcs repository..."
	@cd tests/repositories/darcs && darcs pull -a &>$(stdout)

update-git:
	@echo "Updating Git repository..."
	@git submodule update &>$(stdout)

update-hg:
	@echo "Updating Mercurial repository..."
	@cd tests/repositories/hg && hg pull -u

update-svn:
	@echo "Updating SVN repository..."
	@cd tests/repositories/svn && svn up

update-repositories: update-bzr update-darcs update-git update-hg update-svn

build-docs:
	@cd man && find . -name \*.ronn | xargs ronn -b --roff

.PHONY: clean help run_tests test $(wildcard fetch-*) $(wildcard update-*) build-docs
