# Foomuuri

Foomuuri is a multizone bidirectional nftables firewall.

Full documentation is available [here](https://foomuuri.foobar.fi/latest/).
Example configuration files are available for
[host firewall](https://foomuuri.foobar.fi/latest/example/host-firewall/) and
[router firewall](https://foomuuri.foobar.fi/latest/example/router-firewall/).

See the [installation](https://foomuuri.foobar.fi/latest/install/)
page for instructions on installing Foomuuri. Help is available via
[GitHub discussions](https://github.com/FoobarOy/foomuuri/discussions)
and the `#foomuuri` IRC channel on Libera.Chat.


## Features

* Firewall zones
* Bidirectional firewalling for incoming, outgoing and forwarding traffic
* Suitable for systems ranging from personal laptops to corporate firewalls
* Rich rule language for flexible and complex rules
* Predefined list of services for simpler rule writing
* Macros and templates supported in the rule language
* IPv4 and IPv6 support, with automatic rule splitting per protocol
* SNAT, DNAT and masquerading support
* Logging and packet/byte counting
* Rate limiting
* DNS hostname lookup and IP-list support, with dynamic IP address refreshing
* Country database (geolocation) support
* Multiple ISP support, with an internal network connectivity monitor
* IPsec matching support
* Ability to map specific traffic to separate zones
* Automatic IP address banning support
* Port knocking support
* D-Bus API
* Firewalld emulation for NetworkManager's zone support
* Support for raw nftables rules
* Fresh design, written to use modern nftables features


## Example configuration

Example configuration file to filter incoming traffic only:

```
zone {
  localhost
  public  eth1  # Interface list may be empty if using NetworkManager.
                # Glob patterns like * or e* are supported too.
}

public-localhost {  # Allow specified incoming traffic
  dhcp-client
  dhcpv6-client
  ping
  ssh
  drop log
}

localhost-public {  # Allow all outgoing traffic
  accept
}
```
