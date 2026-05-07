# Host Firewall

Following examples apply for:

* Your personal laptop
* Your personal workstation
* Corporate server behind [router firewall](router-firewall.md)
* Corporate server on cloud
* Any other system with only one network connection


## Incoming only

This is the simplest possible firewall. All outgoing traffic is accepted
and few listed incoming services are accepted.

```
zone {
  localhost
  public  *  # All network interfaces belong to zone "public"
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

Above example is complete `/etc/foomuuri/foomuuri.conf` configuration
file - there is nothing else to be added. It allows incoming
(`public-localhost`) traffic:

* DHCP reply packets to obtain a lease from external DHCP server (IPv4 and
  IPv6)
* Ping packets (no ping-flood protection)
* SSH
* Everything else is dropped and logged

All outgoing (`localhost-public`) traffic is accepted. This is usually safe
but more specific bidirectional firewall is safer.


## Bidirectional

This example accepts listed incoming services and listed outgoing services.

```
zone {
  localhost
  public  *
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


## Multi-zone

This is similar to bidirectional example, except there are two outgoing
zones:

* `public` is the default untrusted connection. There is no network interface
  listed. Use NetworkManager to assign network interface to `public` zone when
  you're connecting to untrusted Wi-Fi network, for example in a cafe.
* `home` is trusted connection. Again use NetworkManager to select `home`
  zone when you're in a safe place, like at your home or office.

This example also shows you how to use `template` to avoid listing
same basic services in `localhost-public` and in `localhost-home`.

```
zone {
  localhost
  public
  home
}

public-localhost {  # Incoming traffic in a cafe
  dhcp-client
  dhcpv6-client
  ping saddr_rate "5/second burst 20"
  ssh saddr_rate "5/minute burst 5"
  drop log
}

home-localhost {  # Incoming traffic in safe location
  dhcp-client
  dhcpv6-client
  lsdp
  mdns
  ping
  ssdp
  ssh
  drop log
}

template outgoing_services {  # Common outgoing traffic
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

localhost-public {  # Outgoing traffic in a cafe
  template outgoing_services
  reject log
}

localhost-home {  # Outgoing traffic in safe location
  template outgoing_services
  googlemeet
  ipp
  mdns
  ssdp
  reject log
}
```
