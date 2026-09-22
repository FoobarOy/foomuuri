# zonemap

By default, Foomuuri maps incoming and outgoing traffic to zones based on
the source and destination network interface. These interfaces are
assigned to zones dynamically by NetworkManager, or configured in the
[zone](zone.md) section.

The zonemap section can be used to map traffic to a different zone using
standard [rules](../rule/index.md). Example:

```
zonemap {
  # Map outgoing IPsec traffic destined for zone "public" to use zone
  # "vpn" instead.
  dipsec dzone public new_dzone vpn

  # Same for incoming traffic.
  sipsec szone public new_szone vpn
}

localhost-public {
  # Rules for non-IPsec traffic
  ipsec   # You must allow IPsec traffic here and in public-localhost
  ...accept some traffic...
  reject log
}

localhost-vpn {
  # Rules for IPsec traffic
  ...accept some traffic...
  reject log
}
```

The example above, splitting traffic into IPsec and non-IPsec zones, is
the most common use case. You can use any matcher - for example, `daddr`
or `saddr` to map specific IP addresses to their own zones, or `uid` or
`gid` to map outgoing traffic from a specific local user to its own zone:

```
zonemap {
  # Map IP address 10.2.3.0/24 from internal to dmz
  saddr 10.2.3.0/24 szone internal new_szone dmz
  daddr 10.2.3.0/24 dzone internal new_dzone dmz

  # Map outgoing traffic from user myservice to myzone
  uid myservice szone localhost new_szone myzone

  # Map all outgoing IPsec traffic to xxx-vpn, regardless of the original
  # dzone
  dipsec new_dzone vpn
}
```
