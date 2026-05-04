# Miscellaneous Rules


## szone, dzone, new_szone, new_dzone

These can be specified in [zonemap](../section/zonemap.md) section to match
original source or destination zone, and to change it to a new zone. These
are used to branch out some specific traffic to its own zone, for example
to split `vpn` and `public` (non-VPN) traffic.


## helper

Linux kernel provides conntrack helper functionality to some services with
multiple ports, like `ftp` (tcp 21). You can enable this functionality by
appending `helper kernelname-port` after matcher. For example
`tcp 21 helper ftp-21`.

Linux has following helpers: `amanda, ftp, h323, irc, netbios_ns, pptp,
sane, sip, snmp, tftp`


## mss

Sets maximum segment size (MSS clamping) to all traffic. Some connections,
like IPsec or PPPoE, might require this. Example:

```
localhost-vpn {
  mss 1390
  ssh
  reject log
}
```

Special value `mss pmtu` can be used to calculate the value in runtime
based on what the routing cache has observed via Path MTU Discovery (PMTUD).
Example:

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

Rules are processed after conntrack check (flag `conntrack`, default value).
Flag `-conntrack` can be added to process rule before conntrack. Conntrack
will accept established and related traffic so normal rule will see only new
traffic.

This can be used to count all traffic instead of new connections only, or
to accept traffic without adding it to conntrack. For example high load
DNS server might accept DNS traffic without conntrack.

Example:

```
public-localhost {
  # Count all incoming traffic
  counter incoming_traffic continue -conntrack

  # Count incoming HTTP(S) traffic in web server
  tcp dport 80 443 counter web_traffic_in continue -conntrack
  ...
}

localhost-public {
  # Count outgoing HTTP(S) traffic in web server
  tcp sport 80 443 counter web_traffic_out continue -conntrack
  ...
}
```


## nft

Raw nftables rule can be written with `nft "raw rule here"`. For example,
`https` rule can be written as:

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

See [nftables web page](https://wiki.nftables.org/) for more information
about nftables syntax.
