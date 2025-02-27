# Foomuuri - Multizone bidirectional nftables firewall.

.PHONY: all test devel clean distclean install sysupdate release tar

CURRENT_VERSION		?= $(shell grep ^VERSION src/foomuuri | awk -F\' '{ print $$2 }')

# Default target is to run tests

all: test

# Run testsuite and check source

test:
	$(MAKE) -C test

# Generate firewall ruleset to file, used in development

devel:
	src/foomuuri --set=etc_dir=../devel --set=share_dir=etc --set=state_dir=../devel --set=run_dir=../devel check

# Delete created files

clean distclean:
	rm -f foomuuri-*.tar.gz
	$(MAKE) -C test $@

# Install current source to DESTDIR

BINDIR			?= /usr/sbin
SYSTEMD_SYSTEM_LOCATION	?= /usr/lib/systemd/system

install:
	mkdir -p $(DESTDIR)/etc/foomuuri/
	mkdir -p $(DESTDIR)$(BINDIR)/
	cp src/foomuuri $(DESTDIR)$(BINDIR)/
	mkdir -p $(DESTDIR)/usr/lib/sysctl.d/
	cp etc/50-foomuuri.conf $(DESTDIR)/usr/lib/sysctl.d/50-foomuuri.conf
	mkdir -p $(DESTDIR)/usr/share/foomuuri/
	cp etc/default.services.conf $(DESTDIR)/usr/share/foomuuri/
	cp etc/static.nft $(DESTDIR)/usr/share/foomuuri/
	cp etc/block.fw $(DESTDIR)/usr/share/foomuuri/
	mkdir -p $(DESTDIR)$(SYSTEMD_SYSTEM_LOCATION)/
	cp systemd/foomuuri.service $(DESTDIR)$(SYSTEMD_SYSTEM_LOCATION)/
	cp systemd/foomuuri-boot.service $(DESTDIR)$(SYSTEMD_SYSTEM_LOCATION)/
	cp systemd/foomuuri-dbus.service $(DESTDIR)$(SYSTEMD_SYSTEM_LOCATION)/
	cp systemd/foomuuri-iplist.service $(DESTDIR)$(SYSTEMD_SYSTEM_LOCATION)/
	cp systemd/foomuuri-iplist.timer $(DESTDIR)$(SYSTEMD_SYSTEM_LOCATION)/
	cp systemd/foomuuri-monitor.service $(DESTDIR)$(SYSTEMD_SYSTEM_LOCATION)/
	mkdir -p $(DESTDIR)/usr/lib/tmpfiles.d/
	cp systemd/foomuuri.tmpfilesd $(DESTDIR)/usr/lib/tmpfiles.d/foomuuri.conf
	mkdir -p $(DESTDIR)/run/foomuuri/
	mkdir -p $(DESTDIR)/var/lib/foomuuri/
	mkdir -p $(DESTDIR)/usr/share/dbus-1/system.d/
	cp systemd/fi.foobar.Foomuuri1.conf $(DESTDIR)/usr/share/dbus-1/system.d/
	cp firewalld/fi.foobar.Foomuuri-FirewallD.conf $(DESTDIR)/usr/share/dbus-1/system.d/
	cp firewalld/dbus-firewalld.conf $(DESTDIR)/usr/share/foomuuri/
	mkdir -p $(DESTDIR)/usr/share/man/man8
	cp doc/foomuuri.8 $(DESTDIR)/usr/share/man/man8/

# Install current source to local system's root

sysupdate:
	make install DESTDIR=/
	systemctl daemon-reload

# Make new release

release: test clean
	@if [ -z "$(VERSION)" ]; then \
		echo "Usage: make release VERSION=x.xx"; \
		echo; \
		echo "Current: $(CURRENT_VERSION)"; \
		exit 1; \
	fi
	git diff --exit-code
	git diff --cached --exit-code
	sed -i -e "s@^\(## ${VERSION} .\)20..-xx-xx.@\1$(shell date +'%Y-%m-%d')\)@" CHANGELOG.md
	sed -i -e "s@^\(VERSION = '\).*@\1$(VERSION)'@" src/foomuuri
	sed -i -e "s@^\(footer: .* \).*@\1$(VERSION)@" doc/foomuuri.md
	sed -i -e "s@^\(date: \).*@\1$(shell date +'%b %d, %Y')@" doc/foomuuri.md
	make --directory=doc
	git diff
	git add CHANGELOG.md src/foomuuri doc/foomuuri.md doc/foomuuri.8
	git commit --message="v$(VERSION)"
	git tag "v$(VERSION)"
	@echo
	@echo "== TODO =="
	@echo "git push && git push --tags"
	@echo "GitHub release: https://github.com/FoobarOy/foomuuri/releases/new"

# Build tarball locally

tar: clean
	tar cavf foomuuri-$(CURRENT_VERSION).tar.gz --transform=s,,foomuuri-$(CURRENT_VERSION)/, --show-transformed .gitignore *
