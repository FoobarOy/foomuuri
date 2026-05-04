# iplist

Instead of using static IP addresses Foomuuri can perform periodical DNS
hostname lookups and download external IP-lists. These addresses are
stored to sets and cached across reboots and single lookup failures.

First word in line is set name, which must begin with `@` character.
Next words can be:

* IPv4 or IPv6 address, with or without mask
* DNS hostname
* Filename containing IP addresses, with or without mask
* URL for file containing IP addresses, with or without mask

Example:

```
iplist {
  # Resolve known good hostnames
  @goodhost foobar.fi mydomain.com

  # Download Finnish IPv4 and IPv6 addresses from https://github.com/ipverse/rir-ip
  @fi   https://raw.githubusercontent.com/ipverse/rir-ip/master/country/fi/ipv4-aggregated.txt
  @fi   + https://raw.githubusercontent.com/ipverse/rir-ip/master/country/fi/ipv6-aggregated.txt

  # Download Finnish Elisa operator IP addresses from https://github.com/ipverse/asn-ip
  @elisa  https://raw.githubusercontent.com/ipverse/asn-ip/master/as/719/ipv4-aggregated.txt
  @elisa  + https://raw.githubusercontent.com/ipverse/asn-ip/master/as/719/ipv6-aggregated.txt

  # Read blacklist from text files
  @blacklist  /etc/foomuuri/blacklist*.txt

  # Read content from file and add some extra IPs to it
  @whitelist  /etc/foomuuri/whitelist*.txt 10.0.0.0/8 192.0.2.32

  # Manipulate this list with "foomuuri iplist add mylist 10.0.0.1" command.
  # See command line help for "foomuuri add/del/flush" commands.
  @mylist
}

public-localhost {
  # Allow SSH from known good hosts
  ssh saddr @goodhost

  # Don't allow blacklisted addresses to IMAP
  imap saddr @blacklist drop log "public-localhost DROP-blacklist"

  # Allow mylist entries to IMAP without rate
  imap saddr @mylist

  # Allow Finnish users to IMAP with fast 1 per second rate
  imap saddr @fi saddr_rate "1/second burst 10"

  # Allow everybody to IMAP with slow 1 per minute rate. This includes
  # over rate limit Finnish users.
  imap saddr_rate "1/minute burst 1"

  # ...rest of the rules...
}
```

Hostnames are refreshed every 15 minutes and they will timeout after 24 hours.
URLs are refreshed once a day and timeout is 10 days. These values can be
changed globally or per set.

```
iplist {
  # Define global timeouts
  dns_refresh=15m
  dns_timeout=24h
  url_refresh=1d
  url_timeout=10d

  # Define per set timeout
  @fasturl  https://some/url  url_refresh=1h30m url_timeout=2d
}
```

Above timeouts are rounded to 15 minutes. This can be configured with
`systemctl edit foomuuri-iplist.timer` command.

Timeout can be:

* `4w` weeks
* `2d` days
* `3h` hours
* `15m` minutes
* `900s` seconds
* `2d3h15m` or `1w90m` combination of above

Downloaded content can be filtered by adding `|filter` after filename,
URL or hostname. Multiple filters can be chained.

* `|shell:/path/to/command` pipe it via external command
* `|json:filter` use external `jq` command to parse it as JSON data
* `|html:XPath` parse it as HTML data, using XPath filter
* `|xml:XPath` parse it as XML data, using XPath filter
* `|missing-ok` don't print warning if download or DNS resolve fails

Example:

```
iplist {
  # Download Github IP address list and parse it as JSON, returning
  # "actions" list.
  @github      https://api.github.com/meta|json:.actions[]

  # Download network scanner IP address list and parse it from HTML page.
  @netscanner  https://internet-measurement.com/|html://div/pre/text()
}
```

Maximum content size for downloaded IP address list can be defined with
`url_max_size=bytes` line. Default value is 33554432 (32 MiB). List will
be ignored if it's too large.

Optional `dynamic=yes` option enables dynamic flag on generated ruleset.
This flag is needed when updating iplist content on packet path with
[`iplist_update`](../rule/matcher.md#iplist_update) matcher, for example in automatic
IP address [banning](../../example/advanced.md#automatic-ip-address-banning).
For normal usage this option should not be used.

Optional `element_timeout=time` option sets default element expire timeout.
This is needed in automatic IP address banning and port knocking.

Optional `merge=no` option disables IP address auto-merge. Normally it is
recommended to keep it enabled. When using external `fail2ban` program
(see below) it is recommended to be disabled.

Foomuuri startup will not add IP addresses to lists marked with optional
`start=no` option. Entries will be added later by `foomuuri-iplist.timer`
service. This can be used with "unsafe" external iplists to make sure
Foomuuri start will not fail or block your access for first minutes after
reboot.

Iplists can be manipulated from command line, for example by `fail2ban`
external program. Command `foomuuri iplist add @setname ipaddress` adds IP
address to `@setname`. Other commands are `foomuuri iplist list`,
`foomuuri iplist del` and `foomuuri iplist flush`. See command line help for
usage. Example:

```
iplist {
  @banned    dynamic=yes element_timeout=5m  # automatic IP address banning
  @blacklist merge=no                        # fail2ban
}

# Manipulate with command:
#
# foomuuri iplist add @blacklist 10.0.0.1
# foomuuri iplist del @blacklist 10.0.0.1
```

Another example how to create a macro to allow access to Valve Steam:

```
iplist {
  # Create iplist from Valve's IP addresses
  @valve_as	 https://raw.githubusercontent.com/ipverse/asn-ip/master/as/32590/ipv4-aggregated.txt
  @valve_as	 + https://raw.githubusercontent.com/ipverse/asn-ip/master/as/32590/ipv6-aggregated.txt
}

macro {
  # Create macro to allow outgoing traffic to Valve iplist
  valve-steam	udp 3478 4379-4380 27000-27100 daddr @valve_as;
  valve-steam	+ tcp 27015-27050 daddr @valve_as
}

localhost-public {
  # Allow outgoing traffic to Valve Steam
  valve-steam
}
```
