# Makefile for generating manpages using ronn(1)

all: build-docs

build-docs:
	@find . -name \*.ronn | xargs ronn -b --html --roff

.PHONY: all build-docs
