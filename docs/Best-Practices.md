# Best Practices

## Configuration files

Foomuuri reads configuration files from `/etc/foomuuri/*.conf` in alphabetical
order, including all sub directories. Configuration can be written to single
or multiple files. Following is just a recommendation, not a rule:

* Simple configuration (less than 200 lines) in single
  `/etc/foomuuri/foomuuri.conf` file.
* Large configuration should be split to `/etc/foomuuri/foomuuri.conf`,
  `/etc/foomuuri/localhost.conf` , `/etc/foomuuri/public.conf` etc. files.
  * `foomuuri.conf` contains everything but zone-zone sections.
  * `localhost.conf` contains all xxx-localhost sections (or localhost-xxx).
  * `public.conf` contains all xxx-public sections (or public-xxx).
* Subdirectories can be used, for example
  `/etc/foomuuri/zones.d/localhost.conf`.
* Very large configuration could be split to multiple `localhost-public.conf`
  etc. files, containing only single zone-zone section per file.


## Zone names

Following zones names are recommended, but you can use whatever you want to.

### localhost

`localhost` is the zone name for the computer running Foomuuri, similar to
"localhost" in hostnames. If you decide to use some other name then you must
configure it in [foomuuri { localhost_zone }](Configuration.md#foomuuri) section.

### public

`public` is the default external network zone, similar to "internet". Basic
host firewall has only `localhost` and `public` zones. If you decide to use
some other name then you should also configure it in
[foomuuri { dbus_zone }](Configuration.md#foomuuri) section.

`public` is for use in public areas. You do not trust the other computers on
networks to not harm your computer.

### home

Similar to `public`, but for use in home areas. You mostly trust the other
computers on networks to not harm your computer.

### work

Similar to `public`, but for use in work areas. You mostly trust the other
computers on networks to not harm your computer.

### internal

`internal` is your internal network ("intranet") zone for router firewall
configurations. Remote connections from `public` should not be allowed to
`internal`.

### dmz

Demilitarized zone is publicly-accessible part of your internal network.
Only selected incoming connections should be accepted from `public` to `dmz`,
for example `https`.

### vpn

IPsec and similar VPN traffic.


## GNOME

NetworkManager supports dynamically [mapping](Configuration.md#zone) connections
with firewall zones but graphical connection editor GNOME Control Center
doesn't. There are two alternative ways to edit connections with zone support:

* Use graphical `nm-connection-editor` (recommended)
* Use command line `nmcli connection modify <connection-name> connection.zone <zone-name>`

This needs to be done only when changing firewall zone for connection. All
other edits can be done with GNOME Control Center.


## Proxy ARP

See [discussions](https://github.com/FoobarOy/foomuuri/discussions/2)
how to configure proxy ARP with Foomuuri using [hooks](Configuration.md#hook).


## Hairpin NAT / NAT Loopback

See [issues](https://github.com/FoobarOy/foomuuri/issues/8) how to configure
hairpin NAT with Foomuuri using [snat](Configuration.md#snat) and
[dnat](Configuration.md#dnat).

Usually it is better to do split DNS instead of hairpin NAT. Split DNS has
locally served zone with local IP addresses and publicly served zone with
public IP addresses.


## fail2ban

See [issues](https://github.com/FoobarOy/foomuuri/issues/9) how to integrate
with `fail2ban`.


## Custom nftables chains

See [discussions](https://github.com/FoobarOy/foomuuri/discussions/31)
how to define custom nftables chains and how to jump to them.


## QEMU/libvirt and vnet interfaces

See [discussions](https://github.com/FoobarOy/foomuuri/discussions/15) how
to silently drop `OUTPUT REJECT IN= OUT=vnetXX` log entries.


## Don't route private networks to public internet

See [issues](https://github.com/FoobarOy/foomuuri/issues/24) how to block
routing 10.0.0.0/8 and similar private networks to public internet.


## Multi-ISP

Foomuuri supports multiple ISPs (aka multi-WAN aka multiple simultaneous
uplink connections) with active-active (load balancing) or active-passive
(failover) configuration. Both configuration types are very similar, with
only one line changed.

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

case "${1}" in
    "start")
        # Started, run by foomuuri-multi-isp.service
        echo "Foomuuri multi-ISP start"

        # Create new route tables for both ISPs having default route
        ip route add table 1001 default dev enp1s0 via 172.23.70.254
        ip route add table 1002 default dev enp2s0 via 172.23.12.254

        # Delete default routes from main table
        ip route del table main default dev enp1s0 via 172.23.70.254
        ip route del table main default dev enp2s0 via 172.23.12.254

        # Start rules with main-table lookup
        ip rule add prio 1000 from all table main

        # Packets with specific source IP must go to correct ISP
        ip rule add prio 1001 from 172.23.70.36 table 1001
        ip rule add prio 1002 from 172.23.12.31 table 1002

        # Other ISP-specific rules will be added by monitor's up-event.
        ;;

    "stop")
        # Stopped, run by foomuuri-multi-isp.service
        echo "Foomuuri multi-ISP stop"

        # Add default route back to main table
        ip route add table main default dev enp1s0 via 172.23.70.254 metric 100
        ip route add table main default dev enp2s0 via 172.23.12.254 metric 101

        # Delete added rules
        ip rule del prio 1000
        ip rule del prio 1001
        ip rule del prio 1002
        ip rule del prio 1101 2> /dev/null
        ip rule del prio 1102 2> /dev/null
        ip rule del prio 1201 2> /dev/null
        ip rule del prio 1202 2> /dev/null

        # Delete added route tables
        ip route flush table 1001
        ip route flush table 1002
        ;;

    "up")
        # ISP is up, add rules to route traffic to it
        echo "Foomuuri multi-ISP isp${2} up"
        # Use packet mark to select this ISP
        ip rule add prio 110${2} from all fwmark 0x${2}00/0xff00 table 100${2} 2> /dev/null
        # Fallback to this ISP if other is down
        ip rule add prio 120${2} from all table 100${2} 2> /dev/null
        ;;

    "down")
        # ISP is down, delete its rules
        echo "Foomuuri multi-ISP isp${2} down"
        ip rule del prio 110${2}
        ip rule del prio 120${2}
        ;;

    *)
        echo "syntax error"
        exit 1
esac
```

Example `/etc/systemd/system/foomuuri-multi-isp.service` file. Remember to
enable it with `systemctl enable foomuuri-multi-isp.service`.

```
[Unit]
Description=Multizone bidirectional nftables firewall - Multi-ISP
Documentation=https://github.com/FoobarOy/foomuuri/wiki
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
