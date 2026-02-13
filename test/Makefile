SUBDIRS ?= $(sort $(wildcard ??-*))

.PHONY: all clean distclean $(SUBDIRS)

all: $(SUBDIRS)
	flake8 ../src/foomuuri ../src/tests/
	pycodestyle ../src/foomuuri ../src/tests/
	pylint ../src/foomuuri ../src/tests/
	cd ../ ; python3 -m unittest

clean distclean:
	rm -f */*.fw
	rm -f */iplist-cache.json
	rm -f */zone

$(SUBDIRS):
	../src/foomuuri --set=etc_dir=$@ --set=share_dir=../etc --set=state_dir=$@ --set=run_dir=$@ check
	diff -u $@/golden.txt $@/next.fw
	[ ! -f $@/Makefile ] || $(MAKE) -C $@
