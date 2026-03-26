# Foomuuri - Multizone bidirectional nftables firewall.

SUBDIRS	?= $(sort $(wildcard ??-*))
SOURCE	?= ../src/foomuuri ../src/tests/

.PHONY: all clean distclean $(SUBDIRS)

ifdef COVERAGE
export RUN	= unshare --map-root-user --net coverage run --append --data-file=$(CURDIR)/../.coverage
else
export RUN	= python3
endif

all:
ifdef RUFF
	ruff check $(SOURCE)
endif
ifdef TY
	ty check --ignore unresolved-import $(SOURCE)
endif
	cd ../ ; $(RUN) -m unittest
	flake8 $(SOURCE)
	pycodestyle $(SOURCE)
	pylint $(SOURCE)
	$(MAKE) $(SUBDIRS)

clean distclean:
	rm -f */*.fw
	rm -f */iplist-cache.json
	rm -f */zone

$(SUBDIRS):
	$(RUN) ../src/foomuuri --set=etc_dir=$@ --set=share_dir=../etc --set=state_dir=$@ --set=run_dir=$@ check
	diff -u $@/golden.txt $@/next.fw
	[ ! -f $@/Makefile ] || $(MAKE) -C $@
