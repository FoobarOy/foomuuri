# prerouting, postrouting, forward, input, output

These sections are used to specify packet mangle rules. Mangle rules are
processed before normal zone-zone filtering rules.

* `prerouting` is for all incoming packets
* `postrouting` is for all outgoing packets
* `forward` is for all forwarded packets (for example `internal-public`)
* `input` is for all packets targetted to `localhost` (`public-localhost`)
* `output` is for all locally generated packets (`localhost-public`)

Normally these sections are used to [set](../rule/matcher.md#mark_set) packet mark value
or [MSS clamping](../rule/misc.md#mss).

Example:

```
prerouting {
  # Do nothing if mark is already set
  mark_match -0x0000/0xff00 accept

  # Set default mark 0x100 to packet
  mark_set 0x100/0xff00

  # Change mark to 0x200 if it is coming from eth2
  iifname eth2 mark_set 0x200/0xff00

  # Use mark 0x300 for SSH traffic from eth2
  iifname eth2 ssh mark_set 0x300/0xff00
}
```

Chain type and hook priority can also be specified. Example:

```
prerouting filter raw {
  ...
}

postrouting nat srcnat + 20 {
  ...
}
```

These sections are special. Rule `drop` or `reject` will drop/reject packet
immediately. Default rule is `accept`, which will continue processing to
other special sections, zone-zone section and again to other special
sections. All of them have to accept the packet. See
[packet flow in Netfilter](https://upload.wikimedia.org/wikipedia/commons/3/37/Netfilter-packet-flow.svg)
for detailed section processing order.
