# Advanced Filtering

## Port Knocking

Port knocking is a technique where attempting to connect to port A enables
access to port B from that same source IP address. This is usually used to
hide SSH service.

Example configuration:

```
zone {
  localhost
  public
}

iplist {
  # List of IP addresses that have performed initial knock..
  # It is valid for 30 seconds.
  @knock  dynamic=yes element_timeout=30s
}

public-localhost {
  # Allow SSH if IP address is in @knock iplist.
  ssh saddr @knock

  # Add source IP address to @knock iplist if there is UDP packet to port 5042.
  udp 5042 iplist_update saddr @knock drop log + ":knock"

  # Delete IP address from @knock iplist if there is any packet to any other
  # port. This prevents opening SSH if port scan is received.
  saddr @knock iplist_delete saddr @knock continue log + ":unknock"

  # ...other normal rules...
  drop log
}
```


## Automatic IP Address Banning

Foomuuri supports automatic IP address banning without any external programs.
This is usually enough, no `fail2ban` is needed. Banning happens fully on
packet path, native on nftables level.

Major differences compared to `fail2ban` program:

* Banning is done on connection count/rate level only, not on protocol
  success/failure level. This means that too many successful SSH connection
  could result banning. Therefore it is important to use high rate limit or
  list of known good hosts, or both.
* Foomuuri restart and reboot will clear ban list.
* There's no need for external programs or complex log file parsing.

Example configuration:

```
zone {
  localhost
  public
}

iplist {
  # List of known good hosts, don't ban these
  @good    192.168.0.0/24 foobar.fi

  # List containing banned IP addresses. They will be banned for 5 minutes.
  @banned  dynamic=yes element_timeout=5m
}

public-localhost {
  # Drop all new traffic if source IP address is in @banned iplist.
  # Update/reset ban expire timeout. Add this as first rule.
  saddr @banned iplist_update saddr @banned drop log + ":banned"

  # Allow SSH from known good hosts and others with rate limit.
  # If there are more than 5/minute connections add them to @banned iplist.
  ssh saddr @good
  ssh saddr_rate "5/minute burst 5"
  ssh iplist_update saddr @banned drop log + ":ban-ssh"

  # ...other normal rules...

  # Instead of normal final "drop log" rule:
  # - Allow 2/min dropped connections without banning.
  # - Somebody is port scanning us. Add IP address to @banned iplist.
  saddr_rate "2/minute burst 10" drop log
  iplist_update saddr @banned drop log + ":ban-portscan"
}
```
