# invalid, rpfilter, smurfs

Packets entering `invalid`, `rpfilter` or `smurfs` chains will be dropped.
These sections can be used to specify more rules to them. For example load
balanced IPVS traffic might enter to `invalid` chain and must be accepted:

```
invalid {
  # Accept HTTPS IPVS traffic
  https
}
```
