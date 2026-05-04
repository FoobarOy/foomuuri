# zone-any, any-zone, any-any

These sections are similar to zone-zone section, except that they match
any destination (zone-any), any source (any-zone) or all (any-any) traffic.
These [rules](../rule/index.md) are processed first and then normal zone-zone rules.
Example:

```
localhost-any {
  # Allow ping and SSH from localhost, no matter where it is going.
  ping
  ssh

  # Final drop/reject rule is usually added to specific localhost-zone
  # section, not in localhost-any.
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

Matcher `szone -public` can be used in rule to skip adding it to
`public-localhost`. Example:

```
any-localhost {
  ssh                  # allow ssh from anywhere
  https szone -public  # allow https from anywhere except from public
}

localhost-any {
  ssh                  # allow ssh to anywhere
  vnc dzone -public    # allow vnc to anywhere except to public
}
```
