# macro

Rather than writing the rule `tcp 443`, it is easier and more readable to
write `https`. These alias names are called macros. A macro can be used
in any part of a rule, defining it fully or partially.

```
macro {
  # Define a service as a macro
  smtp        tcp 25
  https       tcp 443; udp 443
  googlemeet  udp 3478 19302-19309; https

  # Define a rate limit as a macro
  ssh_rate    saddr_rate "5/minute burst 5"

  # A long macro can be split across multiple lines with "+" (append to the
  # previous line) or "\" (continue on the next line).
  # Warning: using "+" or "\" does not add ";". You must add it yourself
  # when needed.
  good_hosts  10.0.0.1 fd00:f00::1
  good_hosts  + 10.0.0.2 fd00:f00::2
  another     10.0.0.3 \
              10.0.0.4
  semicolon   http
  semicolon   + ; https
}
```

You can use the macros above in other sections:

```
localhost-public {
  https daddr good_hosts   # Allow HTTPS to specific IP addresses
  tcp 23 daddr good_hosts  # Allow TCP 23 to specific IP addresses
  https reject             # Reject all other HTTPS traffic
  googlemeet               # Allow Google Meet to everywhere
}

public-localhost {
  ssh ssh_rate             # Allow incoming SSH with a rate limit
}
```

A macro can include other macros, as `googlemeet` does in the example
above.

Using `;` in a macro splits it into multiple rule lines. You must use it
when a macro combines two different rules, such as `tcp 443` and
`udp 443` in the `https` macro, or `udp XXX` and `https` in the
`googlemeet` macro. Do not use it when defining a list of items (IP
addresses, for example) for a single rule, as in `good_hosts`.

All
[known macros](https://github.com/FoobarOy/foomuuri/blob/main/etc/default.services.conf)
can be listed with `foomuuri macro list`.

Macro expansion can be skipped by writing a word in quotes, for example,
`"ssh"` is kept as `ssh` rather than being expanded to `tcp 22`.

For safety, macro expansion is not performed in the `zone` or `foomuuri`
sections.
