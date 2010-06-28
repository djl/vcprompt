help:
	@echo 'Commonly used make targets:'
	@echo '  fetch-repositories   - fetch repositories required for testing'
	@echo '  test                 - run tests'

fetch-repositories:
	@echo "Updating Git submodules..."
	@git submodule update --init
	@echo "Checking out SVN repository"
	@[ -d tests/repositories/svn ] && rm -rf tests/repositories/svn
	@svn checkout http://svn.github.com/xvzf/quotes.git tests/repositories/svn
	@echo "Cloning Mercurial repository"
	@[ -d tests/repositories/hg ] && rm -rf tests/repositories/hg
	@hg clone http://xvzf@bitbucket.org/xvzf/quotes tests/repositories/hg

test: fetch-repositories
	@cd tests && python tests.py

.PHONY: fetch-repositories help test
