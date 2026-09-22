# Statements


## accept, drop, reject

Accepts, drops, or rejects traffic. The default statement for a rule is to
accept matched traffic: `tcp 443` is equivalent to `tcp 443 accept`.

You should always add an explicit final statement as the last rule in
every [zone-zone](../section/zonezone.md) section of your configuration.

* For incoming traffic from the internet to localhost/intranet, the
  recommended statement is `drop log`.
* For outgoing traffic from localhost/intranet to the internet, the
  recommended statement is `reject log`.


## continue

Continues to the next rule. This is mostly used for debugging rules. For
example, the rule `saddr 10.0.0.4 counter log continue` counts and logs
traffic from 10.0.0.4, then continues to the next rule.


## return

A special statement that returns from the current nftables chain to the
caller chain. Not normally used.


## masquerade, snat, dnat, snat_prefix, dnat_prefix

These statements are used in the `snat` and `dnat`
[sections](../section/snat.md) to rewrite the traffic's source or
destination IP address. See that page for a description and examples.


## notrack

Marks a matching packet so that it is not added to conntrack. This must
be done early in the `prerouting` section. For example, a high-load DNS
server can use this for DNS queries.

Example:

```
# Incoming traffic
prerouting filter raw {
  domain notrack        # dport
  tcp sport 53 notrack  # sport
  udp sport 53 notrack
}

# Locally generated traffic
output filter raw {
  domain notrack
  tcp sport 53 notrack
  udp sport 53 notrack
}
```


## queue

Forwards a packet to userspace, for example for IPS/IDS inspection.
Optional flags and a target can be specified. Example:

```
forward {
   # Forward all packets to userspace for IPS inspection
   queue flags fanout,bypass to 3-5

   # Forward matching packets only
   iifname eth0 oifname eth1 queue
}
```


## nftrace

Enables nftrace ruleset debugging for matching packets. This is usually
done in the `input`, `output`, or `forward` section. Trace events can be
viewed with the `nft monitor trace` command.

Example:

```
input {
  # Trace all incoming packets - this generates a lot of trace output!
  nftrace
}

forward {
  # Trace all forwarded ssh packets
  ssh nftrace
}
```
