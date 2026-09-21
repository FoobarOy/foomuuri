# Router Firewall


## localhost - public - internal

This example is for a small corporate firewall:

* A single firewall computer that runs:
  * DHCP server
  * DNS resolver
* Email and all other services run in the cloud
* Multiple laptops and workstations on the internal network
* Bidirectional firewalling

``` mermaid
flowchart LR
    public@{shape: cloud} <--> localhost@{shape: stadium}
    subgraph Local Network
        localhost <--> internal
    end
```

```
zone {
  localhost
  public eth0
  internal eth1
}

snat {
  # Masquerade traffic from internal to public.
  saddr 10.0.0.0/8 oifname eth0 masquerade
}

public-localhost {
  # Allow only ping and SSH to localhost.
  ping saddr_rate "5/second burst 20"
  ssh saddr_rate "5/minute burst 5"
  # If localhost obtains its public IP via DHCP, add "dhcp-client" here.
  drop log
}

internal-localhost {
  # localhost runs the DHCP (IPv4 and IPv6) server and DNS resolver for the
  # internal network, plus basic SSH and similar rules.
  dhcp-server
  dhcpv6-server
  domain
  domain-s
  ntp
  ping
  ssh
  reject log
}

template outgoing_services {
  # Shared list of services for localhost-public and internal-public.
  domain
  domain-s
  http
  https
  ntp
  ping
  smtp
  ssh
}

localhost-public {
  # Basic services from localhost to the internet: DNS queries, HTTPS, SSH,
  # etc. Also allow SMTP so localhost can send email.
  template outgoing_services
  # If localhost obtains its public IP via DHCP, add "dhcp-server" here and
  # "dhcp-client" to public-localhost.
  reject log
}

internal-public {
  # Laptops and workstations on the internal network can access web and
  # email services on the internet. This ruleset is similar to
  # localhost-public in the host firewall example, and is the most
  # important zone-zone section to configure.
  template outgoing_services
  googlemeet
  imap
  reject log
}

public-internal {
  # No traffic is allowed from the internet to the internal network.
  drop log
}

localhost-internal {
  # DHCP server reply packets
  dhcp-client
  dhcpv6-client
  # Very limited access from localhost to the internal network.
  ping
  ssh
  reject log
}
```


### Enable Packet Forwarding

For `public-internal` and other forwarding to work, you must enable IP
packet forwarding in the Linux kernel. Do this by creating
`/etc/sysctl.d/50-ip.forwarding.conf` with the following lines:

```
# Enable IP packet forwarding

net.ipv4.conf.all.forwarding = 1
net.ipv6.conf.all.forwarding = 1
```


## localhost - public - dmz - internal

This example is for a larger corporate firewall:

* A single firewall computer that runs:
  * DHCP server
  * DNS resolver
* A single dmz computer that runs:
  * Web server
  * Email server
* Multiple laptops and workstations on the internal network
* Bidirectional firewalling

See also the note about enabling IP packet forwarding above.

``` mermaid
flowchart LR
    public@{shape: cloud} <--> localhost@{shape: stadium}
    subgraph Local Network
        localhost <--> internal
        localhost <--> dmz
    end
```

```
zone {
  localhost
  public eth0
  internal eth1
  dmz eth2
}

snat {
  # Masquerade traffic from internal to public.
  saddr 10.0.0.0/8 oifname eth0 masquerade
}

dnat {
  # DNAT incoming SMTP and HTTPS traffic from public to the dmz server. This
  # section is only needed if the dmz server doesn't have a public IP address.
  iifname eth0 smtp http https dnat 10.1.0.2  # public -> dmz
  iifname eth1 daddr 192.0.2.32 smtp http https dnat 10.1.0.2  # internal -> dmz
}

macro {
  # Define rate limits as macros, since the same limits are used in
  # public-localhost and public-dmz.
  http_rate saddr_rate "100/second burst 400" saddr_rate_name http_limit
  mail_rate saddr_rate "1/second burst 10"
  ping_rate saddr_rate "5/second burst 20"
  ssh_rate  saddr_rate "5/minute burst 5"
}

template localhost_services {
  # Shared list of services running on localhost. It runs the DHCP server
  # and DNS resolver for the internal and dmz networks, plus basic SSH and
  # similar rules.
  dhcp-server
  dhcpv6-server
  domain
  domain-s
  ntp
  ping
  ssh
}

public-localhost {
  # Allow only ping and SSH from the internet to localhost.
  ping ping_rate
  ssh ssh_rate
  drop log
}

internal-localhost {
  # Servers on the internal network can access localhost's basic services.
  template localhost_services
  reject log
}

dmz-localhost {
  # Servers on dmz can access localhost's basic services, similar to
  # internal-localhost.
  template localhost_services
  reject log
}

template public_services {
  # Shared list of services that can be reached on the internet.
  domain
  domain-s
  http
  https
  ntp
  ping
  ssh
}

localhost-public {
  # Basic services from localhost to the internet: DNS queries, HTTPS,
  # SSH, etc.
  template public_services
  reject log
}

internal-public {
  # Basic services from internal to the internet: DNS queries, HTTPS,
  # SSH, etc.
  template public_services
  googlemeet
  reject log
}

dmz-public {
  # Basic services from dmz to the internet, plus SMTP for email transfer.
  template public_services
  smtp
  reject log
}

public-internal {
  # No traffic is allowed from the internet to the internal network.
  drop log
}

localhost-internal {
  # DHCP server reply packets
  dhcp-client
  dhcpv6-client
  # Very limited access from localhost to the internal network.
  ping
  ssh
  reject log
}

dmz-internal {
  # Servers on dmz don't need any access to the internal network.
  reject log
}

template dmz_services {
  # Shared list of services that run on dmz.
  http
  https
  ping
  smtp
  ssh
}

localhost-dmz {
  # DHCP server reply packets
  dhcp-client
  dhcpv6-client
  # localhost can access dmz server services.
  template dmz_services
  reject log
}

public-dmz {
  # Allow traffic from the internet to the dmz server, with rate limits.
  http http_rate
  https http_rate
  smtp mail_rate
  ping ping_rate
  ssh ssh_rate
  drop log
}

internal-dmz {
  # Laptops and workstations on the internal network can access dmz server
  # services, plus IMAP for reading email.
  template dmz_services
  imap
  reject log
}
```
