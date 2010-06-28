help:
	@echo 'Commonly used make targets:'
	@echo '  fetch-repositories   - fetch repositories required for testing'
	@echo '  test                 - run tests'

fetch-submodules:
	@echo "Updating Git submodules..."
	@git submodule updating --init

fetch-hg:
	@echo "Cloning Mercurial repository"
	@[ -d tests/repositories/hg ] && rm -rf tests/repositories/hg
	@hg clone http://xvzf@bitbucket.org/xvzf/quotes tests/repositories/hg

fetch-svn:
	@echo "Checking out SVN repository"
	@[ -d tests/repositories/svn ] && rm -rf tests/repositories/svn
	@svn checkout http://svn.github.com/xvzf/quotes.git tests/repositories/svn

fetch-repositories: fetch-submodules fetch-hg fetch-svn
	@echo "Updating Git submodules..."
	@git submodule update --init

test:
	@cd tests && python tests.py

.PHONY: fetch-repositories fetch-submodules fetch-hg fetch-svn help test
