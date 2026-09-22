# dnat

Destination NAT is used to rewrite traffic using standard
[rules](../rule/index.md).

Example:

```
dnat {
  # HTTP traffic to 10.0.0.1 is DNAT'ed to 10.0.0.2 port 8080
  daddr 10.0.0.1 http dnat 10.0.0.2:8080

  # HTTP traffic to fd00:f00::1 is DNAT'ed to fd00:f00::2 port 8080
  daddr fd00:f00::1 http dnat [fd00:f00::2]:8080

  # HTTP traffic to 10.0.0.6 is DNAT'ed to 10.0.0.7, port doesn't change
  daddr 10.0.0.6 http dnat 10.0.0.7

  # All SMTP traffic from eth2 is DNAT'ed to 10.0.0.8 or fd00:f00::8,
  # port doesn't change
  iifname eth2 smtp dnat 10.0.0.8 fd00:f00::8

  # All traffic from eth1 interface is DNAT'ed to 10.0.0.3
  iifname eth1 dnat 10.0.0.3

  # HTTP traffic to 10.0.0.4 coming from interface eth2 is DNAT'ed to 10.0.0.5
  iifname eth2 daddr 10.0.0.4 http dnat 10.0.0.5

  # HTTP traffic to localhost coming from interface eth3 is DNAT'ed to 10.0.0.6
  iifname eth3 oifname lo http dnat 10.0.0.6
}
```

Remember to accept DNAT'ed traffic in the relevant zone-zone section. This
can be done with a specific rule or with the `ct_status` matcher. Example:

```
public-internal {
  # Specific rule to accept HTTPS
  https daddr 10.0.0.9

  # Generic rule to accept all DNAT'ed traffic
  ct_status dnat
}
```
