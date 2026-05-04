# Statements


## accept, drop, reject

Accepts, drops or rejects traffic. Default statement for single rule is to
accept matched traffic: `tcp 443` is equal to `tcp 443 accept`.

You should always add explicit final statement as last rule to every
[zone-zone](../section/zonezone.md) section in your configuration.

* For incoming traffic from internet to localhost/intranet the recommended
  statement is `drop log`.
* For outgoing traffic from localhost/intranet to internet the recommended
  statement is `reject log`.


## continue

Continues to next rule. This is used mostly to debug rules. For example rule
`saddr 10.0.0.4 counter log continue` counts and logs traffic from 10.0.0.4 and
continues to next rule.


## return

This is a special statement to return from current nftables chain to caller
chain. Not normally used.


## masquerade, snat, dnat, snat_prefix, dnat_prefix

These statements are used in `snat` and `dnat`
[sections](../section/snat.md) to mangle traffic source or destination
IP address. See that page for description and examples.


## notrack

Mark matching packet to not be added to conntrack. This has to be done early
in `prerouting` section. For example high load DNS server can use this for
DNS queries.

Example:

```
# Incoming traffic
prerouting filter raw {
  domain notrack        # dport
  tcp sport 53 notrack  # sport
  udp sport 53 notrack
}

# Locally created traffic
output filter raw {
  domain notrack
  tcp sport 53 notrack
  udp sport 53 notrack
}
```


## queue

Forward packet to userspace for example for IPS/IDS inspection. Optional flags
and target can be specified. Example:

```
forward {
   # Forward all packets to userspace for IPS inspection
   queue flags fanout,bypass to 3-5

   # Forward matching packets only
   iifname eth0 oifname eth1 queue
}
```


## nftrace

Enable nftrace ruleset debugging for matching packets. This is usually done
in `input`, `output` or `forward` section. Tracing events can be viewed with
`nft monitor trace` command.

Example:

```
input {
  # Trace all incoming packets - generates lot of trace!
  nftrace
}

forward {
  # Trace all forwarded ssh packets
  ssh nftrace
}
```


