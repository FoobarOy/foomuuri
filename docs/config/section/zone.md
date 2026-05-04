# zone

This section is required on all configurations. It lists all known zones.

```
zone {
  localhost
  public
}
```

Above example defines two zones, `localhost` and `public`. All configurations
must have zone `localhost`, which is the computer running Foomuuri,
similar to "localhost" in hostnames. See
[zone names](../basic.md#zone-names) for recommended zone naming.

Above example assumes that you are using firewalld D-Bus (`dbus_firewalld`
config option) emulation where interfaces are attached and detached to zones
by NetworkManager. It is the recommended way for laptops and personal servers.
This config option will be turned on by default when installing
`foomuuri-firewalld` package.

You can also define default interface to zone mapping by specifying interface
name(s) after zone name. This is useful for corporate servers with static
network configuration. This method can be used with or without firewalld
D-Bus emulation. This mapping is only default, not static. Interfaces can
still be moved to other zones with D-Bus calls.

```
zone {
  localhost            # Localhost must be left empty
  public    eth0       # eth0 is attached to public
  dmz       eth1 eth2  # eth1 and eth2 are in dmz
}
```

It is also possible to use wildcard interface names. If you define `wg*`
then make sure that NetworkManager doesn't try to assign `wg0` to any zone.
It would create "interval overlap" error as `wg*` and `wg0` conflicts.

```
zone {
  localhost
  public     eth0
  wireguard  wg*  # Matches wg0, wg1, wgfoo, and so on
}
```
