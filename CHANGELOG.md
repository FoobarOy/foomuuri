# ChangeLog

## 0.31 (20xx-xx-xx)

* CVE-2025-67858: Verify `interface` input parameter on D-Bus methods.
* Security hardening:
  * Add `ProtectSystem=full` to all systemd service files. This changes `/etc`
    to read-only for all Foomuuri processes. Make sure you don't write any
    state files there in your startup hook or Foomuuri Monitor event hook.
  * Change umask to 022 when using `--fork` to fork as a background daemon
    process.
  * More strict IP address verify for iplist entries.

## 0.30 (2025-12-12)

* Add `-merge` option to `iplist` section line to disable IP address
  auto-merge. It should be disabled in `fail2ban` alike scenarios, where
  IP addresses are added and deleted by some external program.
* Major speedup when handling large iplists.
* If all iplist entries have `|missing-ok` filter then whole iplist is
  considered as `Warning: Iplist is empty`. If any entry doesn't have
  that filter then empty list is an error.
* Pipe commands to nft instead of reading them from `dbus.fw` or
  `iplist-cache.fw` files.
* Use atomic write to `iplist-cache.json` and other files.
* Add `foomuuri_exporter` binary to collect statistics and export them
  to Prometheus. Similar Munin collector is included to Munin contrib
  repository.
* Include `group` states to `foomuuri-monitor` statistics file.
* Add `prometheus-*` and `sips` macros to default services.
* Make `python-dbus` optional for small systems. It is still highly
  recommended. Now Foomuuri can be run without any additional Python modules.

## 0.29 (2025-09-26)

* Add `snat_prefix` and `dnat_prefix` statements for IPv6-to-IPv6 Network
  Prefix Translation (NPTv6).
* Deprecate unneeded `to` after `snat` and `dnat` statements. It's quietly
  ignored.
* Add `tproxy` matcher for transparent proxying.
* Add `mss pmtu` to calculate the MTU in runtime based on what the routing
  cache has observed via Path MTU Discovery.
* Fix `mss` to apply to IPv4 and IPv6. Previously it was only for IPv4.
* Add `input` section. It processes incoming packets with destination
  `localhost`.
* Add `try-reload` command to safely test new config. It loads new config,
  asks confirmation from user to keep it, and reverts back to old config
  if user didn't reply within 15 seconds.
* Foomuuri Monitor supports and prefers fping's `--squiet=s` mode. It works
  correctly even if the interface is down. fping command option `--interval=ms`
  is automatically converted to `--squiet=s` if possible.
* Add `command_down_interval` and `down_interval` to Foomuuri Monitor.
  Foomuuri Monitor will run that external command in regular intervals if
  network connectivity is still down.
* Default log prefix can be configured with `foomuuri { log_prefix "..." }`.
* Variables `$(szone)`, `$(dzone)` and `$(statement)` can be used in log
  prefix.
* More text to default log prefix can be added with `log + "mytext"`.
* Multiple interfaces can be specified to `iifname` and `oifname` matchers.
  Negative matching also works.
* Use human readable output format in `list counter` command.
* Add `prometheus`, `prometheus-*` and `alertmanager` macros to default
  services.
* Add `--fork` command line option to fork as a background daemon process.
  This applies to `monitor` and `dbus` only.
* Add `--syslog` command line option to enable syslog logging.
* Add bash-completion (requires v2.12 or newer) script.

## 0.28 (2025-04-15)

* Merge `iplist` and `resolve` sections to unified `iplist`. Old config will
  work as is, but updating it to new `iplist` format is recommended: simply
  rename `resolve {}` to `iplist {}` and check timeout and refresh options.
* Add `url_timeout=10d`, `url_refresh=1d`, `dns_timeout=24h` and
  `dns_refresh=15m` options to `iplist` section to specify expiry timeout and
  refresh interval for URLs (HTTP or file) and resolved hostnames.
  * Old `timeout` and `refresh` options are deprecated. They set both `url_XXX`
    and `dns_XXX` values.
