# zonemap

Normally Foomuuri will map incoming and outgoing traffic to zones by
source and destination network interface. These interfaces are assigned to
zones dynamically by NetworkManager, or configured in
[zone](zone.md) section.

Zonemap section can be used to map traffic to different zone by using
standard [rules](../rule/index.md). Example:

```
zonemap {
  # Map outgoing IPsec traffic that is going to zone "public" to use zone
  # "vpn" instead.
  dipsec dzone public new_dzone vpn

  # Same for incoming.
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

Above example, splitting traffic to IPsec and non-IPsec zones is the most
common use case. You can use any matcher, for example `daddr` or `saddr` to
map some IP addresses to own zones, or `uid` or `gid` to map outgoing
traffic from some local user to own zone:

```
zonemap {
  # Map IP address 10.2.3.0/24 from internal to dmz
  saddr 10.2.3.0/24 szone internal new_szone dmz
  daddr 10.2.3.0/24 dzone internal new_dzone dmz

  # Map outgoing traffic from user myservice to myzone
  uid myservice szone localhost new_szone myzone

  # Map all outgoing IPsec traffic to xxx-vpn, no matter what the original
  # dzone was
  dipsec new_dzone vpn
}
```

