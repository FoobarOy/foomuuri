# ChangeLog

## 0.19 (2023-xx-xx)

* Add `iplist` section to import IP address lists. These can be used to
  import IP country lists, whitelists, blacklists, etc.
* Add `hook` section to run external commands when Foomuuri starts/stops
* Fix `dhcpv6-server` macro in default.services.conf
* Add man page and improve documentation

## 0.18 (2023-04-18)

* Add rule line validator to configuration file parser
* Rename zone `fw` to `localhost` and make in configurable
* Initial deb packaging
* Improve documentation
* Lot of internal cleanup

## 0.17 (2023-03-31)

* Add `foomuuri list macro` to list all known macros
* New default.services.conf entries: mqtt, secure-mqtt, zabbix
* Improve documentation
* Lot of internal cleanup

## 0.16 (2023-02-27)

* First public release