* Downloaded `iplist` content can be filtered:
  * `|shell:/path/to/command` pipe it via external command.
  * `|json:filter` use external `jq` command to parse it as JSON data.
  * `|html:XPath` parse it as HTML data.
  * `|xml:XPath` parse it as XML data.
  * `|missing-ok` don't print warning if URL download or DNS resolve fails.
* Improve `template foo` handling to support matchers and everything else that
  macros support.
* Add `prerouting filter raw` and similar sections to allow specifying chain
  type and hook priority.
* Add `notrack` statement to be used in prerouting section to mark packet to
  not be added to conntrack.
* Add `10 mbytes/second` per byte support to rate limits (`global_rate` etc).
* Add `over` support to rate limits to be used with `drop` statement.
* Add `dscp` matcher to match packet's DSCP value.
* Add `bgp` macro to default services.

## 0.27 (2025-01-28)

* BREAKING CHANGES:
  * Previously `mark_set` was a statement. Now it's a matcher and rule's
    default statement `accept` is used if not specified. Usually `accept` is
    what you want to use. To keep previous behavior use `mark_set XX continue`.
  * `mark_save` and `mark_restore` are removed. They are automatically added
    when needed.
  * Multi-ISP example in GitHub wiki is updated to match above changes.
* Add `priority_set` to set packet's traffic control class id.
* Add `priority_match` to check packet's traffic control class id.
* Add `nbd`, `pxe`, `salt`, and `tor` related macros to default services.
* Add `--quiet` command line option to suppress warnings.
* Print warning in `foomuuri check` if macro is overwritten.
* Add more checks for invalid rules, like `ssh saddr` without address.
* Add filters to `foomuuri list`:
  * `foomuuri list macro http https`: specified macros.
  * `foomuuri list macro 80 443`: macros that include value 80 or 443.
  * `foomuuri list counter traffic_in traffic_out`: specified counters.
* Fix: `foomuuri iplist refresh` actually refreshes it now, no need for
  `--force`. Option `--soft` checks for next refresh time.

## 0.26 (2024-11-13)

* Add `iplist flush name` command to delete all entries in iplist.
* Add support for `-macro`, `macro/24`, `[macro]:123` and `macro:123` in
  macro expansion.
* Add support for `icmp echo-request` (and other names) in addition to
  `icmp 8`. Use name in default `ping` macro instead of number.
* Add `--force` command line option to force iplist refresh now.
* Write `foomuuri-monitor` states and statistics to a file once a minute.
* Add `rtsps` macro to default services.
* Fix: Add range support to `iplist list`.
* Fix: `iplist add` and `iplist del` didn't work correctly on all cases.

## 0.25 (2024-10-01)

* Add `status` command to show if Foomuuri is running, current zone-interface
  mapping.
* Add `set interface eth0 zone public` command to change interface to zone.
* Add `set interface eth0 zone -` command to remove interface from all zones.
* Add `queue` statement. It forwards packet to userspace, used for example
  for IPS/IDS.
* Rules in `any-public` section will be added to `public-public` too.
* Improve syntax error checks for rules.
* More relaxed import for external `iplist` lists: handle `;` as comment,
  allow overlapping IP ranges.
* IP address with or without netmask can be used as `resolve` or `iplist`
  entry.
* Add warning if `resolve` hostname doesn't resolve or whole set is empty.
* Add `ipsec-nat`, `pop3s`, `gluster-client`, `gluster-management`, `amqp`,
  `snmptrap` and `activedirectory` macros to default services.
* Automatically add final `drop log` rule to zone-zone section if it is
  missing for improved logging.
* Fix: Allow using nft's reserved words like `inet` as interface name or
  uid/gid.
* Fix: Don't traceback if `resolve` or `iplist` refresh takes over 60 second
  on `foomuuri reload`.

## 0.24 (2024-06-19)

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
