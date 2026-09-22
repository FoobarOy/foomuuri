# Rate limit


## global_rate

Defines a global rate limit without a source or destination IP address
check. For example, `https global_rate "10/second burst 20"` allows HTTPS
traffic at the following rate:

* The first 20 new connections are allowed without limit.
* Once the burst is used up, up to 10 new connections per second are
  allowed.
* This rate is "global", meaning a single source IP can use all of the
  available slots, or 20 different sources can each use one slot.
* Here, "connection" means a new connection, not the total number of
  established, active connections (see `ct count` below).

There are three types of rates:

* New-connection rates (`x/time burst y`), which ignore whether some
  connections have already been closed:

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

* Conntrack rates (`ct count x`), counting the total number of
  established, active connections:

  * `"ct count 5"`
  * `"ct count over 6"`

A new-connection rate limit can be visualized as a leaking water bucket.
`burst 10` specifies the bucket size as 10 units. `3/minute` specifies how
fast it leaks - 3 units per minute, or 1 unit every 20 seconds. Every new
connection adds one unit of water to the bucket. If it fits, the rule
matches (usually meaning the connection is accepted); if the bucket
overflows, the rule doesn't match.

If burst is not specified, the Linux kernel assumes a value of 5. The
minimum value for burst is 1.

Some examples:

* `5/minute burst 1` allows one new connection (`burst 1`), plus one new
  connection every 12 seconds (`5/minute`).
* `3/minute burst 5` allows up to 5 new connections, then one new
  connection every 20 seconds once those 5 are used up.

A bandwidth rate can be used as a simple traffic limiter, either per
service or in total. Example:

```
public-localhost {
  # Limit all incoming traffic to 30 MiB/s, total across all traffic
  global_rate "over 30 mbytes/second" drop -conntrack

  # Limit incoming SSH traffic to 2 MiB/s, per service
  ssh global_rate "over 2 mbytes/second" drop -conntrack

  # Allow incoming SSH connections
  ssh
  ...
}
```

The rate `ct count 5` matches if there are up to 5 established
connections, including the current one. So the rule
`ssh global_rate "ct count 2"` allows two SSH connections (one existing,
plus the current one).

The rate `ct count over 6` matches if there are more than 6 established
connections. This is usually used with the `drop` statement:
`ssh global_rate "ct count over 6" drop`.


## saddr_rate, daddr_rate

Source/destination IP address-specific rate limiting works similarly to
`global_rate`.

`saddr_rate` limits the number of connections or amount of bandwidth from
a single source IP address, but applies no total (global) limit.

`daddr_rate` limits the number of connections or amount of bandwidth to a
single destination IP address - usually a host in the `dmz` zone.

Both `saddr_rate` and `daddr_rate` can be specified on a single rule. For
example, `https saddr_rate "10/second" daddr_rate "1000/second"`
specifies:

* A single IP can open 10 new connections per second.
* A total of 1000 connections per second are allowed across all IPs.


## saddr_rate_mask, daddr_rate_mask

Normally, full IPv4 or IPv6 addresses are used when counting `saddr_rate`
or `daddr_rate`. This can be changed with a netmask:
`ping saddr_rate "5/second burst 20" saddr_rate_mask 24 56` uses
`<IPv4-address>/24` and `<IPv6-address>/56` instead of the full IP address
when counting limits.


## saddr_rate_name, daddr_rate_name

To share the same rate limit across two different rules, specify a name
for it. For example:

```
  http  saddr_rate "30/second burst 50" saddr_rate_name http_limit
  https saddr_rate "30/second burst 50" saddr_rate_name http_limit
```

This counts HTTP and HTTPS traffic together as a single rate, allowing a
total of 30 connections per IP per second. Without the shared name, it
would allow 30 + 30 connections per IP per second.


## saddr_daddr_rate, saddr_daddr_rate_mask, saddr_daddr_rate_name

This is a special form of `saddr_rate` combined with `daddr_rate`, useful
when a service has multiple destination IPs (as with DNS round-robin). In
this rule, both the source and destination address are used as the count
key, instead of just the source or destination alone.
