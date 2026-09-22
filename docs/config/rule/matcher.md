# Matchers


## tcp, udp, icmp, icmpv6

Matches TCP, UDP, ICMP, or ICMPv6 traffic. This matcher is usually
followed by a port number; for example, `tcp 443` matches TCP traffic to
port 443 (HTTPS). Without a port number, all traffic is matched. See
[protocol](matcher.md#protocol) for how to match other protocols.

Rather than using `tcp 443` directly, it is recommended to use the
predefined `https` macro. All
[known macros](https://github.com/FoobarOy/foomuuri/blob/main/etc/default.services.conf)
can be listed with `foomuuri macro list`.


## sport, dport

Matches the source/destination port, followed by a port number. The
`dport` matcher is usually optional: `tcp 443` is equivalent to
`tcp dport 443`.

Port number can be:

* Single number, `443`
* Multiple numbers, `80 443`, matching 80 or 443
* Range, `8880-9000`
* Range and a number, `80 443 8880-9000`
* Negative number, `-443`, matching everything but 443
* Multiple negative numbers, `-80 -443`, matching everything but 80 or 443


## saddr, daddr

Matches the source/destination IPv4 or IPv6 address.

An address can be:

* Single IPv4 address, `10.0.0.1`
* Single IPv6 address, `fd00:f00::1`
* Address with a netmask, `10.0.0.0/8` or `fd00:f00::/32`
* IPv6 address with a suffix netmask, `::10:0:0:f00/-64`, to match with
  the netmask `::ffff:ffff:ffff:ffff`
* Interval, `10.0.0.10-10.0.0.20` or `fd00:f00::10-fd00:f00::20`
* Multiple addresses, `10.0.0.1 10.0.0.10-10.0.0.20 fd00:f00::/32`. Both
  IPv4 and IPv6 addresses can be listed in the same rule; Foomuuri
  automatically splits them into the correct traffic chains.
* Negative address, `-10.0.0.1` or `-fd00:f00::1`, meaning all other
  addresses
* Negative IPv6 address with a suffix netmask, `-::10:0:0:f00/-64`
* Multiple negative addresses, `-10.0.0.1 -fd00:f00::1`
* Iplist set name, `@listname`
* Negative iplist set name, `-@listname`

This matcher is usually combined with the `tcp port` matcher to allow
traffic from a specific source IP only, `tcp 443 saddr 10.0.0.1`, or to a
specific destination IP.


## mac_saddr, mac_daddr

Matches the source/destination MAC address for incoming traffic. This
does not work for outgoing traffic.

An address can be:

* Single MAC address, `01:23:45:67:89:ab`
* Multiple MAC addresses, `01:23:45:67:89:ab 01:23:45:67:89:cc`
* Negative MAC address, `-01:23:45:67:89:ab`, meaning all other addresses
* Multiple negative MAC addresses, `-01:23:45:67:89:ab -01:23:45:67:89:cc`

Example:

```
internal-localhost {
  # Drop spoofed traffic from 10.0.0.3
  saddr 10.0.0.3 mac_saddr -12:00:27:00:00:ce drop log "MAC-SPOOF"
  ...
}
```


## iifname, oifname

Matches the incoming/outgoing interface name. This is mostly used in the
`snat`, `dnat`, and `zonemap` sections. For example, in `snat`,
`saddr 10.0.0.0/8 oifname eth0 masquerade` matches all traffic coming from
10.0.0.0/8 that is going out via eth0, and masquerades it.

Multiple interface names can be specified. Negative interface name(s) can
also be used, meaning all but the specified name(s).


## ipv4, ipv6

A single rule applies to both IPv4 and IPv6 traffic by default. Adding an
`ipv4` or `ipv6` matcher to a rule limits it to IPv4 or IPv6 only.


## multicast, broadcast

Matches multicast or broadcast traffic. Foomuuri silently drops all
incoming multicast and broadcast traffic unless it is explicitly accepted
by a rule.

The Linux kernel can match multicast/broadcast only for incoming traffic.
Therefore, Foomuuri generates the outgoing nft rule without the
multicast/broadcast matcher, even if one was specified in the rule. This
makes it easy to use the same rule or macro for all traffic, regardless of
whether it is incoming or outgoing.

The rule `broadcast udp 11430` allows incoming broadcast messages to UDP
port 11430, and all outgoing traffic to UDP port 11430. The rule
`multicast` allows all incoming multicast traffic, and nothing for
outgoing. It is highly recommended to always specify `daddr` for multicast
rules.

Example:

```
public-localhost {
  # Allow all incoming multicast traffic
  multicast
  ...
}

localhost-public {
  # Allow some outgoing multicast addresses. This rule can also be written
  # without the "multicast" matcher, since it is omitted for outgoing
  # traffic anyway.
  multicast daddr 224.0.0.0/8 239.0.0.0/8 ff00::/8
  ...
}
```

It is much better to accept only specific multicast/broadcast traffic
rather than everything. For example, the `ssdp` macro is defined as:

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

This macro allows incoming traffic to specific multicast addresses and UDP
port 1900, outgoing traffic to the same addresses and port, and finally
unicast traffic from the same port.


## protocol

Matches traffic for a specific protocol. For example, `protocol gre`
matches all GRE traffic, and `protocol sctp 22` matches SCTP traffic to
port 22.

For TCP, UDP, ICMP, and ICMPv6, it is recommended to use the
[shortcut](matcher.md#tcp-udp-icmp-icmpv6) matchers instead.


## sipsec, dipsec

Matches incoming/outgoing IPsec traffic. These are useful when you want to
allow traffic to or from IPsec without creating a separate `vpn` zone for
it. Example:

```
public-localhost {
  ssh              # Allow SSH with and without IPsec
  tcp 1234 sipsec  # Allow TCP 1234 with IPsec only
  ...
}
```

To split IPsec and non-IPsec traffic into `vpn` and `public` zones, you
can use these matchers in the `zonemap` [section](../section/zonemap.md).
It is usually unnecessary to create a separate zone for this.

The negative matchers `-sipsec` and `-dipsec` can also be used; they match
non-IPsec traffic. These are useful in the `snat` and `dnat`
[sections](../section/snat.md).


## uid, gid

Matches traffic generated by a given uid/gid. This only works for traffic
originating from `localhost`. For example, `tcp 2703 uid amavis` in the
`localhost-public` section allows outgoing TCP 2703 traffic from the user
`amavis`.

Multiple uid/gid names or numbers can be specified. Negative value(s) also
work, meaning all but the specified value(s).

Only the effective gid is matched; matching against supplementary groups
does not work.


## mark_match

Matches the packet's mark. The argument can be:

* Number, `42` or `0x2a`
* Number with a mask, `0x100/0xff00`, meaning check whether
  `mark and 0xff00` equals `0x100`
* Negative number, `-42`, meaning any mark other than `42`
* Negative number with a mask, `-0x0000/0xff00`, for a not-equal check


## mark_set

Sets the packet's mark. The argument can be:

* Number, `42` or `0x2a`
* Number with a mask, `0x100/0xff00`, meaning set the bits `0xff00` to
  `0x100`. In other words, this keeps the lower 8 bits as they are and
  sets the upper 8 bits.

This is not a normal matcher, since it matches everything. Usually, some
other matcher should be applied first. Example:

```
prerouting {
  iifname eth0 mark_set 0x100/0xff00  # Mark traffic from eth0 and accept it
  iifname eth1 mark_set 0x200/0xff00  # Mark traffic from eth1 and accept it
  mark_set 0x300/0xff00               # Mark all other traffic
}
```


## priority_match

Matches the packet's traffic control class ID. The argument can be:

* Class ID, `1:ff01` or `1:0xff01` (the `0x` is optional)
* Text `none`, for no priority set


## priority_set

Sets the packet's traffic control class ID.

This is not a normal matcher, since it matches everything. Usually, some
other matcher should be applied first. Example:

```
forward {
  daddr 192.168.0.0/16 priority_match none priority_set 1:ff01
  saddr 192.168.0.0/16 priority_match none priority_set 1:ff01
  priority_match none priority_set 1:2
}
```


## iplist_add

Adds the packet's source or destination IP address to an
[iplist](../section/iplist.md), using the default `element_timeout`. The
timeout is not updated if the IP address is already in the iplist. Two
arguments are required: `saddr` or `daddr`, and the iplist `@name`.

`iplist_update` is usually the better choice, since it updates the
timeout.


## iplist_update

Adds or updates the packet's source or destination IP address in an
[iplist](../section/iplist.md), using the default `element_timeout`. The
timeout is updated if the IP address is already in the iplist. Two
arguments are required: `saddr` or `daddr`, and the iplist `@name`.

See [port knocking](../../example/advanced.md#port-knocking) and automatic
IP address [banning](../../example/advanced.md#automatic-ip-address-banning)
for examples.


## iplist_delete

Deletes the packet's source or destination IP address from an
[iplist](../section/iplist.md). Two arguments are required: `saddr` or
`daddr`, and the iplist `@name`.

See [port knocking](../../example/advanced.md#port-knocking) for an
example.


## ct_status

Matches the packet's conntrack status, mostly used with
[SNAT or DNAT](../section/dnat.md). Valid arguments are: expected,
seen-reply, assured, confirmed, snat, dnat, dying.


## cgroup

Matches a cgroup ID or cgroupv2 name. The argument can be:

* Single number, `1234`
* Multiple numbers, `1234 1244`
* Range, `4000-5000`
* Range and a number, `1234 1244 4000-5000`
* Negative number, `-1234`, matching everything but 1234
* Multiple negative numbers, `-1234 -1244`, matching everything but 1234
  or 1244
* cgroupv2 name, `user.slice` or `system.slice/sshd.service`

**Warning**: A cgroupv2 must exist before Foomuuri starts. Since Foomuuri
starts very early during boot, using this feature incorrectly can break
your firewall startup.


## time

Matches the current time, date, and day of the week. The argument can be:

* Time, `hh:mm` or `hh:mm:ss`
* Time interval, `hh:mm-hh:mm` (see the warning below)
* Date, `yyyy-mm-dd`
* Day of the week: `Monday`, `Tuesday`, `Wednesday`, `Thursday`,
  `Friday`, `Saturday`, `Sunday`
* Comparison operator: `==` (equal, the default), `!=` (not equal),
  `<`, `>`, `<=`, `>=`
* Any combination of the above

**Warning**: Some versions of `nft` do not correctly handle a time
interval that crosses midnight UTC. If your timezone is +03:00, the
interval `23:00-02:00` works, but `02:00-06:00` fails.

Example:

```
public-localhost {
  # Allow until the year 2025
  tcp 1234 time "< 2025-01-01"

  # Kids, go to bed! Reject traffic at night.
  saddr @kids time "23:00-07:00" reject

  # An unusual combination: allow traffic on Mondays from 16:00-22:00,
  # until the year 2025
  tcp 5001 time "Monday 16:00-22:00 < 2025-01-01"
}
```


## dscp

Matches the packet's Differentiated Services Code Point (DSCP) value.
Example:

```
internal-public {
  saddr 10.0.0.4 dscp 10
  dscp af13
}
```


## tproxy

Transparent proxy traffic to an IP address:port. Example:

```
prerouting {
  # Use the lower 8 bits to mark tproxy traffic
  mark_match -0x00/0xff  # Anti-loop protection

  # All IPv4 and IPv6 TCP traffic
  tcp tproxy 127.0.0.1:8888 [::1]:8888 mark_set 0x01/0xff
}
```
