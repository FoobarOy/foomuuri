# Advanced Filtering

## Port Knocking

Port knocking is a technique in which attempting to connect to port A
enables access to port B from that same source IP address. It is
typically used to hide the SSH service.

Example configuration:

```
zone {
  localhost
  public
}

iplist {
  # List of IP addresses that have performed the initial knock.
  # Entries are valid for 30 seconds.
  @knock  dynamic=yes element_timeout=30s
}

public-localhost {
  # Allow SSH if the source IP address is in the @knock iplist.
  ssh saddr @knock

  # Add the source IP address to the @knock iplist on a UDP packet to port 5042.
  udp 5042 iplist_update saddr @knock drop log + ":knock"

  # Remove the IP address from the @knock iplist on any packet to any other
  # port. This prevents SSH access if a port scan is received.
  saddr @knock iplist_delete saddr @knock continue log + ":unknock"

  # ...other normal rules...
  drop log
}
```


## Automatic IP Address Banning

Foomuuri supports automatic IP address banning without any external
programs, so `fail2ban` is usually unnecessary. Banning happens entirely
on the packet path, natively at the nftables level.

Key differences compared to the `fail2ban` program:

* Banning is based on connection count/rate alone, not on protocol
  success/failure. This means that too many successful SSH connections
  could still trigger a ban, so it is important to use a high rate limit,
  a list of known good hosts, or both.
* A Foomuuri restart or a reboot clears the ban list.
* No external programs or complex log file parsing are required.

Example configuration:

```
zone {
  localhost
  public
}

iplist {
  # List of known good hosts; never ban these.
  @good    192.168.0.0/24 foobar.fi

  # List of banned IP addresses. They are banned for 5 minutes.
  @banned  dynamic=yes element_timeout=5m
}

public-localhost {
  # Drop all new traffic if the source IP address is in the @banned iplist.
  # Update/reset the ban expiry timeout. Add this as the first rule.
  saddr @banned iplist_update saddr @banned drop log + ":banned"

  # Allow SSH from known good hosts, and from others up to a rate limit.
  # If a source exceeds 5 connections per minute, add it to the @banned iplist.
  ssh saddr @good
  ssh saddr_rate "5/minute burst 5"
  ssh iplist_update saddr @banned drop log + ":ban-ssh"

  # ...other normal rules, with or without similar rate-limit banning...

  # Instead of the normal final "drop log" rule:
  # - Make sure @good addresses are never banned.
  # - Allow up to 2/minute dropped connections without banning.
  # - If the rate is exceeded, assume it's a port scan and ban the source.
  saddr @good drop log
  saddr_rate "2/minute burst 10" drop log
  iplist_update saddr @banned drop log + ":ban-portscan"
}
```
