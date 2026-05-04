# template

Template is very similar to [macro](macro.md). It's just another
way to define list of rules. Usually macro refers to single service
(like `domain` or `facetime`) while template refers to list of different
services. Example:

```
template outgoing_services {
  # Define template called "outgoing_services"
  dhcp-server
  domain
  https
  ntp
  ping
  ssh
}

localhost-public {
  # Include template's content here
  template outgoing_services

  # Continue with other rules
  http
  reject log
}

dmz-public {
  # Use same template for traffic coming from dmz zone
  template outgoing_services

  # Continue with other rules
  reject log
}
```

See [host firewall](../../example/host-firewall.md#multi-zone)
for real life example.
