# Best Practices / FAQ

## Configuration files

Foomuuri reads configuration files from `/etc/foomuuri/*.conf` in alphabetical
order, including all sub directories. Configuration can be written to single
or multiple files. Following is just a recommendation, not a rule:

* Simple configuration (less than 200 lines) in single
  `/etc/foomuuri/foomuuri.conf` file.
* Large configuration should be split to `/etc/foomuuri/foomuuri.conf`,
  `/etc/foomuuri/localhost.conf` , `/etc/foomuuri/public.conf` etc. files.
  * `foomuuri.conf` contains everything but zone-zone sections.
  * `localhost.conf` contains all xxx-localhost sections (or localhost-xxx).
  * `public.conf` contains all xxx-public sections (or public-xxx).
* Subdirectories can be used, for example
  `/etc/foomuuri/zones.d/localhost.conf`.
* Very large configuration could be split to multiple `localhost-public.conf`
  etc. files, containing only single zone-zone section per file.


## Zone names

Following zones names are recommended, but you can use whatever you want to.

### localhost

`localhost` is the zone name for the computer running Foomuuri, similar to
"localhost" in hostnames. If you decide to use some other name then you must
configure it in [foomuuri { localhost_zone }](Configuration.md#foomuuri) section.

### public

`public` is the default external network zone, similar to "internet". Basic
host firewall has only `localhost` and `public` zones. If you decide to use
some other name then you should also configure it in
[foomuuri { dbus_zone }](Configuration.md#foomuuri) section.

`public` is for use in public areas. You do not trust the other computers on
networks to not harm your computer.

### home

Similar to `public`, but for use in home areas. You mostly trust the other
computers on networks to not harm your computer.

### work

Similar to `public`, but for use in work areas. You mostly trust the other
computers on networks to not harm your computer.

### internal

`internal` is your internal network ("intranet") zone for router firewall
configurations. Remote connections from `public` should not be allowed to
`internal`.

### dmz

Demilitarized zone is publicly-accessible part of your internal network.
Only selected incoming connections should be accepted from `public` to `dmz`,
for example `https`.

### vpn

IPsec and similar VPN traffic.


## GNOME

NetworkManager supports dynamically [mapping](Configuration.md#zone) connections
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
how to configure proxy ARP with Foomuuri using [hooks](Configuration.md#hook).


## Hairpin NAT / NAT Loopback

See [issues](https://github.com/FoobarOy/foomuuri/issues/8) how to configure
hairpin NAT with Foomuuri using [snat](Configuration.md#snat) and
[dnat](Configuration.md#dnat).

Usually it is better to do split DNS instead of hairpin NAT. Split DNS has
locally served zone with local IP addresses and publicly served zone with
public IP addresses.


## fail2ban

Foomuuri supports automatic IP address
[banning](Advanced-Filtering.md#automatic-ip-address-banning) without any
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
