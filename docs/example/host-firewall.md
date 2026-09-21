# Host Firewall

The following examples apply to:

* Your personal laptop
* Your personal workstation
* A corporate server behind a [router firewall](router-firewall.md)
* A corporate server in the cloud
* Any other system with only one network connection


## Incoming Only

This is the simplest possible firewall. All outgoing traffic is accepted,
and a small set of listed incoming services is accepted.

``` mermaid
flowchart LR
    public@{shape: cloud} --> localhost@{shape: stadium}
```

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

The example above is a complete `/etc/foomuuri/foomuuri.conf`
configuration file - nothing else needs to be added. It allows incoming
(`public-localhost`) traffic for:

* DHCP reply packets, to obtain a lease from an external DHCP server (IPv4
  and IPv6)
* Ping packets (no ping-flood protection)
* SSH
* Everything else is dropped and logged

All outgoing (`localhost-public`) traffic is accepted. This is usually
safe, but a more specific, bidirectional firewall is safer.


## Bidirectional

This example accepts a specific list of incoming services and a specific
list of outgoing services.

``` mermaid
flowchart LR
    public@{shape: cloud} <--> localhost@{shape: stadium}
```

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

This complete `/etc/foomuuri/foomuuri.conf` configuration file allows the
following incoming traffic:

* DHCP reply packets
* Ping packets, except ping floods
* SSH, up to 5 connections per minute per source IP
* Everything else is dropped and logged

The following outgoing traffic is allowed:

* DHCP request packets, to obtain a lease
* DNS queries
* HTTP and HTTPS
* IMAP
* NTP
* Ping packets
* SMTP
* SSH
* Everything else is rejected and logged


## Multi-zone

This example is similar to the bidirectional example above, except that
there are two outgoing zones:

* `public` is the default, untrusted connection. No network interface is
  listed for it; use NetworkManager to assign a network interface to the
  `public` zone when connecting to an untrusted Wi-Fi network, such as one
  in a cafe.
* `home` is the trusted connection. Likewise, use NetworkManager to select
  the `home` zone when you are in a safe location, such as your home or
  work office.

This example also demonstrates how to use a `template` to avoid listing
the same basic services in both `localhost-public` and `localhost-home`.

``` mermaid
flowchart LR
    subgraph WAN
        direction TB
        public@{shape: cloud}
        home@{shape: cloud}
    end
    public <--> localhost@{shape: stadium}
    home <--> localhost
```

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

home-localhost {  # Incoming traffic in a safe location
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

localhost-home {  # Outgoing traffic in a safe location
  template outgoing_services
  googlemeet
  ipp
  mdns
  ssdp
  reject log
}
```
