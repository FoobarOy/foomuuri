.PHONY: all test clean distclean install sysupdate release tar rpm deb

SYSTEMD_SYSTEM_LOCATION	?= /usr/lib/systemd/system

all: test

test:
	flake8 src/foomuuri
	pycodestyle src/foomuuri
	pylint src/foomuuri

clean distclean:
	rm -rf foomuuri-*.tar.gz foomuuri-*.src.rpm foomuuri-*.deb tmp/

install:
	mkdir -p $(DESTDIR)/etc/foomuuri/
	mkdir -p $(DESTDIR)/usr/sbin/
	cp src/foomuuri $(DESTDIR)/usr/sbin/
	mkdir -p $(DESTDIR)/usr/lib/sysctl.d/
	cp etc/50-foomuuri.conf $(DESTDIR)/usr/lib/sysctl.d/50-foomuuri.conf
	mkdir -p $(DESTDIR)/usr/share/foomuuri/
	cp etc/default.services.conf $(DESTDIR)/usr/share/foomuuri/
	cp etc/static.nft $(DESTDIR)/usr/share/foomuuri/
	mkdir -p $(DESTDIR)$(SYSTEMD_SYSTEM_LOCATION)/
	cp systemd/foomuuri.service $(DESTDIR)$(SYSTEMD_SYSTEM_LOCATION)/
	cp systemd/foomuuri-dbus.service $(DESTDIR)$(SYSTEMD_SYSTEM_LOCATION)/
	cp systemd/foomuuri-iplist.service $(DESTDIR)$(SYSTEMD_SYSTEM_LOCATION)/
	cp systemd/foomuuri-iplist.timer $(DESTDIR)$(SYSTEMD_SYSTEM_LOCATION)/
	cp systemd/foomuuri-monitor.service $(DESTDIR)$(SYSTEMD_SYSTEM_LOCATION)/
	cp systemd/foomuuri-resolve.service $(DESTDIR)$(SYSTEMD_SYSTEM_LOCATION)/
	cp systemd/foomuuri-resolve.timer $(DESTDIR)$(SYSTEMD_SYSTEM_LOCATION)/
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

sysupdate:
	make install DESTDIR=/
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
	sed -i -e "s@^\(footer: .* \).*@\1$(VERSION)@" doc/foomuuri.md
	sed -i -e "s@^\(Version: *\).*@\1$(VERSION)@" foomuuri.spec
	sed -i -e "s@^\(Version: *\).*@\1$(VERSION)@" debian/control
	sed -i -e "s@^\(Version: *\).*@\1$(VERSION)@" debian/firewalld.control
	make --directory=doc
	git add src/foomuuri doc/foomuuri.md doc/foomuuri.1 foomuuri.spec debian/control debian/firewalld.control
	git commit --message="v$(VERSION)"
	git tag "v$(VERSION)"
	make rpm
	mv tmp/RPMS/noarch/foomuuri-*.rpm tmp/SRPMS/foomuuri-*.rpm ~
	make deb
	mv foomuuri-*.deb ~
	make clean
	@echo
	@echo "== TODO =="
	@echo "git push; git push --tags"
	@echo "In GitHub: draft a new release and upload rpm and deb files."

### Build tar/rpm/deb locally

SPEC_VERSION ?= $(lastword $(shell grep ^Version: foomuuri.spec))

tar: clean
	tar cavf foomuuri-$(SPEC_VERSION).tar.gz --transform=s,,foomuuri-$(SPEC_VERSION)/, --show-transformed .gitignore *

rpm: tar
	rpmbuild -ba --define="_topdir $(CURDIR)/tmp" --define="_sourcedir $(CURDIR)" foomuuri.spec

deb: clean
	make install DESTDIR=tmp/1
	cp --archive debian tmp/1/DEBIAN
	mkdir -p tmp/2/DEBIAN
	mkdir -p tmp/2/usr/share/dbus-1/system.d
	mkdir -p tmp/2/usr/share/foomuuri
	mv tmp/1/DEBIAN/firewalld.control tmp/2/DEBIAN/control
	mv tmp/1/usr/share/dbus-1/system.d/fi.foobar.Foomuuri-FirewallD.conf tmp/2/usr/share/dbus-1/system.d/
	mv tmp/1/usr/share/foomuuri/dbus-firewalld.conf tmp/2/usr/share/foomuuri/
	dpkg-deb --root-owner-group --build tmp/1 foomuuri-$(SPEC_VERSION)_all.deb
	dpkg-deb --root-owner-group --build tmp/2 foomuuri-firewalld-$(SPEC_VERSION)_all.deb
