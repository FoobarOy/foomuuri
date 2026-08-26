---
hide:
  - navigation
---

# Foomuuri

Foomuuri is a multizone bidirectional nftables firewall.

Example configuration files are available for
[host firewall](example/host-firewall.md) and
[router firewall](example/router-firewall.md).

See the [installation](install.md)
page for instructions on installing Foomuuri. Help is available via
[GitHub discussions](https://github.com/FoobarOy/foomuuri/discussions)
and the `#foomuuri` IRC channel on Libera.Chat.


## Features

* Firewall [zones](config/section/zone.md)
* [Bidirectional](example/host-firewall.md#bidirectional)
  firewalling for incoming, outgoing and forwarding traffic
* Suitable for systems ranging from personal
  [laptops](example/host-firewall.md) to
  [corporate](example/router-firewall.md) firewalls
* Rich rule language for flexible and complex [rules](config/rule/index.md)
* Predefined list of
  [services](https://github.com/FoobarOy/foomuuri/blob/main/etc/default.services.conf)
  for simpler rule writing
* [Macros](config/section/macro.md) and
  [templates](config/section/template.md) supported in the rule language
* IPv4 and IPv6 support, with automatic rule
  [splitting](config/rule/matcher.md#saddr-daddr) per protocol
* [SNAT](config/section/snat.md), [DNAT](config/section/dnat.md) and
  masquerading support
* [Logging](config/rule/logging.md) and packet/byte counting
* [Rate limiting](config/rule/ratelimit.md)
* DNS hostname [lookup](config/section/iplist.md) and IP-list support, with
  dynamic IP address refreshing
* [Country database](config/section/iplist.md) (geolocation) support
* [Multiple ISP](example/multiple-isp.md) support, with an internal network
  [connectivity monitor](tool/monitor.md)
* [IPsec](config/rule/matcher.md#sipsec-dipsec) matching support
* Ability to [map](config/section/zonemap.md) specific traffic to separate
  zones
* Automatic IP address [banning](example/advanced.md#automatic-ip-address-banning)
  support
* [Port knocking](example/advanced.md#port-knocking) support
* D-Bus API
* Firewalld emulation for NetworkManager's zone support
* Support for raw nftables [rules](config/rule/misc.md#nft)
* Fresh design, written to use modern nftables features


## Changelog

Recent changes are documented in the
[changelog](https://github.com/FoobarOy/foomuuri/blob/main/CHANGELOG.md).
