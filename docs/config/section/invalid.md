# invalid, rpfilter, smurfs

Packets entering the `invalid`, `rpfilter`, or `smurfs` chains are
dropped. These sections can be used to add more rules to them. For
example, load-balanced IPVS traffic might enter the `invalid` chain and
must be explicitly accepted:

```
invalid {
  # Accept HTTPS IPVS traffic
  https
}
```
