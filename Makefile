define create-new-repo
	@rm -rf tests/repositories/$1
	@rm -rf tests/data/$1
	@mkdir -p tests/repositories/$1/foo/bar
	@mkdir -p tests/data/$1
	@cd tests/repositories/$1 && echo "This is a test" > quotes.txt
	@cd tests/repositories/$1 && echo "This is a test" > foo/bar/test.txt
	@echo $1 > tests/data/$1/system
	@cd tests/repositories/$1; $2 > /dev/null 2>&1
endef

define run-data-command
	@cd tests/data/$1 && $2
endef

define run-repo-command
	@cd tests/repositories/$1 && $2
endef

help:
	@echo 'Commonly used make targets:'
	@echo '  init-repos          - Create test repos'
	@echo '  test                - Run tests'
	@echo '  quicktest           - Run tests without generating new repos'

test: init-repos run_tests clean

quicktest: run_tests clean

run_tests:
	@cd tests && python tests.py

clean:
	@rm -rf tests/repositories/
	@rm -rf tests/data/

init-bzr:
	@echo "Creating Bazaar repository..."
	@$(call create-new-repo,'bzr',bzr init)
	@$(call run-repo-command,'bzr',bzr add -q .)
	@$(call run-repo-command,'bzr',bzr commit -q -m "First commit.")
	@$(call run-data-command,'bzr',echo 'bzr' > branch)
	@$(call run-data-command,'bzr',head -n1 ../../repositories/bzr/.bzr/branch/last-revision | awk '{print $$1}' > revision)
	@$(call run-data-command,'bzr',ln -s revision hash)

init-darcs:
	@echo "Creating Darcs repository..."
	@$(call create-new-repo,'darcs',darcs initialize)
	@$(call run-repo-command,'darcs',darcs add -q -r .)
	@$(call run-repo-command,'darcs',darcs record -q -a -m "First commit." > /dev/null)
	@$(call run-data-command,'darcs',echo 'darcs' > branch)
	@$(call run-repo-command,'darcs',darcs changes --last 1 --xml | grep hash | awk -F "hash='" '{print $$NF}' | awk -F '-' '{print $$3}' | cut -c-7 > ../../data/darcs/hash)
	@$(call run-data-command,darcs,ln -sf hash revision)

init-fossil:
	@echo "Creating Fossil repository..."
	@$(call create-new-repo,'fossil',fossil init fossil)
	@$(call run-repo-command,'fossil',fossil open fossil > /dev/null)
	@$(call run-repo-command,'fossil',fossil add . > /dev/null)
	@$(call run-repo-command,'fossil',fossil commit -m "First commit." > /dev/null)
	@$(call run-repo-command,'fossil',sqlite3 fossil "SELECT uuid from blob ORDER BY rid DESC LIMIT 1;" | cut -c-7 > ../../data/fossil/hash)
	@$(call run-data-command,'fossil',ln -sf hash revision)
	@$(call run-repo-command,'fossil',sqlite3 fossil "SELECT value FROM tagxref WHERE value IS NOT NULL LIMIT 1" > ../../data/fossil/branch)

init-git:
	@echo "Creating Git repository..."
	@$(call create-new-repo,'git',git init)
	@$(call run-repo-command,'git',git add .)
	@$(call run-repo-command,'git',git commit -m "First commit." > /dev/null)
	@$(call run-repo-command,'git',git log -n1 --oneline | awk '{print $$1}' > ../../data/git/hash)
	@$(call run-data-command,'git',ln -sf hash revision)
	@$(call run-repo-command,'git',git rev-parse --abbrev-ref HEAD > ../../data/git/branch)

init-hg:
	@echo "Creating Mercurial repository..."
	@$(call create-new-repo,'hg',hg init -q)
	@$(call run-repo-command,'hg',hg add -q .)
	@$(call run-repo-command,'hg',hg commit -q -m "First commit" --user `whoami`)
	@$(call run-repo-command,'hg',hg id -i | cut -c-7 > ../../data/hg/hash)
	@$(call run-repo-command,'hg',hg id -n > ../../data/hg/revision)
	@$(call run-repo-command,'hg',hg branch > ../../data/hg/branch)

init-svn:
	@echo "Creating Subversion repository..."
	@$(call create-new-repo,'svn',svnadmin create src)
	@svn checkout file://`pwd`/tests/repositories/svn/src tests/repositories/svn/ > /dev/null
	@$(call run-repo-command,"svn",svn propset -q svn:ignore src .)
	@$(call run-repo-command,"svn",svn add -q quotes.txt foo)
	@$(call run-repo-command,"svn",svn commit -q -m "First commit." > /dev/null)
	@$(call run-data-command,"svn",echo "(unknown)" > branch)
	@$(call run-data-command,'svn',svn info ../../repositories/svn | grep Revision | awk '{print $$2}' > revision)
	@$(call run-data-command,"svn",ln -sf revision hash)

init-repos: clean init-bzr init-darcs init-fossil init-git init-hg init-svn

.PHONY: clean help run_tests test quicktest $(wildcard init-*)
