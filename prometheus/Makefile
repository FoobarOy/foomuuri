# Foomuuri - Multizone bidirectional nftables firewall.

.PHONY: all test clean distclean install sysupdate

# Default target is to run tests

all: test

# Check source

test:
	flake8 foomuuri_exporter
	pycodestyle foomuuri_exporter
	pylint foomuuri_exporter

# Nothing to be cleaned

clean distclean:

# Install current source to DESTDIR

BINDIR			?= /usr/bin
SYSTEMD_SYSTEM_LOCATION	?= /usr/lib/systemd/system
SETTINGS_LOCATION	?= /etc/default

install:
	mkdir -p $(DESTDIR)$(BINDIR)/
	cp foomuuri_exporter $(DESTDIR)$(BINDIR)/
	mkdir -p $(DESTDIR)$(SYSTEMD_SYSTEM_LOCATION)/
	cp foomuuri_exporter.service $(DESTDIR)$(SYSTEMD_SYSTEM_LOCATION)/
	mkdir -p $(DESTDIR)$(SETTINGS_LOCATION)/
	cp foomuuri_exporter.default $(DESTDIR)$(SETTINGS_LOCATION)/foomuuri_exporter

# Install current source to local system's root

sysupdate:
	make install DESTDIR=/
	systemctl daemon-reload
