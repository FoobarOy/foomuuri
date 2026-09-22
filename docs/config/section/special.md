# prerouting, postrouting, forward, input, output

These sections are used to specify packet-mangling rules. Mangle rules
are processed before the normal zone-zone filtering rules.

* `prerouting` applies to all incoming packets
* `postrouting` applies to all outgoing packets
* `forward` applies to all forwarded packets (for example, `internal-public`)
* `input` applies to all packets destined for `localhost` (`public-localhost`)
* `output` applies to all locally generated packets (`localhost-public`)

These sections are normally used to [set](../rule/matcher.md#mark_set) a
packet's mark value or for [MSS clamping](../rule/misc.md#mss).

Example:

```
prerouting {
  # Do nothing if the mark is already set
  mark_match -0x0000/0xff00 accept

  # Set the default mark 0x100 on the packet
  mark_set 0x100/0xff00

  # Change the mark to 0x200 if the packet is coming from eth2
  iifname eth2 mark_set 0x200/0xff00

  # Use mark 0x300 for SSH traffic from eth2
  iifname eth2 ssh mark_set 0x300/0xff00
}
```

The chain type and hook priority can also be specified. Example:

```
prerouting filter raw {
  ...
}

postrouting nat srcnat + 20 {
  ...
}
```

These sections are special: a `drop` or `reject` rule drops or rejects the
packet immediately. The default rule is `accept`, which allows processing
to continue to other special sections, the zone-zone section, and then
back to other special sections. All of them must accept the packet for
it to pass. See the
[Netfilter packet flow diagram](https://upload.wikimedia.org/wikipedia/commons/3/37/Netfilter-packet-flow.svg)
for the detailed section processing order.
