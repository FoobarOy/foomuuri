# FAQ

## GNOME

NetworkManager supports dynamically [mapping](config/section/zone.md) connections
with firewall zones but graphical connection editor GNOME Control Center
doesn't. There are two alternative ways to edit connections with zone support:

* Use graphical `nm-connection-editor` (recommended)
* Use command line `nmcli connection modify <connection-name> connection.zone <zone-name>`

This needs to be done only when changing firewall zone for connection. All
other edits can be done with GNOME Control Center.


## DHCP

To obtain an IP address with DHCP you must allow both outgoing `dhcp-server`
request and incoming `dhcp-client` reply. Example:

```
localhost-public {
  # Allow localhost's DHCP client to send a request to a DHCP server running
  # on public zone (discover/request a lease).
  dhcp-server
  dhcpv6-server
}

public-localhost {
  # Allow reply packet from public's DHCP server to localhost's client
  # (offer an IP address).
  dhcp-client
  dhcpv6-client
}
```

Similar rules are required if you run DHCP server on `localhost` serving IP
leases to your `internal` zone clients:

```
internal-localhost {
  # Allow incoming DHCP discover/request from internal's client to
  # DHCP server running on localhost.
  dhcp-server
  dhcpv6-server
}

localhost-internal {
  # Allow localhost's DHCP server to send an offer reply to internal's client.
  dhcp-client
  dhcpv6-client
}
```


## Proxy ARP

See [discussions](https://github.com/FoobarOy/foomuuri/discussions/2)
how to configure proxy ARP with Foomuuri using [hooks](config/section/hook.md).


## Hairpin NAT / NAT Loopback

See [issues](https://github.com/FoobarOy/foomuuri/issues/8) how to configure
hairpin NAT with Foomuuri using [snat](config/section/snat.md) and
[dnat](config/section/dnat.md).

Usually it is better to do split DNS instead of hairpin NAT. Split DNS has
locally served zone with local IP addresses and publicly served zone with
public IP addresses.


## fail2ban

Foomuuri supports automatic IP address
[banning](example/advanced.md#automatic-ip-address-banning) without any
external programs. This is usually enough, no `fail2ban` is needed. Banning
happens fully on packet path, native on nftables level.

Alternatively, see [issues](https://github.com/FoobarOy/foomuuri/issues/9)
how to integrate Foomuuri with `fail2ban` program.


## Custom nftables chains

See [discussions](https://github.com/FoobarOy/foomuuri/discussions/31)
how to define custom nftables chains and how to jump to them.


## QEMU/libvirt and vnet interfaces in a bridge

See [discussions](https://github.com/FoobarOy/foomuuri/discussions/15) how
to silently drop `OUTPUT REJECT IN= OUT=vnetXX` log entries. These lines
are logged after bridge interface is added or removed.


## Don't route private networks to public internet

See [issues](https://github.com/FoobarOy/foomuuri/issues/24) how to block
routing 10.0.0.0/8 and similar private networks to public internet.
