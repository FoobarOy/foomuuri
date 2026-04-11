# Multiple ISP

Foomuuri supports multiple ISPs (aka multi-ISP aka multi-WAN aka multiple
simultaneous uplink connections) with active-active (load balancing) or
active-passive (failover) configuration.


## Configuration with static ISP routes

This example requires static ISP routes. It works with NetworkManager and
systemd-networkd. Both active-active and active-passive configurations are
supported. Both configuration types are very similar, with only one line
changed.

This example configuration assumes:

* ISP #1 is network interface `enp1s0`, my own IP is 172.23.70.36/24, gateway
  is 172.23.70.254. Traffic will be marked with value 0x100 and uses route
  table 1001.
* ISP #2 is network interface `enp2s0`, my own IP is 172.23.12.31/24, gateway
  is 172.23.12.254. Traffic will be marked with value 0x200 and uses route
  table 1002.
* Zone `internal` network interface is `enp8s0`, with network 10.0.0.0/8.
  Outgoing traffic to `public` zone is masqueraded.

Example `foomuuri.conf` file:

```
# Basic configuration:

zone {
  # Define zones with interfaces
  localhost
  public     enp1s0 enp2s0
  internal   enp8s0
}

foomuuri {
  # Reverse path filtering must be disabled for public interfaces
  rpfilter -enp1s0 -enp2s0
}

snat {
  # Masquerade outgoing traffic from internal to public. Both ISPs must be
  # masqueraded separately.
  saddr 10.0.0.0/8 oifname enp1s0 masquerade
  saddr 10.0.0.0/8 oifname enp2s0 masquerade
}

# Multi-ISP magic is here, using marks to select which ISP to use. Order
# of the rules is important. Specific rules should be first, generic last.

prerouting {
  # Accept if mark is already set (not zero). Existing mark will be used.
  mark_match -0x0000/0xff00

  # == Incoming traffic ==

  # Mark traffic from enp1s0 as 0x100 (ISP1) and enp2s0 as 0x200 (ISP2).
  # This is needed for correctly routing reply packets.
  iifname enp1s0 mark_set 0x100/0xff00
  iifname enp2s0 mark_set 0x200/0xff00

  # == Outgoing traffic ==

  # Specific rules should be added first. For example, uncomment next line to
  # route all SSH traffic from internal to public via ISP2.
  #iifname enp8s0 ssh mark_set 0x200/0xff00

  # Similarly, some source IPs can always be routed via ISP1.
  #saddr 10.0.1.0/24 mark_set 0x100/0xff00

  # For active-active configuration use following line. It uses random number
  # generator to mark traffic with 0x100 or 0x200. This routes 60% (0-5)
  # of outgoing traffic to ISP1 and 40% (6-9) to ISP2.
  nft "meta mark set numgen random mod 10 map { 0-5: 0x100, 6-9: 0x200 } ct mark set meta mark accept"

  # For active-passive configuration uncomment next line and add comment to
  # above nft-line. It simply assigns mark 0x100 (ISP1) to all traffic and
  # uses ISP2 only as fallback.
  #mark_set 0x100/0xff00
}

# foomuuri-monitor config:

target isp1 {
  # Monitor ISP1 connectivity by pinging 8.8.4.4. Ideally this would be
  # some ISP1's router's IP address.
  command      fping --iface enp1s0 8.8.4.4
  command_up   /etc/foomuuri/multi-isp up 1
  command_down /etc/foomuuri/multi-isp down 1
}

target isp2 {
  # Monitor ISP2 connectivity by pinging their router 172.25.31.149.
  command      fping --iface enp2s0 172.25.31.149
  command_up   /etc/foomuuri/multi-isp up 2
  command_down /etc/foomuuri/multi-isp down 2
}

# Normal zone-zone rules, copied from router firewall example configuration:

public-localhost {
  ping saddr_rate "5/second burst 20"
  ssh saddr_rate "5/minute burst 5"
  drop log
}

internal-localhost {
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
  template outgoing_services
  reject log
}

internal-public {
  template outgoing_services
  googlemeet
  imap
  reject log
}

public-internal {
  drop log
}

localhost-internal {
  dhcp-client
  dhcpv6-client
  ping
  ssh
  reject log
}
```

