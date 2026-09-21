# iplist

Instead of using static IP addresses, Foomuuri can perform periodic DNS
hostname lookups and download external IP address lists. These addresses
are stored in iplists and cached across reboots and single lookup failures.

The first word on each line is the iplist name, which must begin with an
`@` character. The words that follow can be any combination of:

* An IPv4 or IPv6 address, with or without a netmask
* A DNS hostname
* A filename containing IP addresses, with or without a netmask
* A URL for a file containing IP addresses, with or without a netmask

Example:

```
iplist {
  # Resolve known good hostnames
  @goodhost foobar.fi mydomain.com

  # Download Finnish IPv4 and IPv6 addresses from https://github.com/ipverse/geo-ip-blocks
  @fi   https://raw.githubusercontent.com/ipverse/geo-ip-blocks/master/country/fi/fi-ipv4.txt
  @fi   + https://raw.githubusercontent.com/ipverse/geo-ip-blocks/master/country/fi/fi-ipv6.txt

  # Download Finnish Elisa operator IP addresses from https://github.com/ipverse/as-ip-blocks
  @elisa  https://raw.githubusercontent.com/ipverse/as-ip-blocks/master/as/719/ipv4-aggregated.txt
  @elisa  + https://raw.githubusercontent.com/ipverse/as-ip-blocks/master/as/719/ipv6-aggregated.txt

  # Read a blacklist from text files
  @blacklist  /etc/foomuuri/blacklist*.txt

  # Read content from a file and add some extra IPs to it
  @whitelist  /etc/foomuuri/whitelist*.txt 10.0.0.0/8 192.0.2.32

  # Manipulate this list with the "foomuuri iplist add mylist 10.0.0.1" command.
  # See the command line help for the "foomuuri add/del/flush" commands.
  @mylist
}

public-localhost {
  # Allow SSH from known good hosts
  ssh saddr @goodhost

  # Don't allow blacklisted addresses to reach IMAP
  imap saddr @blacklist drop log "public-localhost DROP-blacklist"

  # Allow mylist entries to reach IMAP without rate limiting
  imap saddr @mylist

  # Allow Finnish users to reach IMAP at a fast rate of 1 per second
  imap saddr @fi saddr_rate "1/second burst 10"

  # Allow everybody to reach IMAP at a slow rate of 1 per minute.
  # This includes Finnish users who exceed the rate limit above.
  imap saddr_rate "1/minute burst 1"

  # ...rest of the rules...
}
```

Another example, showing how to create a macro that allows access to Valve
Steam:

```
iplist {
  # Create an iplist from Valve's IP addresses
  @valve_as	 https://raw.githubusercontent.com/ipverse/as-ip-blocks/master/as/32590/ipv4-aggregated.txt
  @valve_as	 + https://raw.githubusercontent.com/ipverse/as-ip-blocks/master/as/32590/ipv6-aggregated.txt
}

macro {
  # Create a macro to allow outgoing traffic to the Valve iplist
  valve-steam	udp 3478 4379-4380 27000-27100 daddr @valve_as;
  valve-steam	+ tcp 27015-27050 daddr @valve_as
}

localhost-public {
  # Allow outgoing traffic to Valve Steam
  valve-steam
}
```


## Iplist Filters

Downloaded content can be filtered by appending `|filter` after a filename,
URL, or hostname. Multiple filters can be chained.

* `|shell:/path/to/command` - pipe the content through an external command
* `|json:filter` - parse the content as JSON, using the external `jq` command
* `|html:XPath` - parse the content as HTML, using an XPath filter
* `|xml:XPath` - parse the content as XML, using an XPath filter

Example:

```
iplist {
  # Download the GitHub IP address list and parse it as JSON, returning
  # the "actions" list.
  @github      https://api.github.com/meta|json:.actions[]

  # Download a network scanner's IP address list and parse it from an
  # HTML page.
  @netscanner  https://internet-measurement.com/|html://div/pre/text()
}
```


## Iplist Settings

Hostnames are refreshed every 15 minutes and time out after 24 hours. URLs
are refreshed once a day and time out after 10 days. These values can be
changed globally or per iplist.

```
iplist {
  # Define global timeouts
  dns_refresh=15m
  dns_timeout=24h
  url_refresh=1d
  url_timeout=10d

  # Define a per-iplist timeout
  @fasturl  https://some/url  url_refresh=1h30m url_timeout=2d
}
```

The timeouts above are rounded to 15-minute increments. This interval can
be changed with `systemctl edit foomuuri-iplist.timer`.

A timeout value can be specified as:

* `4w` - weeks
* `2d` - days
* `3h` - hours
* `15m` - minutes
* `900s` - seconds
* `2d3h15m` or `1w90m` - a combination of the above

With the optional `missing_ok=yes` option (default: `no`), a warning is
printed instead of an error when:

* DNS resolution or the URL/file download fails, or
* the resolution/download succeeds but the content is empty.

The optional `overwrite=yes|no` option controls how resolved IP addresses
or URL content are applied to the iplist. With `yes`, old content is
removed and replaced with the new addresses. With `no`, old content is
kept until it expires, and new addresses are either added or have their
expiry timeout updated.

The default `overwrite` value depends on the content type:

* URL/file content defaults to `overwrite=yes`
* DNS resolution defaults to `overwrite=no`

The maximum size of a downloaded IP address list can be set with
`url_max_size=bytes`. The default is 33554432 (32 MiB); content exceeding
this size is ignored.

The optional `dynamic=yes` option (default: `no`) enables the dynamic flag
on the generated ruleset. This is required when updating iplist content on
the packet path using the [`iplist_update`](../rule/matcher.md#iplist_update)
matcher, for example, in automatic IP address
[banning](../../example/advanced.md#automatic-ip-address-banning). This
option should not be used for normal usage.

The optional `element_timeout=time` option sets the default element expiry
timeout. This is needed for automatic IP address banning and port knocking.

The optional `merge=no` option (default: `yes`) disables IP address
auto-merging. It is generally recommended to leave auto-merging enabled,
except when using an external `fail2ban` integration, where it should be
disabled.

Foomuuri will not add IP addresses at startup to lists marked with the
optional `start=no` option (default: `yes`); entries are added later by the
`foomuuri-iplist.timer` service instead. This is useful for "unsafe"
external iplists, to ensure that Foomuuri startup does not fail or block
access during the first few minutes after a reboot.


## Iplist Command Line

Iplists can be manipulated from the command line, for example, by an
external `fail2ban` program. The command `foomuuri iplist add IPLIST
ipaddress` adds an IP address to `IPLIST`. Other available commands are
`foomuuri iplist list`, `foomuuri iplist del`, and `foomuuri iplist flush`.
See the command line help for full usage details.

Example:

```
iplist {
  @banned    dynamic=yes element_timeout=5m  # automatic IP address banning
  @blacklist merge=no                        # fail2ban
}

# Manipulate with the command:
#
# foomuuri iplist add @blacklist 10.0.0.1
# foomuuri iplist del @blacklist 10.0.0.1
```
