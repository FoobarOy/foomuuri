# ChangeLog

## 0.24 (2024-xx-xx)

* Remove `start-or-good` command line option. Add systemd
  `foomuuri-boot.service` to implement same functionality safer.
* Add `block` command line option to load "block all traffic" ruleset.
* Add `continue` statement. Rule `saddr 192.168.1.1 counter log continue`
  counts and logs traffic from 192.168.1.1 and continues to next rules.
* Add `time` matcher to check hour, date and weekday.
* Add `mac_saddr` and `mac_daddr` matchers to match MAC address. This works
  only for incoming traffic.
* Add `ct_status` matcher to match conntrack status, for example `dnat` or
  `snat`.
* Add `cgroup` matcher to match cgroup id or cgroupv2 name.
* Add `-conntrack` flag to rule. This rule will be outputted before
  conntrack. This can be used to count all specific traffic, or to accept
  some traffic without adding it to conntrack (for example high load DNS
  server).
* Add `redis`, `redis-sentinel`, `vnc`, `domain-quic` (DoQ) and `domain-tls`
  (DoT) macros to default services.
* Matcher `szone -public` in `any-localhost` (or `dzone` in `localhost-any`)
  section can be used to skip adding rule to `public-localhost`.
* Allow using any command (`curl` example included) instead of `fping` in
  network connectivity monitor.
* Allow `foomuuri { nft_bin nft --optimize }` to specify options.
* Fix: `counter myname` didn't work on `prerouting` section.
* Fix: Restart network connectivity monitor `command` if it fails to start
  or dies.

## 0.23 (2024-03-20)

* Rework `multicast` and `broadcast` handling for incoming/outgoing traffic.
  This simplifies macros and results more optimal ruleset.
* Allow outgoing IGMP multicast membership reports, incoming IGMP query.
* Change default `log_level` to `level info flags skuid` to include UID/GID
  for locally generated traffic.
* Add `invalid`, `rpfilter` and `smurfs` sections to accept specific
  traffic that is normally dropped.
* Add `ospf` macro to default services.
* Add support for negative set matching `saddr -@geoip drop`
* Fix: Separate `counter` and `accept counter` rules.
* Fix: Better output for `foomuuri check` if not running as root.
* Fix: Handle D-Bus change event for `lo` interface better.

## 0.22 (2023-12-12)

* Add `protocol` matcher, for example `protocol gre` accepts GRE traffic.
* Add support for `localhost-localhost` section and rules. If not defined,
  it defaults to `accept`.
* Rule's log level can be set with `log_level "level crit"`. This overrides
  global `foomuuri { log_level ... }` setting.
* Iplist refresh interval can be configured globally and per-iplist.
* Pretty output for `foomuuri iplist list` instead of raw nft output.
* Fix handling "[ipv6]", "[ipv6]/mask" and "[ipv6]:port" notations.

## 0.21 (2023-10-06)

* Add support for `$(shell command)` in configuration file
* Add support for named counters: `https counter web_traffic`
* Add support for IPv6 suffix netmask: `::192:168:1:1/-64`
* Add support for conntrack count rates: `saddr_rate "ct count 4"`
* Add `chain_priority` to `foomuuri` section
* Add lot of misconfiguration checks
* `foomuuri reload` restarts firewall and refreshes resolve+iplist
* `foomuuri list counter` lists all named counters
* `foomuuri iplist` subcommands manipulates and lists iplist entries
* Harden `dhcp`, `dhcpv6`, `mdns` and `ssdp` macros
* Fix icmp to handle matchers correctly (`ping saddr 192.168.1.1 drop`)
* Fix caching failed `resolve` section lookups for reboot

## 0.20 (2023-08-15)

* Multi-ISP support with internal network connectivity monitor.
  See wiki's best practices for example configuration.
* Add `mark_set`, `mark_restore` and `mark_save` statements
* Add `mark_match` matcher
* Add `prerouting`, `postrouting`, `output` and `forward` sections for marks
* Expand macros and support quotes in `foomuuri` section
* Fix running pre/post_stop hooks on `foomuuri stop`
* Fix man page section from 1 to 8, other Makefile fixes
* Foomuuri is now included to Fedora, EPEL and Debian. Remove local build
  rules for rpm/deb packages.

## 0.19 (2023-05-19)

* Add `iplist` section to import IP address lists. These can be used to
  import IP country lists, whitelists, blacklists, etc.
* Add `hook` section to run external commands when Foomuuri starts/stops
* Fix `dhcpv6-server` macro in default.services.conf
* Add man page and improve documentation
* Add experimental connectivity monitor which will be used for upcoming
  multi ISP support

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
