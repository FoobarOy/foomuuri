SUBDIRS ?= $(sort $(wildcard ??-*))

.PHONY: all clean distclean $(SUBDIRS)

all: $(SUBDIRS)
	flake8 ../src/foomuuri
	pycodestyle ../src/foomuuri
	pylint ../src/foomuuri

clean distclean:
	rm -f */*.fw
	rm -f */iplist-cache.json
	rm -f */zone

$(SUBDIRS):
	../src/foomuuri --set=etc_dir=$@ --set=share_dir=../etc --set=state_dir=$@ --set=run_dir=$@ check
	diff -u $@/golden.txt $@/next.fw
	[ ! -f $@/Makefile ] || $(MAKE) -C $@
