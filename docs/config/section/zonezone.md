# zone-zone

A FromZone-ToZone section defines [rules](../rule/index.md) for traffic
coming from FromZone and going to ToZone. Typically, you first accept
certain traffic and then
[reject or drop](../rule/statement.md#accept-drop-reject) everything else
as a final rule. Rules within a zone-zone section are (mostly, see
[below](zonezone.md#processing-order)) processed in the order listed.

Example:

```
public-localhost {
  # Allow some incoming traffic
  dhcp-client
  ping
  ssh

  # Drop everything else
  drop log
}

localhost-public {
  # Allow some outgoing traffic
  dhcp-server
  domain
  https
  ping
  ssh

  # Reject everything else
  reject log
}
```

If not specified, Foomuuri automatically appends a final `drop log` rule
(or `reject log` for `localhost-something` sections) to each zone-zone
section. It is always better to add this final rule explicitly in your
configuration. This final rule is also added to any unconfigured
zone-zone pairs.

If you have many zones, you will end up with many zone-zone pairs. See
[configuration files](../basic.md#configuration-files) for
recommendations on splitting them across multiple configuration files.


## localhost-localhost

The `localhost-localhost` zone-zone section (i.e., loopback traffic,
`127.0.0.1` and `::1`) is a special case: its final rule is `accept`.
Usually there is no need to add a `localhost-localhost` section explicitly.

A typical use case for `localhost-localhost` is to deny specific traffic
and then accept everything else:

```
localhost-localhost {
  # Don't allow user "untrusted" to connect to local services
  uid untrusted drop log

  # Don't allow local HTTP traffic
  http reject log

  # Accept everything else
  accept
}
```

Note that loopback traffic from your public IP to your public IP belongs
to `localhost-localhost`, not `public-public`.


## Processing Order

Rules within a zone-zone section are automatically sorted and processed in
the following block order:

1. [zonemap](zonemap.md) rules
2. [MSS clamping](../rule/misc.md#mss) options
3. Rules with [`-conntrack`](../rule/misc.md#conntrack-conntrack) flag
4. [ICMP](../rule/matcher.md#tcp-udp-icmp-icmpv6) rules
5. Previously accepted established and related traffic, accepted by conntrack
6. Incoming [multicast and broadcast](../rule/matcher.md#multicast-broadcast) rules
7. Everything else
