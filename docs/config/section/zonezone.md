# zone-zone

FromZone-ToZone section defines [rules](../rule/index.md) for traffic coming from
FromZone and going to ToZone. Normally you first accept some traffic
and then [reject or drop](../rule/statement.md#accept-drop-reject) everything else as final
rule. Rules inside zone-zone section are (mostly, see below) processed in
listed order. Example:

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

Foomuuri will automatically add final `drop log` (or `reject log` for
`localhost-something`) rule to zone-zone section if not specified. It is
always better to add explicit final rule to configuration.

Zone-zone section `localhost-localhost` (aka loopback traffic, aka
`127.0.0.1` and `::1`) is special case. It's final rule is `accept`. Usually
there is no need to add `localhost-localhost`section.

Normal use case for `localhost-localhost` is to deny some traffic and then
accept everything else.

```
localhost-localhost {
  # Don't allow user "untrusted" to connect local services
  uid untrusted drop log

  # Don't allow local http traffic
  http reject log

  # Accept everything else
  accept
}
```

Please note that loopback traffic from your public IP to your public IP
belongs to `localhost-localhost`, not `public-public`.

If you have a lot of zones there will be a lot of zone-zone pairs. See
[configuration files](../basic.md#configuration-files) for recommendations
how to split them to multiple files.

"Mostly": Rules inside zone-zone section are automatically sorted and
processed in following block order:

1. ICMP rules in listed order
2. Previously accepted established and related traffic is accepted by conntrack
3. Incoming multicast and broadcast rules in listed order
4. Everything else in listed order