Example `/etc/foomuuri/multi-isp` script. Remember to save it as executable,
`chmod 750 /etc/foomuuri/multi-isp`.

``` bash
#!/bin/sh

# Path to "ip" command
IP=/usr/sbin/ip

case "${1}" in
    "start")
        # Started, run by foomuuri-multi-isp.service
        echo "Foomuuri multi-ISP start"

        # Create new route tables for both ISPs having default route
        ${IP} route add table 1001 default dev enp1s0 via 172.23.70.254
        ${IP} route add table 1002 default dev enp2s0 via 172.23.12.254

        # Delete default routes from main table
        ${IP} route del table main default dev enp1s0 via 172.23.70.254
        ${IP} route del table main default dev enp2s0 via 172.23.12.254

        # Start rules with main-table lookup
        ${IP} rule add prio 1000 from all table main

        # Packets with specific source IP must go to correct ISP
        ${IP} rule add prio 1001 from 172.23.70.36 table 1001
        ${IP} rule add prio 1002 from 172.23.12.31 table 1002

        # Other ISP-specific rules will be added by monitor's up-event.
        ;;

    "stop")
        # Stopped, run by foomuuri-multi-isp.service
        echo "Foomuuri multi-ISP stop"

        # Add default route back to main table
        ${IP} route add table main default dev enp1s0 via 172.23.70.254 metric 100
        ${IP} route add table main default dev enp2s0 via 172.23.12.254 metric 101

        # Delete added rules
        ${IP} rule del prio 1000
        ${IP} rule del prio 1001
        ${IP} rule del prio 1002
        ${IP} rule del prio 1101 2> /dev/null
        ${IP} rule del prio 1102 2> /dev/null
        ${IP} rule del prio 1201 2> /dev/null
        ${IP} rule del prio 1202 2> /dev/null

        # Delete added route tables
        ${IP} route flush table 1001
        ${IP} route flush table 1002
        ;;

    "up")
        # ISP is up, add rules to route traffic to it
        echo "Foomuuri multi-ISP isp${2} up"
        # Use packet mark to select this ISP
        ${IP} rule add prio 110${2} from all fwmark 0x${2}00/0xff00 table 100${2}
        # Fallback to this ISP if other is down
        ${IP} rule add prio 120${2} from all table 100${2}
        ;;

    "down")
        # ISP is down, delete its rules
        echo "Foomuuri multi-ISP isp${2} down"
        ${IP} rule del prio 110${2}
        ${IP} rule del prio 120${2}
        ;;

    *)
        echo "syntax error"
        exit 1
esac
```

Example `/etc/systemd/system/foomuuri-multi-isp.service` file. Remember to
enable it with `systemctl enable foomuuri-multi-isp.service`.

``` systemd
[Unit]
Description=Multizone bidirectional nftables firewall - Multi-ISP
Documentation=https://foomuuri.foobar.fi/latest/
After=network-online.target
Requires=network-online.target
PartOf=foomuuri.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/etc/foomuuri/multi-isp start
ExecStop=/etc/foomuuri/multi-isp stop

[Install]
WantedBy=multi-user.target
```


## Configuration with routes dynamically allocated by ISPs

This example configuration assumes:

* ISP #1 is on the network interface `enp1s0` with routes and IP addresses allocated via DHCP/IPv6RA. Traffic will be marked with value 0x100.
* ISP #2 is on the network interface `enp2s0` with routes and IP addresses allocated via DHCP/IPv6RA. Traffic will be marked with value 0x200.
* Zone `internal` network interface is `enp8s0` with IP 10.0.0.1/24. Outgoing traffic to `public` zone is masqueraded.
* At least the public interfaces and their routing tables will be managed by `systemd-networkd`.
* This example demonstrates a purely failover setup from ISP #1 to ISP #2. For load balancing add a second target monitor for `enp2s0` in `foomuuri.conf` and adjust the `switch.sh` script to identify and replace the fwmark randomizer as documented in the static routes example above.

Initiate the routing tables by creating the following two files.

`/etc/systemd/networkd.conf.d/table-primary.conf`:

```
[Network]
RouteTable=primary:100
```

`/etc/systemd/networkd.conf.d/table-secondary.conf`:

```
[Network]
RouteTable=secondary:200
```

