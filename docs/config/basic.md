# Basics


## Configuration Files

Foomuuri reads configuration files from `/etc/foomuuri/*.conf`, in
alphabetical order, including all subdirectories. Foomuuri also reads
static configuration from `/usr/share/foomuuri/*.conf`, which can be
overridden in `/etc/foomuuri`.

Configuration can be written to a single file or split across multiple
files. The following is a recommendation, not a rule:

* Simple configurations (fewer than 200 lines) can go in a single
  `/etc/foomuuri/foomuuri.conf` file.
* Larger configurations should be split across
  `/etc/foomuuri/foomuuri.conf`, `/etc/foomuuri/localhost.conf`,
  `/etc/foomuuri/public.conf`, etc.:
  * `foomuuri.conf` contains everything except the zone-zone sections.
  * `localhost.conf` contains all `xxx-localhost` (or `localhost-xxx`)
    sections.
  * `public.conf` contains all `xxx-public` (or `public-xxx`) sections.
* Subdirectories can be used, for example
  `/etc/foomuuri/zones.d/localhost.conf`.
* Very large configurations could be split further, into files such as
  `localhost-public.conf`, each containing a single zone-zone section.

Raw `nftables` rules can be written to `/etc/foomuuri/*.nft` and will be
included in the generated ruleset.


## Zone Names

The following zone names are recommended, but you may use whatever names
you prefer.


### localhost

`localhost` is the zone name for the computer running Foomuuri, similar to
"localhost" in hostnames. If you use a different name, you must configure
it in the [foomuuri { localhost_zone }](section/foomuuri.md) section.


### public

`public` is the default external network zone, similar to "the internet".
A basic host firewall has only `localhost` and `public` zones. If you use
a different name, you should also configure it in the
[foomuuri { dbus_zone }](section/foomuuri.md) section.

`public` is intended for use in public location, where you do not trust the
other computers on the network not to harm your computer.


### home

Similar to `public`, but for use in home location, where you mostly trust
the other computers on the network not to harm your computer.


### work

Similar to `public`, but for use in work location, where you mostly trust
the other computers on the network not to harm your computer.


### internal

`internal` is your internal network ("intranet") zone, for router firewall
configurations. Remote connections from `public` should not be allowed to
reach `internal`.


### dmz

The demilitarized zone is the publicly accessible part of your internal
network. Only selected incoming connections should be accepted from
`public` to `dmz`, for example `https`.


### vpn

IPsec and similar VPN traffic.


## Miscellaneous

Comments in the configuration files are written as `# comment`.

A long line can be split across multiple lines by adding `\` at the end
of each line.

Multiple words can be combined into a single token by enclosing them in
quotes. For example, `ssh accept log "accept ssh for testing"` accepts
SSH traffic and logs it with the message `accept ssh for testing`.

The output of an external command can be used to generate rules. It may
return a single line, multiple lines, or part of a line. The syntax is
`$(shell command to run with parameters)`. The command runs in a shell, so
pipes and `;` work as expected. Be careful to run only trusted commands.
`$(shell)` is processed before [macro](section/macro.md) expansion.

Example:

```
# This is a comment

macro {
  # Define the local_port_range macro by reading the correct value from /proc.
  local_port_range $(shell sed s/\\t/-/ < /proc/sys/net/ipv4/ip_local_port_range)
}

localhost-public {
  ssh  # This is a comment
  smtp \
    daddr 192.0.2.32  # Allow SMTP to a single IP
}

public-localhost {
  tcp local_port_range  # Allow TCP to ports 32768-60999 (default range)
}
```

The command being run cannot contain a `)` character. For such complex
commands, it's better to create a shell script and call that instead:

```
macro {
  mymacro  $(shell /etc/foomuuri/mymacro.sh parameters)
}
```
