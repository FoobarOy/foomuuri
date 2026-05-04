# Rate limit


## global_rate

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

  * `"7/second burst 30"`
  * `"3/second"` (no burst specified, so `burst 5` is assumed)
  * `"1/minute burst 1"`
  * `"50/minute burst 200"`
  * `"30/minute"`
  * `"100/hour burst 200"`
  * `"100/hour"`
  * `"over 8/second burst 10"`

* Bandwidth rates (`x bytes/time burst y bytes`):

  * `"10 mbytes/second burst 12000 kbytes"`
  * `"10 mbytes/second"`
  * `"over 10 mbytes/second burst 12000 kbytes"`
  * `"over 10 mbytes/second"`

* Conntrack rates (`ct count x`) counting total number of established, active
  connections:

  * `"ct count 5"`
  * `"ct count over 6"`

New connection rate limit can be visualized as leaking water bucket.
`burst 10` specifies the bucket size as 10 units. `3/minute` specifies how
much it leaks, 3 units per minute, or 1 unit per every 20 seconds. Every new
connection adds one unit of water to it. If it fits, rule matches (usually:
connection is accepted). If the bucket overflows, rule doesn't match.

If burst is not specified, Linux kernel assumes value 5 for it. Minimum value
for burst is 1.

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


## saddr_rate, daddr_rate

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


## saddr_rate_mask, daddr_rate_mask

Normally full IPv4 or IPv6 addresses are considered when counting `saddr_rate`
or `daddr_rate`. This can be changed with netmask: `ping saddr_rate "5/second
burst 20" saddr_rate_mask 24 56` uses <IPv4-address>/24 and
<IPv6-address>/56 instead of full IP address when counting limits.


## saddr_rate_name, daddr_rate_name

If you want to share same rate limit with two different rules you must
specify a name for it. For example:

```
  http  saddr_rate "30/second burst 50" saddr_rate_name http_limit
  https saddr_rate "30/second burst 50" saddr_rate_name http_limit
```

This counts both http and https traffic as single, allowing total of 30
connections per IP per second. Without name it would allow 30 + 30
connections per IP per second.


## saddr_daddr_rate, saddr_daddr_rate_mask, saddr_daddr_rate_name

This is special form of `saddr_rate + daddr_rate`, usable when you have
multiple destination IPs per service (DNS round-robin). In this rule
both source and destination address are counted as check key, instead of only
source or destination.

