# FAQ

## GNOME

NetworkManager supports dynamically [mapping](config/section/zone.md)
connections to firewall zones, but the GNOME Control Center graphical
connection editor does not. There are two alternative ways to edit a
connection's zone:

* Use the graphical `nm-connection-editor` (recommended)
* Use the command line
  `nmcli connection modify <connection-name> connection.zone <zone-name>`

This is only needed when changing a connection's firewall zone. All other
edits can still be made through GNOME Control Center.


## DHCP

To obtain an IP address via DHCP, you must allow both the outgoing
`dhcp-server` request and the incoming `dhcp-client` reply. For example:

```
localhost-public {
  # Allow localhost's DHCP client to send a request to a DHCP server running
  # on public zone (discover/request a lease).
  dhcp-server
  dhcpv6-server
}

public-localhost {
  # Allow the reply packet from public's DHCP server to localhost's client
  # (offer an IP address).
  dhcp-client
  dhcpv6-client
}
```

Similar rules are required if you run a DHCP server on `localhost` that
serves leases to clients in your `internal` zone:

```
internal-localhost {
  # Allow incoming DHCP discover/request from the internal zone's client to
  # the DHCP server running on localhost.
  dhcp-server
  dhcpv6-server
}

localhost-internal {
  # Allow localhost's DHCP server to send an offer reply to the internal
  # zone's client.
  dhcp-client
  dhcpv6-client
}
```


## Proxy ARP

See this [discussion](https://github.com/FoobarOy/foomuuri/discussions/2)
for instructions on configuring proxy ARP with Foomuuri using
[hooks](config/section/hook.md).


## Hairpin NAT / NAT Loopback

See this [issue](https://github.com/FoobarOy/foomuuri/issues/8) for
instructions on configuring hairpin NAT with Foomuuri using
[SNAT](config/section/snat.md) and [DNAT](config/section/dnat.md).

In most cases, split DNS is preferable to hairpin NAT. With split DNS, a
locally served zone resolves to local IP addresses while a publicly served
zone resolves to public IP addresses.


## fail2ban

Foomuuri supports automatic IP address
[banning](example/advanced.md#automatic-ip-address-banning) without any
external programs, so `fail2ban` is usually unnecessary. Banning happens
entirely on the packet path, natively at the nftables level.

Alternatively, see this [issue](https://github.com/FoobarOy/foomuuri/issues/9)
for instructions on integrating Foomuuri with `fail2ban`.


## Custom nftables chains

See this [discussion](https://github.com/FoobarOy/foomuuri/discussions/31)
for instructions on defining custom nftables chains and jumping to them.


## QEMU/libvirt and vnet interfaces in a bridge

See this [discussion](https://github.com/FoobarOy/foomuuri/discussions/15)
for instructions on silently dropping `OUTPUT REJECT IN= OUT=vnetXX` log
entries, which appear after a bridge interface is added or removed.


## Preventing private networks from routing to the public internet

See this [issue](https://github.com/FoobarOy/foomuuri/issues/24) for
instructions on blocking routing of 10.0.0.0/8 and similar private
networks to the public internet.
