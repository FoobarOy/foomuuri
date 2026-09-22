# Miscellaneous Rules


## szone, dzone, new_szone, new_dzone

These can be specified in the [zonemap](../section/zonemap.md) section to
match the original source or destination zone, and to change it to a new
zone. They are used to branch specific traffic out into its own zone, for
example to split `vpn` and `public` (non-VPN) traffic.


## helper

The Linux kernel provides conntrack helper functionality for some services
with multiple ports, such as `ftp` (`tcp 21`). You can enable this
functionality by appending `helper kernelname-port` after a matcher, for
example `tcp 21 helper ftp-21`.

Linux provides the following helpers: `amanda, ftp, h323, irc, netbios_ns,
pptp, sane, sip, snmp, tftp`.


## mss

Sets the maximum segment size (MSS clamping) for all traffic. Some
connections, such as IPsec or PPPoE, may require this. Example:

```
localhost-vpn {
  mss 1390
  ssh
  reject log
}
```

The special value `mss pmtu` can be used to calculate the value at
runtime, based on what the routing cache has observed via Path MTU
Discovery (PMTUD). Example:

```
forward {  # internal-public
  mss pmtu
}

input {    # public-localhost
  mss pmtu
}

output {   # localhost-public
  mss pmtu
}
```


## conntrack, -conntrack

By default, rules are processed after the conntrack check (flag
`conntrack`). The flag `-conntrack` can be added to process a rule before
conntrack. Conntrack accepts established and related traffic, so a normal
rule only sees new traffic.

This can be used to count all traffic rather than just new connections, or
to accept traffic without adding it to conntrack. For example, a high-load
DNS server might accept DNS traffic without conntrack.

Example:

```
public-localhost {
  # Count all incoming traffic
  counter incoming_traffic continue -conntrack

  # Count incoming HTTP(S) traffic on a web server
  tcp dport 80 443 counter web_traffic_in continue -conntrack
  ...
}

localhost-public {
  # Count outgoing HTTP(S) traffic on a web server
  tcp sport 80 443 counter web_traffic_out continue -conntrack
  ...
}
```


## nft

A raw nftables rule can be written with `nft "raw rule here"`. For
example, the `https` rule can be written as:

```
public-localhost {
  nft "tcp dport 443 accept"
  nft "udp dport 443 accept"
  ...
}
```

`nft` can also be combined with matchers:

```
  # Jump to my-custom-chain for UDP traffic to ports 1000-2000
  udp 1000-2000 nft "jump my-custom-chain"
```

See the [nftables website](https://wiki.nftables.org/) for more
information about nftables syntax.
