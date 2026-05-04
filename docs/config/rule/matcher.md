# Matchers


## tcp, udp, icmp, icmpv6

Matches TCP / UDP / ICMP / ICMPv6 traffic. This matcher is usually followed by
port number. For example `tcp 443` matches TCP traffic to port 443 (https).
Without port number all traffic is matched. See [protocol](matcher.md#protocol)
how to match other protocols.

Instead of using `tcp 443` it is recommended to use pre-defined `https`
macro. All
[known macros](https://github.com/FoobarOy/foomuuri/blob/main/etc/default.services.conf)
can be listed with `foomuuri list macro` command.


## sport, dport

Matches source / destination port, followed by port number. `dport` matcher is
usually optional: `tcp 443` is equal to `tcp dport 443`.

Port number can be:

* Single number `443`
* Multiple numbers `80 443`, matching 80 or 443
* Range `8880-9000`
* Range and number `80 443 8880-9000`
* Negative number `-443`, matching all but 443
* Multiple negative numbers `-80 -443`, matching all but 80 or 443


## saddr, daddr

Matches source / destination IPv4 or IPv6 address.

Address can be

* Single IPv4 address `10.0.0.1`
* Single IPv6 address `fd00:f00::1`
* Address with netmask `10.0.0.0/8` or `fd00:f00::/32`
* IPv6 address with suffix netmask `::10:0:0:f00/-64` to match with netmask
  `::ffff:ffff:ffff:ffff`
* Interval `10.0.0.10-10.0.0.20` or `fd00:f00::10-fd00:f00::20`
* Multiple addresses `10.0.0.1 10.0.0.10-10.0.0.20 fd00:f00::/32`.
  You can list both IPv4 and IPv6 addresses in same rule. Foomuuri will
  split them automatically to correct traffic chains.
* Negative address `-10.0.0.1` or `-fd00:f00::1`, meaning all other
  addresses.
* Negative IPv6 address with suffix netmask `-::10:0:0:f00/-64`
* Multiple negative addresses `-10.0.0.1 -fd00:f00::1`
* Iplist set name `@listname`
* Negative iplist set name `-@listname`

This matcher is usually combined with `tcp port` matcher to allow traffic
from specific source IP only, `tcp 443 saddr 10.0.0.1`, or to specific
destination IP.


## mac_saddr, mac_daddr

Matches source / destination MAC address for incoming traffic. This doesn't
work for outgoing traffic.

Address can be:

* Single MAC address `01:23:45:67:89:ab`
* Multiple MAC addresses `01:23:45:67:89:ab 01:23:45:67:89:cc`
* Negative MAC address `-01:23:45:67:89:ab`, meaning all other addresses.
* Multiple negative MAC addresses `-01:23:45:67:89:ab -01:23:45:67:89:cc`

Example:

```
internal-localhost {
  # drop spoofed traffic from 10.0.0.3
  saddr 10.0.0.3 mac_saddr -12:00:27:00:00:ce drop log "MAC-SPOOF"
  ...
}
```


## iifname, oifname

Matches incoming / outgoing interface name. This is used mostly on `snat`,
`dnat` and `zonemap` sections. For example in snat
`saddr 10.0.0.0/8 oifname eth0 masquerade` will match all traffic coming
from 10.0.0.0/8, going to eth0, and masquerades it.

Multiple interface names can be specified. Negative interface name(s) works
too, meaning all but specified name(s).


## ipv4, ipv6

Single rule will apply to both IPv4 and IPv6 traffic. Adding
`ipv4` or `ipv6` matcher to rule will limit it to IPv4 or IPv6 only.


## multicast, broadcast

Matches multicast or broadcast traffic. Foomuuri will silently drop all
incoming multicast and broadcast traffic unless explicitly accepted by rule.

Linux kernel can match multicast/broadcast only in incoming traffic.
Therefore Foomuuri generates outgoing nft rule without multicast/broadcast
matcher even if one was specified in the rule. This makes it easy to use same
rule or macro for all traffic, no matter if it's incoming or outgoing.

Rule `broadcast udp 11430` allows incoming broadcast messages to UDP port
11430, or all outgoing traffic to UDP port 11430. Rule `multicast` allows all
incoming multicasts, nothing for outgoing. It is highly recommended to always
specify `daddr` for multicast rules.

Example:

```
public-localhost {
  # Allow all incoming multicasts
  multicast
  ...
}

localhost-public {
  # Allow some outgoing multicast addresses. This rule can also be written
  # without "multicast" matcher as it will be omitted.
  multicast daddr 224.0.0.0/8 239.0.0.0/8 ff00::/8
  ...
}
```

It is much better to accept specific multicast/broadcast only, not everything.
For example macro `ssdp` is defined as:

```
macro {
  ssdp    multicast udp 1900 daddr 239.255.255.250 ff02::c; udp sport 1900
}

public-localhost {
  # Allow incoming ssdp
  ssdp
  ...
}

localhost-public {
  # Allow outgoing ssdp
  ssdp
  ...
}
```

Above macro allows incoming traffic to specific multicast addresses and UDP
port 1900, outgoing traffic to same addresses and port, and finally unicast
from same port.


## protocol

Matches specific protocol traffic. For example `protocol gre` will match all
GRE traffic and `protocol sctp 22` will match SCTP traffic to port 22.

For TCP, UDP, ICMP and ICMPv6 protocols it is recommended to use
[shortcut](matcher.md#tcp-udp-icmp-icmpv6) matchers.


## sipsec, dipsec

Matches incoming / outgoing IPsec traffic. These are useful if you want to
allow traffic from/to IPsec without creating a new `vpn` zone for them.
Example:

```
public-localhost {
  ssh              # Allow SSH with and without IPsec
  tcp 1234 sipsec  # Allow TCP 1234 with IPsec only
  ...
}
```

To split IPsec and non-IPsec traffic to `vpn` and `public` zones you can
use these matchers in `zonemap` [section](../section/zonemap.md). Usually
it is not necessary to create separate zone for that.

Negative matchers `-sipsec` and `-dipsec` can also be used. They match
non-IPsec traffic. These are useful in `snat` and `dnat`
[sections](../section/snat.md).


## uid, gid

Matches traffic generated by uid / gid user. This works only for traffic
from `localhost`. For example `tcp 2703 uid amavis` in `localhost-public`
section allows outgoing TCP 2703 traffic from user `amavis`.

Multiple uid / gid names or numbers can be specified. Negative value(s)
works too, meaning all but specified value(s).


## mark_match

Matches packet's mark. Argument can be:

* Number `42` or `0x2a`
* Number with mask `0x100/0xff00`, meaning check if `mark and 0xff00` is
  equal to `0x100`
* Negative number `-42`, meaning all other marks than `42`
* Negative number with mask `-0x0000/0xff00` for non-equal check


## mark_set

Set packet's mark. Argument can be:

* Number `42` or `0x2a`
* Number with mask `0x100/0xff00`, meaning set bits `0xff00` to `0x100`. In
  other words, this keeps lower 8 bits as they are and sets upper 8 bits.

This is not normal matcher as it matches everything. Usually some other
matcher should be used first. Example:

```
prerouting {
  iifname eth0 mark_set 0x100/0xff00  # Mark traffic from eth0 and accept it
  iifname eth1 mark_set 0x200/0xff00  # Mark traffic from eth1 and accept it
  mark_set 0x300/0xff00               # Mark all other traffic
}
```


## priority_match

Matches packet's traffic control class id. Argument can be:

* Class id `1:ff01` or `1:0xff01` (`0x` is optional)
* Text `none` for no priority set


## priority_set

Set packet's traffic control class id.

This is not normal matcher as it matches everything. Usually some other
matcher should be used first. Example:

```
forward {
  daddr 192.168.0.0/16 priority_match none priority_set 1:ff01
  saddr 192.168.0.0/16 priority_match none priority_set 1:ff01
  priority_match none priority_set 1:2
}
```


## iplist_add

Add packet source or destination IP address to
[iplist](../section/iplist.md), using default `element_timeout`.
Timeout is not updated if IP address is already in iplist.
Two arguments are needed: `saddr` or `daddr`, and iplist `@name`.

Normally `iplist_update` is a better choice as it updates timeout.


## iplist_update

Add/update packet source or destination IP address to
[iplist](../section/iplist.md), using default `element_timeout`.
Timeout will be updated if IP address is already in iplist.
Two arguments are needed: `saddr` or `daddr`, and iplist `@name`.

See [port knocking](../../example/advanced.md#port-knocking)
and automatic IP address
[banning](../../example/advanced.md#automatic-ip-address-banning)
for examples.


## iplist_delete

Delete packet source or destination IP address from
[iplist](../section/iplist.md).
Two arguments are needed: `saddr` or `daddr`, and iplist `@name`.

See [port knocking](../../example/advanced.md#port-knocking) for example.


## ct_status

Matches packet's conntrack status, mostly used with
[SNAT or DNAT](../section/dnat.md). Valid arguments are: expected,
seen-reply, assured, confirmed, snat, dnat, dying.


## cgroup

Matches cgroup id or cgroupv2 name. Argument can be:

* Single number `1234`
* Multiple numbers `1234 1244`
* Range `4000-5000`
* Range and number `1234 1244 4000-5000`
* Negative number `-1234`, matching all but 1234
* Multiple negative numbers `-1234 -1244`, matching all but 1234 or 1244
* cgroupv2 name `user.slice` or `system.slice/sshd.service`

**Warning**: cgroupv2 must exist before starting Foomuuri. As Foomuuri starts
very early on boot using this feature incorrectly can break your firewall
startup.


## time

Matches current time, date and day of the week. Argument can be:

* Time `hh:mm` or `hh:mm:ss`
* Time interval `hh:mm-hh:mm` (see warning below)
* Date `yyyy-mm-dd`
* Day of the week: `Monday`, `Tuesday`, `Wednesday`, `Thursday`,
 `Friday`, `Saturday`, `Sunday`
* Compare function: `==` (equal, the default), `!=` (not equal), `<`, `>`,
  `<=`, `>=`
* Combination of above

**Warning**: Some versions of `nft` do not handle time interval crossing
midnight UTC. If your timezone is +03:00, interval `23:00-02:00` works
but `02:00-06:00` fails.

Example:

```
public-localhost {
  # Allow until year 2025
  tcp 1234 time "< 2025-01-01"

  # Kids, go to bed! Reject traffic at night time.
  saddr @kids time "23:00-07:00" reject

  # Strange combination: Allow traffic on Mondays at 16-22, until year 2025
  tcp 5001 time "Monday 16:00-22:00 < 2025-01-01"
}
```


## dscp

Matches packet's differentiated services code point (DSCP) value. Example:

```
internal-public {
  saddr 10.0.0.4 dscp 10
  dscp af13
}
```


## tproxy

Transparent proxy traffic to ipaddress:port. Example:

```
prerouting {
  # Use lower 8 bits to mark tproxy traffic
  mark_match -0x00/0xff  # Anti-loop protection

  # All IPv4 and IPv6 TCP traffic
  tcp tproxy 127.0.0.1:8888 [::1]:8888 mark_set 0x01/0xff
}
```
