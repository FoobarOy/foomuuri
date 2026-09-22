# zone

This section is required in every configuration. It lists all known
zones.

```
zone {
  localhost
  public
}
```

The example above defines two zones, `localhost` and `public`. Every
configuration must include the `localhost` zone, which represents the
computer running Foomuuri, similar to "localhost" in hostnames. See
[zone names](../basic.md#zone-names) for recommended zone naming.

The example above assumes you are using firewalld D-Bus
(`dbus_firewalld` config option) emulation, where interfaces are attached
to and detached from zones by NetworkManager. This is the recommended
approach for laptops and personal servers, and this config option is
turned on by default when the `foomuuri-firewalld` package is installed.

You can also define a default interface-to-zone mapping by listing
interface name(s) after the zone name. This is useful for corporate
servers with a static network configuration, and can be used with or
without firewalld D-Bus emulation. This mapping is only a default, not
static - interfaces can still be moved to other zones via D-Bus calls.

```
zone {
  localhost            # localhost must be left empty
  public    eth0       # eth0 is attached to public
  dmz       eth1 eth2  # eth1 and eth2 are in dmz
}
```

It is also possible to use wildcard interface names. If you define `wg*`,
make sure NetworkManager doesn't also try to assign `wg0` to a zone
directly - doing so would create an "interval overlap" error, since `wg*`
and `wg0` would conflict.

```
zone {
  localhost
  public     eth0
  wireguard  wg*  # Matches wg0, wg1, wgfoo, and so on
}
```

There is also a catch-all interface, `*`, which matches all unassigned
interfaces. Interfaces already assigned to a zone, whether in the
configuration or by NetworkManager, keep that zone.

```
zone {
  localhost
  public     *     # Everything other than eth0 is assigned to public
  internal   eth0
}
```
