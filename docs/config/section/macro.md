# macro

Instead of writing rule `tcp 443` it is easier and more readable to use rule
`https`. These alias names are called macros. Macro can be used in any part
of rule you want to, defining rule fully or partially.

```
macro {
  # Define service as macro
  smtp        tcp 25
  https       tcp 443; udp 443
  googlemeet  udp 3478 19302-19309; https

  # Define rate limit as macro
  ssh_rate    saddr_rate "5/minute burst 5"

  # Long macro can be split to multiple lines with "+" (append to previous) or
  # "\" (continue in next line).
  # Warning: Using "+" or "\" does not add ";". You must add it yourself when
  # needed.
  good_hosts  10.0.0.1 fd00:f00::1
  good_hosts  + 10.0.0.2 fd00:f00::2
  another     10.0.0.3 \
              10.0.0.4
  semicolon   http
  semicolon   + ; https
}
```

You can use above macros in other sections:

```
localhost-public {
  https daddr good_hosts   # Allow https to specific IP addresses
  tcp 23 daddr good_hosts  # Allow TCP 23 to specific IP addresses
  https reject             # Reject all other https traffic
  googlemeet               # Allow Google Meet to everywhere
}

public-localhost {
  ssh ssh_rate             # Allow incoming ssh with rate limit
}
```

Macro can include other macros, as `googlemeet` in above example does.

Using `;` in macro splits it to multiple rule lines. You must use it
when macro contains two different rules, like `tcp 443` and `udp 443` in
`https` macro, or `udp XXX` and `https` in `googlemeet` macro.
Do not use it when creating list of items (IP addresses for example)
for single rule, like in `good_hosts`.

All
[known macros](https://github.com/FoobarOy/foomuuri/blob/main/etc/default.services.conf)
can be listed with `foomuuri list macro` command.

Macro expansion can be skipped by writing word in quotes. For example `"ssh"`
is kept as `ssh` and not expanded to `tcp 22`.

For safety reasons macro expansion is not done in `zone` or `foomuuri`
sections.

