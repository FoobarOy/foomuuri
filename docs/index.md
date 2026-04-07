# Foomuuri

Foomuuri is a multizone bidirectional nftables firewall.

See [host firewall](Host-Firewall.md) or [router firewall](Router-Firewall.md)
for example configuration files.

[Getting started](Getting-Started.md) page contains quick instructions how to
install Foomuuri. Help is available via
[GitHub discussions](https://github.com/FoobarOy/foomuuri/discussions).


## Features

* Firewall [zones](Configuration.md#zone)
* [Bidirectional](Host-Firewall.md#example-configuration-for-bidirectional)
  firewalling for incoming, outgoing and forwarding traffic
* Suitable for all systems from personal [laptop](Host-Firewall.md) to
  [corporate](Router-Firewall.md) firewalls
* Rich rule language for flexible and complex [rules](Rule.md)
* Predefined list of
  [services](https://github.com/FoobarOy/foomuuri/blob/main/etc/default.services.conf)
  for simple rule writing
* Rule language supports [macros](Configuration.md#macro) and
  [templates](Configuration.md#template)
* IPv4 and IPv6 support with automatic rule [splitting](Rule.md#saddr-daddr)
  per protocol
* [SNAT](Configuration.md#snat), [DNAT](Configuration.md#dnat) and masquerading
  support
* [Logging](Rule.md#logging) and counting
* [Rate](Rule.md#rate-limit) limiting
* DNS hostname [lookup](Configuration.md#iplist) and IP-list support with dynamic
  IP address refreshing
* [Country database](Configuration.md#iplist) support aka geolocation
* [Multiple ISP](Multiple-ISP.md) support with internal network
  [connectivity monitor](Monitor.md)
* [IPsec](Rule.md#sipsec-dipsec) matching support
* Ability to [map](Configuration.md#zonemap) certain traffic to separate zones
* D-Bus API
* FirewallD emulation for NetworkManager's zone support
* Raw nftables [rules](Rule.md#nft) can be used
* Fresh design, written to use modern nftables's features


