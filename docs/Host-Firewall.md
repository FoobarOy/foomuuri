# Host Firewall

Following examples apply for:

* Your personal laptop
* Your personal workstation
* Corporate server behind [router firewall](Router-Firewall.md)
* Corporate server on cloud
* Any other system with only one network connection


## Example configuration for incoming only

```
zone {
  localhost
  public
}

public-localhost {
  dhcp-client
  dhcpv6-client
  ping
  ssh
  drop log
}

localhost-public {
  accept
}
```

Above example is the simplest possible firewall. It is complete
`/etc/foomuuri/foomuuri.conf` configuration file - there is nothing else
to be added. It allows incoming (`public-localhost`) traffic:

* DHCP reply packets to obtain a lease from external DHCP server (IPv4 and
  IPv6)
* Ping packets (no ping-flood protection)
* SSH
* Everything else is dropped and logged

All outgoing (`localhost-public`) traffic is accepted. This is usually safe
but more specific bidirectional firewall is safer.

Normally NetworkManager assigns network interfaces to zones via D-Bus and
Foomuuri's firewalld emulation. Alternative is to specify network interface(s)
in `zone` section:

```
zone {
  localhost
  public eth0 wlan0
}
```


## Example configuration for bidirectional

```
zone {
  localhost
  public
}

public-localhost {
  dhcp-client
  dhcpv6-client
  ping saddr_rate "5/second burst 20"
  ssh saddr_rate "5/minute burst 5"
  drop log
}

localhost-public {
  dhcp-server
  dhcpv6-server
  domain
  http
  https
  imap
  ntp
  ping
  smtp
  ssh
  reject log
}
```

This complete `/etc/foomuuri/foomuuri.conf` configuration file allows incoming:

* DHCP reply packets
* Ping packets, except ping-flood
* SSH, up to 5 connections per minute per source IP
* Everything else is dropped and logged

Following outgoing traffic is allowed:

* DHCP request packets to obtain a lease
* DNS queries
* HTTP and HTTPS
* IMAP
* NTP
* Ping packets
* SMTP
* SSH
* Everything else is rejected and logged


## Example configuration for multi-zone

```
zone {
  localhost
  public
  home
}

public-localhost {
  dhcp-client
  dhcpv6-client
  ping saddr_rate "5/second burst 20"
  ssh saddr_rate "5/minute burst 5"
  drop log
}

home-localhost {
  dhcp-client
  dhcpv6-client
  lsdp
  mdns
  ping
  ssdp
  ssh
  drop log
}

template outgoing_services {
  dhcp-server
  dhcpv6-server
  domain
  http
  https
  imap
  ntp
  ping
  smtp
  ssh
}

localhost-public {
  template outgoing_services
  reject log
}

localhost-home {
  template outgoing_services
  googlemeet
  ipp
  mdns
  ssdp
  reject log
}
```

This is similar to bidirectional example, except there are two outgoing
zones:

* `public` is the default untrusted connection. Use NetworkManager to
  assign network interface to `public` zone when you're connecting to
  untrusted Wi-Fi network, for example in a cafe.
* `home` is trusted connection. Again use NetworkManager to select `home`
  zone when you're in a safe place, like at your home or office.

This example also shows you how to use `template` to avoid listing
same basic services in `localhost-public` and in `localhost-home`.
