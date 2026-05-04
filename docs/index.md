---
hide:
  - navigation
---

# Foomuuri

Foomuuri is a multizone bidirectional nftables firewall.

See [host firewall](example/host-firewall.md) or [router firewall](example/router-firewall.md)
for example configuration files.

[Installation](install.md) page contains instructions how to
install Foomuuri. Help is available via
[GitHub discussions](https://github.com/FoobarOy/foomuuri/discussions) and
IRC channel `#foomuuri` on Libera.Chat.


## Features

* Firewall [zones](config/section/zone.md)
* [Bidirectional](example/host-firewall.md#bidirectional)
  firewalling for incoming, outgoing and forwarding traffic
* Suitable for all systems from personal [laptop](example/host-firewall.md) to
  [corporate](example/router-firewall.md) firewalls
* Rich rule language for flexible and complex [rules](config/rule/index.md)
* Predefined list of
  [services](https://github.com/FoobarOy/foomuuri/blob/main/etc/default.services.conf)
  for simple rule writing
* Rule language supports [macros](config/section/macro.md) and
  [templates](config/section/template.md)
* IPv4 and IPv6 support with automatic rule [splitting](config/rule/matcher.md#saddr-daddr)
  per protocol
* [SNAT](config/section/snat.md), [DNAT](config/section/dnat.md) and masquerading
  support
* [Logging](config/rule/logging.md) and counting
* [Rate](config/rule/ratelimit.md) limiting
* DNS hostname [lookup](config/section/iplist.md) and IP-list support with dynamic
  IP address refreshing
* [Country database](config/section/iplist.md) support aka geolocation
* [Multiple ISP](example/multiple-isp.md) support with internal network
  [connectivity monitor](tool/monitor.md)
* [IPsec](config/rule/matcher.md#sipsec-dipsec) matching support
* Ability to [map](config/section/zonemap.md) certain traffic to separate zones
* [Port knocking](example/advanced.md#port-knocking) and automatic IP address
  [banning](example/advanced.md#automatic-ip-address-banning) support
* D-Bus API
* Firewalld emulation for NetworkManager's zone support
* Raw nftables [rules](config/rule/misc.md#nft) can be used
* Fresh design, written to use modern nftables's features


## Changelog

[Changelog](https://github.com/FoobarOy/foomuuri/blob/main/CHANGELOG.md) file
contains recent changes.
