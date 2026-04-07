# Rule

Each line in configuration section is a single rule. Single rule contains
optional matching parts and statement part.


## Matchers


### tcp, udp, icmp, icmpv6

Matches TCP / UDP / ICMP / ICMPv6 traffic. This matcher is usually followed by
port number. For example `tcp 443` matches TCP traffic to port 443 (https).
Without port number all traffic is matched. See [protocol](Rule.md#protocol)
how to match other protocols.

Instead of using `tcp 443` it is recommended to use pre-defined `https`
macro. All
[known macros](https://github.com/FoobarOy/foomuuri/blob/main/etc/default.services.conf)
can be listed with `foomuuri list macro` command.


### sport, dport

Matches source / destination port, followed by port number. `dport` matcher is
usually optional: `tcp 443` is equal to `tcp dport 443`.

Port number can be:

* Single number `443`
* Multiple numbers `80 443`, matching 80 or 443
* Range `8880-9000`
* Range and number `80 443 8880-9000`
* Negative number `-443`, matching all but 443
* Multiple negative numbers `-80 -443`, matching all but 80 or 443


### saddr, daddr

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


### mac_saddr, mac_daddr

Matches source / destination MAC address for incoming traffic.
This doesn't work for outgoing traffic.

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


### iifname, oifname

Matches incoming / outgoing interface name. This is used mostly on `snat`,
`dnat` and `zonemap` sections. For example in snat
`saddr 10.0.0.0/8 oifname eth0 masquerade` will match all traffic coming
from 10.0.0.0/8, going to eth0, and masquerades it.

Multiple interface names can be specified. Negative interface name(s) works
too, meaning all but specified name(s).


### ipv4, ipv6

Single rule will apply to both IPv4 and IPv6 traffic. Adding
`ipv4` or `ipv6` matcher to rule will limit it to IPv4 or IPv6 only.


### multicast, broadcast

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


### protocol

Matches specific protocol traffic. For example
`protocol gre` will match all GRE traffic and `protocol sctp 22` will
match SCTP traffic to port 22.

For TCP, UDP, ICMP and ICMPv6 protocols it is recommended to use
[shortcut](Rule.md#tcp-udp-icmp-icmpv6) matchers.


### sipsec, dipsec

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
use these matchers in `zonemap` [section](Configuration.md#zonemap). Usually
it is not necessary to create separate zone for that.

Negative matchers `-sipsec` and `-dipsec` can also be used. They match
non-IPsec traffic. These are useful in `snat` and `dnat`
[sections](Configuration.md#snat).


### uid, gid

Matches traffic generated by uid / gid user. This works only for traffic
from `localhost`. For example `tcp 2703 uid amavis` in `localhost-public`
section allows outgoing TCP 2703 traffic from user `amavis`.

Multiple uid / gid names or numbers can be specified. Negative value(s)
works too, meaning all but specified value(s).


### mark_match

Matches packet's mark. Argument can be:

* Number `42` or `0x2a`
* Number with mask `0x100/0xff00`, meaning check if `mark and 0xff00` is
  equal to `0x100`
* Negative number `-42`, meaning all other marks than `42`
* Negative number with mask `-0x0000/0xff00` for non-equal check


### mark_set

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


### priority_match

Matches packet's traffic control class id. Argument can be:

* Class id `1:ff01` or `1:0xff01` (`0x` is optional)
* Text `none` for no priority set


### priority_set

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


### ct_status

Matches packet's conntrack status, mostly used with
[SNAT or DNAT](Configuration.md#dnat).
Valid arguments are: expected, seen-reply, assured, confirmed, snat, dnat,
dying.


### cgroup

Matches cgroup id or cgroupv2 name. Argument can be:

* Single number `1234`
* Multiple numbers `1234 1244`
* Range `4000-5000`
* Range and number `1234 1244 4000-5000`
* Negative number `-1234`, matching all but 1234
* Multiple negative numbers `-1234 -1244`, matching all but 1234 or 1244
* cgroupv2 name `user.slice` or `system.slice/sshd.service`

**Warning:** cgroupv2 must exist before starting Foomuuri. As Foomuuri starts
very early on boot using this feature incorrectly can break your firewall
startup.


### time

Matches current time, date and day of the week.
Argument can be:

* Time `hh:mm` or `hh:mm:ss`
* Time interval `hh:mm-hh:mm`
* Date `yyyy-mm-dd`
* Day of the week: `Monday`, `Tuesday`, `Wednesday`, `Thursday`,
 `Friday`, `Saturday`, `Sunday`
* Compare function: `==` (equal, the default), `!=` (not equal), `<`, `>`,
  `<=`, `>=`
* Combination of above

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


### dscp

Matches packet's differentiated services code point (DSCP) value.
Example:

```
internal-public {
  saddr 10.0.0.4 dscp 10
  dscp af13
}
```


### tproxy

Transparent proxy traffic to ipaddress:port. Example:

```
prerouting {
  # Use lower 8 bits to mark tproxy traffic
  mark_match -0x00/0xff  # Anti-loop protection

  # All IPv4 and IPv6 TCP traffic
  tcp tproxy 127.0.0.1:8888 [::1]:8888 mark_set 0x01/0xff
}
```


## Statements


### accept, drop, reject

Accepts, drops or rejects traffic. Default statement for single rule is to
accept matched traffic: `tcp 443` is equal to `tcp 443 accept`.

You should always add explicit final statement as last rule to every
[zone-zone](Configuration.md#zone-zone) section in your configuration.

* For incoming traffic from internet to localhost/intranet the recommended
  statement is `drop log`.
* For outgoing traffic from localhost/intranet to internet the recommended
  statement is `reject log`.


### continue

Continues to next rule. This is used mostly to debug
rules. For example rule `saddr 10.0.0.4 counter log continue` counts and
logs traffic from 10.0.0.4 and continues to next rule.


### return

This is a special statement to return from current nftables chain to caller
chain. Not normally used.


### masquerade, snat to, dnat to, snat_prefix to, dnat_prefix to

These statements are used in `snat` and `dnat` [sections](Configuration.md#snat)
to mangle traffic source or destination IP address.


### queue

Forward packet to userspace for example for IPS/IDS inspection.
Optional flags and target can be specified. Example:

```
forward {
   # Forward all packets to userspace for IPS inspection
   queue flags fanout,bypass to 3-5

   # Forward matching packets only
   iifname eth0 oifname eth1 queue
}
```


## Logging


### counter

Add byte and packet counter to rule. All traffic matching this rule will be
counted. Counter can be named or anonymous. To name a counter add name after
`counter`, for example `counter my_counter`.

Example:

```
localhost-public {
  # Add named counter to count all outgoing traffic
  counter outgoing_traffic continue -conntrack

  # Accept ssh and add anonymous counter for it
  ssh counter

  # Accept http + https and add named counter
  http counter web_traffic
  https counter web_traffic

  # Reject SMTP with named counter
  smtp reject counter smtp_blocked
}
```

Named counter values can be listed with `foomuuri list counter`. Anonymous
counters can be listed with `foomuuri list`.


### log

Write log entry (journal / syslog) when traffic matches this rule. Optional
log prefix can be added. Default prefix is "szone-dzone STATEMENT", for example
"localhost-public REJECT".

Following variables are supported in log prefix:

* `$(szone)`
* `$(dzone)`
* `$(statement)`

More text to default log prefix can be added with `log + "my text"`.

Example:

```
public-localhost {
  # Use default log prefix "public-localhost DROP"
  ssh drop log

  # Drop and log incoming http with custom prefix
  http drop log "incoming-http dropped"

  # Drop and log https with custom prefix with variables. This results to
  # prefix "public => localhost: DROP"
  https drop log "$(szone) => $(dzone): $(statement)"

  # Drop telnet with prefix "public-localhost DROP:telnet"
  telnet drop log + ":telnet"

  # Use default log prefix "public-localhost DROP"
  drop log
}
```

Foomuuri will limit logging to [log_rate](Configuration.md#foomuuri) rate.
Default value is to log first three entries per source IP and then one
additional entry per second.


### log_level

This overrides global `foomuuri { log_level ... }` logging level for this
single rule.

Possible values are:

* `level emerg`
* `level alert`
* `level crit`
* `level err`
* `level warn`
* `level notice`
* `level info`
* `level debug`

Optionally flags can be appended:

* `flags tcp sequence,options` enables logging of TCP sequence and options
* `flags ip options` enables IP options
* `flags skuid` enables socket UID
* `flags ether` enables ethernet link layer address
* `flags all` enables all flags

To use nflog infrastructure instead of syslog specify value `group 0` (or any
other number) instead of `level x`. Nflog options can be appended:

* `snaplen 256` specifies length of packet payload to include
* `queue-threshold 20` will queue packets inside the kernel before sending
  them to userspace

Example:

```
public-localhost {
  # Drop and log incoming http requests with critical level, all flags
  http drop log log_level "level crit flags all"
  ...
}
```


## Rate limit


### global_rate

Defines global rate limit without source or destination IP address check. For
example `https global_rate "10/second burst 20"` allows https traffic with
rate:

* First 20 new connections are allowed without limit.
* After burst is filled, up to 10 new connections per second are allowed.
* This rate is "global", meaning that one single source IP can use all allowed
  slots, or 20 sources can use one slot each.
* Here "connection" means new connection, not total number of established,
  active connections (see `ct count` below).

There are three types of rates:

* New connection rates (`x/time burst y`), ignoring if some of
  them have already been closed.

  * `"5/second"`
  * `"7/second burst 30"`
  * `"30/minute"`
  * `"50/minute burst 200"`
  * `"100/hour"`
  * `"100/hour burst 100"`
  * `"over 8/second burst 10"`

* Bandwidth rates (`x bytes/time burst y bytes`):

  * `"10 mbytes/second"`
  * `"10 mbytes/second burst 12000 kbytes"`
  * `"over 10 mbytes/second"`
  * `"over 10 mbytes/second burst 12000 kbytes"`

* Conntrack rates (`ct count x`) counting total number of established, active
  connections:

  * `"ct count 5"`
  * `"ct count over 6"`

New connection rate limit can be visualized as leaking water bucket.
`burst 10` specifies the bucket size as 10 units. `3/minute` specifies how
much it leaks, 3 units per minute, or 1 unit per every 20 seconds. Every new
connection adds one unit of water to it. If it fits, rule matches (usually:
connection is accepted). If the bucket overflows, rule doesn't match.

If burst is not specified, value 5 is assumed for it.

Some examples:

* `5/minute burst 1` allows one new connection (`burst 1`) and new connection
  every 12 second (`5/minute`).
* `3/minute burst 5` allows up to 5 new connections and new connection every
  20 second after those 5 connections are used.

Bandwidth rate can be used as simple traffic limiter. This can be specified
per service, or total for all. Example:

```
public-localhost {
  # Limit all incoming traffic to 30 MiB/s, total for all traffic
  global_rate "over 30 mbytes/second" drop -conntrack

  # Limit incoming SSH traffic to 2 MiB/s, per service traffic
  ssh global_rate "over 2 mbytes/second" drop -conntrack

  # Allow incoming SSH connections
  ssh
  ...
}
```

Rate `ct count 5` matches if there are up to 5 established connections,
including current one. So rule `ssh global_rate "ct count 2"` allows two
SSH connections (one old + current).

Rate `ct count over 6` matches if there are more than 6 established
connections. This is usually used with `drop` statement: `ssh global_rate
"ct count over 6" drop`.


### saddr_rate, daddr_rate

Source / destination IP address specific rate limit is similar to
`global_rate`.

`saddr_rate` allows limited amount of connections or bandwidth from single
source IP address, but there is no total (global) limit.

`daddr_rate` allows limited amount of connections or bandwidth for single
destination IP address, which is usually some host in `dmz` zone.

Both `saddr_rate` and `daddr_rate` can be specified for single rule. For
example `https saddr_rate "10/second" daddr_rate "1000/second"` specifies:

* Single IP can open 10 new connections per second.
* Total of 1000 connection per second from all IPs are allowed.


### saddr_rate_mask, daddr_rate_mask

Normally full IPv4 or IPv6 addresses are considered when counting `saddr_rate`
or `daddr_rate`. This can be changed with netmask: `ping saddr_rate "5/second
burst 20" saddr_rate_mask 24 56` uses <IPv4-address>/24 and
<IPv6-address>/56 instead of full IP address when counting limits.


### saddr_rate_name, daddr_rate_name

If you want to share same rate limit with two different rules you must
specify a name for it. For example:

```
  http  saddr_rate "30/second burst 50" saddr_rate_name http_limit
  https saddr_rate "30/second burst 50" saddr_rate_name http_limit
```

This counts both http and https traffic as single, allowing total of 30
connections per IP per second. Without name it would allow 30 + 30
connections per IP per second.


### saddr_daddr_rate, saddr_daddr_rate_mask, saddr_daddr_rate_name

This is special form of `saddr_rate + daddr_rate`, usable when you have
multiple destination IPs per service (DNS round-robin). In this rule
both source and destination address are counted as check key, instead of only
source or destination.


## Other


### template

Template is very similar to [macro](Configuration.md#macro). It's just another
way to define list of rules. Usually macro refers to single service
(like `domain` or `facetime`) while template refers to list of different
services. Example:

```
template my_own_name {  # Define template called "my_own_name"
  domain
  https
  ssh
}

localhost-public {
  template my_own_name  # Include template's content here
  ping
  reject log
}
```

See [host firewall](Host-Firewall.md#example-configuration-for-multi-zone)
for real life example.


### szone, dzone, new_szone, new_dzone

These can be specified in [zonemap](Configuration.md#zonemap) section to match
original source or destination zone, and to change it to a new zone. These
are used to branch out some specific traffic to its own zone, for example
to split `vpn` and `public` (non-VPN) traffic.


### helper

Linux kernel provides conntrack helper functionality to some services with
multiple ports, like `ftp` (tcp 21). You can enable this functionality by
appending `helper kernelname-port` after matcher. For example
`tcp 21 helper ftp-21`.

Linux has following helpers: `amanda, ftp, h323, irc, netbios_ns, pptp,
sane, sip, snmp, tftp`


### mss

Sets maximum segment size (MSS clamping) to all traffic. Some connections,
like IPsec or PPPoE, might require this. Example:

```
localhost-vpn {
  mss 1390
  ssh
  reject log
}
```

Special value `mss pmtu` can be used to calculate the value in runtime
based on what the routing cache has observed via Path MTU Discovery (PMTUD).
Example:

```
forward {  # internal-public
  mss pmtu
}

input {    # public-localhost
  mss pmtu
}

output {   # localhost-public
  mss pmtu
}
```


### conntrack, -conntrack

Rules are processed after conntrack check (flag `conntrack`, default value).
Flag `-conntrack` can be added to process rule before
conntrack. Conntrack will accept established and related traffic so normal
rule will see only new traffic.

This can be used to count all traffic instead of new connections only, or
to accept traffic without adding it to conntrack. For example high load
DNS server might accept DNS traffic without conntrack.

Example:

```
public-localhost {
  # Count all incoming traffic
  counter incoming_traffic continue -conntrack

  # Count incoming HTTP(S) traffic in web server
  tcp dport 80 443 counter web_traffic_in continue -conntrack
  ...
}

localhost-public {
  # Count outgoing HTTP(S) traffic in web server
  tcp sport 80 443 counter web_traffic_out continue -conntrack
  ...
}
```


### nft

Raw nftables rule can written with `nft "raw rule here"`. This works in
`zone-zone`, `zonemap`, `snat` and `dnat` sections. For example, `https`
macro can be written as:

```
  nft "tcp dport 443 accept"
  nft "udp dport 443 accept"
```

`nft` can also be used as part of rule:

```
  # Jump to my-custom-chain for UDP traffic to ports 1000-2000
  udp dport 1000-2000 nft "jump my-custom-chain"
```

See [nftables web page](https://wiki.nftables.org/) for more information
about nftables syntax.
