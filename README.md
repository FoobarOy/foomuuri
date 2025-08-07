# Foomuuri

Foomuuri is a multizone bidirectional nftables firewall.

See [wiki](https://github.com/FoobarOy/foomuuri/wiki) for documentation
and [host firewall](https://github.com/FoobarOy/foomuuri/wiki/Host-Firewall)
or [router firewall](https://github.com/FoobarOy/foomuuri/wiki/Router-Firewall)
for example configuration files.

[Getting started](https://github.com/FoobarOy/foomuuri/wiki/Getting-Started)
page contains quick instructions how to install Foomuuri. Help is available
via [discussions](https://github.com/FoobarOy/foomuuri/discussions).


## Features

* Firewall zones
* Bidirectional firewalling for incoming, outgoing and forwarding traffic
* Suitable for all systems from personal laptop to corporate firewalls
* Rich rule language for flexible and complex rules
* Predefined list of services for simple rule writing
* Rule language supports macros and templates
* IPv4 and IPv6 support with automatic rule splitting per protocol
* SNAT, DNAT and masquerading support
* Logging and counting
* Rate limiting
* DNS hostname lookup and IP-list support with dynamic IP address refreshing
* Country database support aka geolocation
* Multiple ISP support with internal network connectivity monitor
* IPsec matching support
* Ability to map certain traffic to separate zones
* D-Bus API
* FirewallD emulation for NetworkManager's zone support
* Raw nftables rules can be used
* Fresh design, written to use modern nftables's features
