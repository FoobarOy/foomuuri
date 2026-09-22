# template

A template is very similar to a [macro](macro.md) - it's just another way
to define a list of rules. Typically, a macro refers to a single service
(such as `ssh` or `https`), while a template refers to a list of different
services.

Example:

```
template outgoing_services {
  # Define a template called "outgoing_services"
  dhcp-server
  domain
  https
  ntp
  ping
  ssh
}

localhost-public {
  # Include the template's content here
  template outgoing_services

  # Continue with other rules
  http
  reject log
}

dmz-public {
  # Use the same template for traffic coming from dmz zone
  template outgoing_services

  # Continue with other rules
  reject log
}
```

See the [host firewall example](../../example/host-firewall.md#multi-zone)
for a real-life example.
