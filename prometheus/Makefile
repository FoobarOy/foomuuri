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

EXPORTER_DIR		?= /usr/bin
EXPORTER_NAME		?= foomuuri_exporter
SYSTEMD_SYSTEM_LOCATION	?= /usr/lib/systemd/system
SETTINGS_LOCATION	?= /etc/default

install:
	mkdir -p $(DESTDIR)$(EXPORTER_DIR)/
	cp foomuuri_exporter $(DESTDIR)$(EXPORTER_DIR)/$(EXPORTER_NAME)
	mkdir -p $(DESTDIR)$(SYSTEMD_SYSTEM_LOCATION)/
	cat foomuuri_exporter.service | sed s/foomuuri_exporter/$(EXPORTER_NAME)/g > $(DESTDIR)$(SYSTEMD_SYSTEM_LOCATION)/$(EXPORTER_NAME).service
	mkdir -p $(DESTDIR)$(SETTINGS_LOCATION)/
	cp foomuuri_exporter.default $(DESTDIR)$(SETTINGS_LOCATION)/$(EXPORTER_NAME)

# Install current source to local system's root

sysupdate:
	make install DESTDIR=/
	systemctl daemon-reload
