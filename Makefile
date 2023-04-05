.PHONY: all test clean distclean install sysupdate release tar rpm deb

all: test

test:
	flake8-3 src/foomuuri
	pycodestyle-3 src/foomuuri
	pylint-3 src/foomuuri

clean distclean:
	rm -rf foomuuri-*.tar.gz foomuuri-*.src.rpm foomuuri-*.deb tmp/

install:
	mkdir -p $(PREFIX)/etc/foomuuri/
	mkdir -p $(PREFIX)/usr/sbin/
	cp src/foomuuri $(PREFIX)/usr/sbin/
	mkdir -p $(PREFIX)/usr/lib/sysctl.d/
	cp etc/50-foomuuri.conf $(PREFIX)/usr/lib/sysctl.d/50-foomuuri.conf
	mkdir -p $(PREFIX)/usr/share/foomuuri/
	cp etc/default.services.conf $(PREFIX)/usr/share/foomuuri/
	cp etc/static.nft $(PREFIX)/usr/share/foomuuri/
	mkdir -p $(PREFIX)/usr/lib/systemd/system/
	cp systemd/foomuuri.service $(PREFIX)/usr/lib/systemd/system/
	cp systemd/foomuuri-dbus.service $(PREFIX)/usr/lib/systemd/system/
	cp systemd/foomuuri-resolve.timer $(PREFIX)/usr/lib/systemd/system/
	cp systemd/foomuuri-resolve.service $(PREFIX)/usr/lib/systemd/system/
	mkdir -p $(PREFIX)/usr/lib/tmpfiles.d/
	cp systemd/foomuuri.tmpfilesd $(PREFIX)/usr/lib/tmpfiles.d/foomuuri.conf
	mkdir -p $(PREFIX)/run/foomuuri/
	mkdir -p $(PREFIX)/var/lib/foomuuri/
	mkdir -p $(PREFIX)/usr/share/dbus-1/system.d/
	cp systemd/fi.foobar.Foomuuri1.conf $(PREFIX)/usr/share/dbus-1/system.d/
	cp firewalld/fi.foobar.Foomuuri-FirewallD.conf $(PREFIX)/usr/share/dbus-1/system.d/
	cp firewalld/dbus-firewalld.conf $(PREFIX)/usr/share/foomuuri/

sysupdate:
	make install PREFIX=/
	systemctl daemon-reload

### Release

release:
	@if [ -z "$(VERSION)" ]; then \
		echo "Usage: make release VERSION=x.xx"; \
		echo; \
		echo "Current: $(shell grep ^VERSION src/foomuuri)"; \
		exit 1; \
	fi
	git diff --exit-code
	git diff --cached --exit-code
	sed -i -e "s@^\(VERSION = '\).*@\1$(VERSION)'@" src/foomuuri
	sed -i -e "s@^\(Version:        \).*@\1$(VERSION)@" foomuuri.spec
	sed -i -e "s@^\(Version: \).*@\1$(VERSION)@" debian/control
	sed -i -e "s@^\(Version: \).*@\1$(VERSION)@" debian/firewalld.control
	git add src/foomuuri foomuuri.spec debian/control debian/firewalld.control
	git commit --message="v$(VERSION)"
	git tag "v$(VERSION)"
	echo
	echo "== TODO =="
	echo "make rpm deb"
	echo "git push; git push --tags"
	echo "In GitHub: draft a new release and upload rpm and deb files."

### Build tar/rpm/deb locally

SPEC_VERSION ?= $(lastword $(shell grep ^Version: foomuuri.spec))

tar: clean
	tar cavf foomuuri-$(SPEC_VERSION).tar.gz --transform=s,,foomuuri-$(SPEC_VERSION)/, --show-transformed .gitignore *

rpm: tar
	rpmbuild -ba --define="_topdir $(CURDIR)/tmp" --define="_sourcedir $(CURDIR)" foomuuri.spec

deb: clean
	make install PREFIX=tmp/1
	cp --archive debian tmp/1/DEBIAN
	mkdir -p tmp/2/DEBIAN
	mkdir -p tmp/2/usr/share/dbus-1/system.d
	mkdir -p tmp/2/usr/share/foomuuri
	mv tmp/1/DEBIAN/firewalld.control tmp/2/DEBIAN/control
	mv tmp/1/usr/share/dbus-1/system.d/fi.foobar.Foomuuri-FirewallD.conf tmp/2/usr/share/dbus-1/system.d/
	mv tmp/1/usr/share/foomuuri/dbus-firewalld.conf tmp/2/usr/share/foomuuri/
	dpkg-deb --root-owner-group --build tmp/1 foomuuri-$(SPEC_VERSION)_all.deb
	dpkg-deb --root-owner-group --build tmp/2 foomuuri-firewalld-$(SPEC_VERSION)_all.deb