Configure `enp1s0` as followed in `/etc/systemd/network/enp1s0.network`:

```
[Match]
Name=enp1s0

[Network]
DHCP=yes
IPv6AcceptRA=yes

[DHCPv4]
RouteTable=primary

[IPv6AcceptRA]
RouteTable=primary

[RoutingPolicyRule]
FirewallMark=0x100/0xff00
Family=both
Table=primary
Priority=40100

[RoutingPolicyRule]
Family=both
Table=primary
Priority=41000
```

Configure `enp2s0` as followed in `/etc/systemd/network/enp2s0.network`:

```
[Match]
Name=enp2s0

[Network]
DHCP=yes
IPv6AcceptRA=yes

[DHCPv4]
RouteTable=secondary

[IPv6AcceptRA]
RouteTable=secondary

[RoutingPolicyRule]
FirewallMark=0x200/0xff00
Family=both
Table=secondary
Priority=40200

[RoutingPolicyRule]
Family=both
Table=secondary
Priority=42000
```

After a restart of `systemd-networkd` the `ip route show table main` command should show this output:

`10.0.0.0/24 dev enp8s0 proto kernel scope link src 10.0.0.1`

As you can see no default route is defined in the main routing table because `systemd-networkd` added them only to our separate primary and secondary tables as defined above. This can be confirmed by checking the outputs of `ip route show table 100` and `ip route show table 200`. You should see the routes added via DHCP (`ip -6 route show table 100` for ipv6 router advertisement).

`ip rule` should output something like this:

```
0:	from all lookup local
32766:	from all lookup main
32767:	from all lookup default
40100:	from all fwmark 0x100/0xff00 lookup 100 proto static
40200:	from all fwmark 0x200/0xff00 lookup 200 proto static
41000:	from all lookup 100 proto static
42000:	from all lookup 200 proto static
```

The catchall rules `41000` and `42000` are needed so `localhost` knows where to lookup the default routes.

Now all that is missing is to configure Foomuuri to use the `fwmark` rules.

Example `foomuuri.conf` file:

```
zone {
  localhost
  internal enp8s0
  public   enp1s0 enp2s0
}

foomuuri {
  rpfilter -enp1s0 -enp2s0
}

snat {
  oifname enp1s0 masquerade
  oifname enp2s0 masquerade
}

prerouting {
  mark_match -0x0000/0xff00
  iifname enp1s0 mark_set 0x100/0xff00
  iifname enp2s0 mark_set 0x200/0xff00
}

target main {
  command fping --iface enp1s0 8.8.8.8
  command_up /etc/foomuuri/switch.sh up
  command_down /etc/foomuuri/switch.sh down
}

zone-zone rules...
```

If the `fping` monitor recognizes no uplink on the main interface `enp1s0` the following `switch.sh` script (remember to `chmod 750`) will set the default fwmark to 0x200 from the backup interface `enp2s0` by directly manipulating the nft prerouting chain.

``` bash
#!/bin/bash

case "$1" in
    up)
        echo "main is up"

        FWMARK="0x00000100"
        FWMASK="0xffff01ff"
        ;;
    down)
        echo "main is down"

        FWMARK="0x00000200"
        FWMASK="0xffff02ff"
        ;;
    *)
        echo "syntax error"
        exit 1
esac

HANDLE="$(
    nft --handle list chain inet foomuuri filter_prerouting_mangle |
    grep --only-matching --perl-regexp '^\s+meta mark set meta mark.*handle\s\K([0-9]+)$'
)"

if [[ $HANDLE ]]
then
    echo "catchall fwmark rule with handle $HANDLE found"

    nft replace rule inet foomuuri filter_prerouting_mangle handle "$HANDLE" \
        meta mark set meta mark \& "$FWMASK" \| "$FWMARK" \
        ct mark set meta mark accept

    echo "replaced handle $HANDLE with new fwmark ${FWMARK}/${FWMASK}"
else
    echo "no existing catchall fwmark rule found"

    nft add rule inet foomuuri filter_prerouting_mangle \
        meta mark set meta mark \& "$FWMASK" \| "$FWMARK" \
        ct mark set meta mark accept

    echo "added catchall fwmark ${FWMARK}/${FWMASK}"
fi
```
