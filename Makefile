.PHONY: all test clean distclean install sysupdate tar rpm foopkg

all: test

test:
	flake8-3 src/foomuuri
	pycodestyle-3 src/foomuuri
	pylint-3 src/foomuuri

clean distclean:
	rm -rf foomuuri-*.tar.gz foomuuri-*.src.rpm foopkg.conf tmp/

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

VERSION ?= $(lastword $(shell grep ^Version: foomuuri.spec))

tar: clean
	tar cavf foomuuri-$(VERSION).tar.gz --transform=s,,foomuuri-$(VERSION)/, --show-transformed .gitignore *

rpm: tar
	rpmbuild -ba --define="_topdir $(CURDIR)/tmp" --define="_sourcedir $(CURDIR)" foomuuri.spec

foopkg:
	rpmdev-spectool --get-files foomuuri.spec
	echo "[foopkg]" > foopkg.conf
	echo "buildrepo = foo9/foobar-testing" >> foopkg.conf
	foopkg build
