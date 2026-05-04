# Basics

## Configuration files

Foomuuri reads configuration files from `/etc/foomuuri/*.conf` in alphabetical
order, including all sub directories. Foomuuri also reads static configuration
from `/usr/share/foomuuri/*.conf` which can be overwritten in `/etc/foomuuri`.

Configuration can be written to single or multiple files. Following is just a
recommendation, not a rule:

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

Raw `nftables` rules can be written to `/etc/foomuuri/*.nft` and they will be
included to generated ruleset.

## Zone names

Following zones names are recommended, but you can use whatever you want to.

### localhost

`localhost` is the zone name for the computer running Foomuuri, similar to
"localhost" in hostnames. If you decide to use some other name then you must
configure it in [foomuuri { localhost_zone }](section/foomuuri.md) section.

### public

`public` is the default external network zone, similar to "internet". Basic
host firewall has only `localhost` and `public` zones. If you decide to use
some other name then you should also configure it in
[foomuuri { dbus_zone }](section/foomuuri.md) section.

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


## Miscellaneous

Comments can be written as `# comment`.

Long line can be split to multiple lines by adding `\` to end of line.

Multiple words can be combined to single word by writing them in quotes.
For example `ssh accept log "accept ssh for testing"` will accept SSH
traffic with log message `accept ssh for testing`.

Output from external command can be used to generate rules. It can return
single line, multiple lines or part of line. Syntax is
`$(shell command to run with parameters)`. Command is run with shell so pipes
and `;` will work. Be careful to run only trusted commands. `$(shell)` is
processed before [macro](section/macro.md) expansion.

Example:

```
# This is a comment

macro {
  # Define local_port_range macro by reading correct value from /proc file
  local_port_range $(shell sed s/\\t/-/ < /proc/sys/net/ipv4/ip_local_port_range)
}

localhost-public {
  ssh  # This is a comment
  smtp \
    daddr 192.0.2.32  # Allow SMTP to single IP
}

public-localhost {
  tcp local_port_range  # Allow TCP to ports 32768-60999 (default range)
}
```

Command to run can not contain `)` character. For such complex commands it's
better to create shell script and call that:

```
macro {
  mymacro  $(shell /etc/foomuuri/mymacro.sh parameters)
}
```
