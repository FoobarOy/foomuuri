# zone-any, any-zone, any-any

These sections are similar to a zone-zone section, except that they match
any destination (zone-any), any source (any-zone), or all traffic
(any-any). These [rules](../rule/index.md) are processed first, and
processing then continues to the normal zone-zone rules.

Foomuuri does not add a final `drop log` rule to these sections; it is
instead added to the specific zone-zone sections.

Example:

```
localhost-any {
  # Allow ping and SSH from localhost, regardless of destination.
  ping
  ssh

  # The final drop/reject rule is usually added to a specific
  # localhost-zone section, not to localhost-any.
}

localhost-public {
  # Accept all localhost-any rules (ping, SSH), plus HTTPS.
  https
  reject log
}

localhost-internal {
  # Accept all localhost-any rules (ping, SSH), plus DNS queries.
  domain
  reject log
}
```

When traffic goes from `localhost` to `public`, the applicable sections are
evaluated in the following order:

1. `any-public` rules
2. `localhost-any` rules
3. `any-any` rules
4. `localhost-public` rules (the final rule is added here even if
   `localhost-public` is missing from the configuration)

The `szone -public` matcher can be used in a rule to exclude it from
`public-localhost`. Example:

```
any-localhost {
  ssh                  # Allow SSH from anywhere
  https szone -public  # Allow HTTPS from anywhere except from public
}

localhost-any {
  ssh                  # Allow SSH to anywhere
  vnc dzone -public    # Allow VNC to anywhere except to public
}
```
