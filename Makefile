help:
	@echo 'Commonly used make targets:'
	@echo '  init-repos          - Create test repos'
	@echo '  test                - Run tests'

test: init-repos run_tests clean

quicktest: run_tests clean

run_tests:
	@cd tests && python tests.py

clean:
	@rm -rf tests/repositories/
	@rm -rf tests/data/

init-bzr:
	@echo "Creating Bazaar repository..."
	@rm -rf tests/repositories/bzr
	@rm -rf tests/data/bzr
	@mkdir -p tests/repositories/bzr/foo/bar
	@mkdir -p tests/data/bzr
	@bzr init tests/repositories/bzr > /dev/null 2>&1
	@cd tests/repositories/bzr && echo "This is a test" > quotes.txt
	@cd tests/repositories/bzr && echo "This is a test" > foo/bar/test.txt
	@cd tests/repositories/bzr && bzr add . > /dev/null 2>&1
	@cd tests/repositories/bzr && bzr commit -m "First commit." > /dev/null 2>&1
	@cd tests/data/bzr && echo 'bzr' > branch
	@cd tests/data/bzr && ln -sf branch system
	@cd tests/data/bzr && head -n1 ../../repositories/bzr/.bzr/branch/last-revision | awk '{print $$1}' > revision
	@cd tests/data/bzr && ln -s revision hash

init-darcs:
	@echo "Creating Darcs repository..."
	@rm -rf tests/repositories/darcs/
	@rm -rf tests/data/darcs/
	@mkdir -p tests/repositories/darcs/foo/bar
	@mkdir -p tests/data/darcs
	@cd tests/repositories/darcs && darcs initialize
	@cd tests/repositories/darcs && echo "This is a test" > quotes.txt
	@cd tests/repositories/darcs && echo "This is a test" > foo/bar/test.txt
	@cd tests/repositories/darcs && darcs add -r . > /dev/null
	@cd tests/repositories/darcs && darcs record -a -m "First commit." > /dev/null 2>&1
	@cd tests/data/darcs && echo 'darcs' > branch
	@cd tests/data/darcs && ln -sf branch system
	@cd tests/repositories/darcs && darcs changes --last 1 --xml | grep hash | awk -F "hash='" '{print $$NF}' | awk -F '-' '{print $$3}' | cut -c-7 > ../../data/darcs/hash
	@cd tests/data/darcs && ln -sf hash revision

init-fossil:
	@echo "Creating Fossil repository..."
	@rm -rf tests/repositories/fossil
	@rm -rf tests/data/fossil
	@mkdir -p tests/repositories/fossil/foo/bar
	@mkdir -p tests/data/fossil
	@fossil init tests/repositories/fossil/fossil > /dev/null 2>&1
	@cd tests/repositories/fossil && fossil open fossil 2> /dev/null
	@cd tests/repositories/fossil && echo "This is a test" > quotes.txt
	@cd tests/repositories/fossil && echo "This is a test" > foo/bar/test.txt
	@cd tests/repositories/fossil && fossil add . > /dev/null 2>&1
	@cd tests/repositories/fossil && fossil commit -m "First commit." > /dev/null 2>&1
	@cd tests/data/fossil && echo "fossil" > system
	@cd tests/data/fossil && sqlite3 ../../repositories/fossil/fossil "SELECT uuid from blob ORDER BY rid DESC LIMIT 1;" | cut -c-7 > hash
	@cd tests/data/fossil && ln -sf hash revision
	@cd tests/data/fossil && sqlite3 ../../repositories/fossil/fossil "SELECT value FROM tagxref WHERE value IS NOT NULL LIMIT 1" > branch

init-git:
	@echo "Creating Git repository..."
	@rm -rf tests/repositories/git
	@rm -rf tests/data/git
	@mkdir -p tests/repositories/git/foo/bar
	@mkdir -p tests/data/git
	@git init tests/repositories/git > /dev/null 2>&1
	@cd tests/repositories/git && echo "This is a test" > quotes.txt
	@cd tests/repositories/git && echo "This is a test" > foo/bar/test.txt
	@cd tests/repositories/git && git add . > /dev/null 2>&1
	@cd tests/repositories/git && git commit -m "First commit." > /dev/null 2>&1
	@cd tests/data/git && echo "git" > system
	@cd tests/repositories/git && git log -n1 --oneline | awk '{print $$1}' > ../../data/git/hash
	@cd tests/data/git && ln -sf hash revision
	@cd tests/repositories/git && git rev-parse --abbrev-ref HEAD > ../../data/git/branch

init-hg:
	@echo "Creating Mercurial repository..."
	@rm -rf tests/repositories/hg
	@rm -rf tests/data/hg
	@mkdir -p tests/repositories/hg/foo/bar
	@mkdir -p tests/data/hg
	@hg init tests/repositories/hg
	@cd tests/repositories/hg && echo "This is a test" > quotes.txt
	@cd tests/repositories/hg && echo "This is a test" > foo/bar/test.txt
	@cd tests/repositories/hg && hg add . > /dev/null 2>&1
	@cd tests/repositories/hg && hg commit -m "First commit." --user `whoami`
	@cd tests/data/hg && echo "hg" > system
	@cd tests/repositories/hg && hg id -i | cut -c-7 > ../../data/hg/hash
	@cd tests/repositories/hg && hg id -n > ../../data/hg/revision
	@cd tests/repositories/hg && hg branch > ../../data/hg/branch

init-svn:
	@echo "Creating Subversion repository..."
	@rm -rf tests/repositories/svn
	@rm -rf tests/data/svn
	@mkdir -p tests/repositories/svn/src
	@mkdir -p tests/repositories/svn/dst
	@mkdir -p tests/data/svn/dst
	@svnadmin create tests/repositories/svn/src
	@svn checkout file://`pwd`/tests/repositories/svn/src tests/repositories/svn/dst > /dev/null
	@mkdir -p tests/repositories/svn/dst/foo/bar
	@cd tests/repositories/svn/dst && echo "This is a test" > quotes.txt
	@cd tests/repositories/svn/dst && echo "This is a test" > foo/bar/test.txt
	@cd tests/repositories/svn/dst && svn add quotes.txt foo > /dev/null
	@cd tests/repositories/svn/dst && svn commit -m "First commit." > /dev/null
	@cd tests/data/svn/dst && echo "svn" > system
	@cd tests/data/svn/dst && echo "(unknown)" > branch
	@cd tests/data/svn/dst && svn info ../../../repositories/svn/dst | grep Revision | awk '{print $$2}' > revision
	@cd tests/data/svn/dst && ln -sf revision hash

init-repos: clean init-bzr init-darcs init-fossil init-git init-hg init-svn

.PHONY: clean help run_tests test $(wildcard init-*)
