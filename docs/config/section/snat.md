# snat

Source NAT is used to mangle traffic by using standard [rules](../rule/index.md).

Example:

```
snat {
  # Masquerade all traffic from 10.0.0.0/8 going to eth0 interface.
  # New outgoing IP is eth0's IP address.
  saddr 10.0.0.0/8 oifname eth0 masquerade

  # Use outgoing IP 192.0.2.32 to all non-IPsec traffic coming from
  # 10.0.0.0/8 and going to eth1 interface.
  saddr 10.0.0.0/8 oifname eth1 -dipsec snat 192.0.2.32

  # IPv6-to-IPv6 Network Prefix Translation (NPTv6)
  saddr fd00:f00:4444::/64 oifname eth2 snat_prefix to 2a03:1111:222:8888::/64
}
```

Remember to accept SNAT'ed traffic in zone-zone section.
See [dnat](dnat.md) for more examples.

