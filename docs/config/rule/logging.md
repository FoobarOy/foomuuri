# Logging


## counter

Adds a byte and packet counter to a rule. All new traffic matching this rule
is counted. A counter can be named or anonymous. To name a counter, add a
name after `counter`, for example `counter my_counter`.

Example:

```
localhost-public {
  # Add a named counter to count all outgoing traffic. Flag "-conntrack"
  # is used to count established traffic too.
  counter outgoing_traffic continue -conntrack

  # Accept SSH and add an anonymous counter for it
  ssh counter

  # Accept HTTP and HTTPS and add a named counter
  http counter web_traffic
  https counter web_traffic

  # Reject SMTP with a named counter
  smtp reject counter smtp_blocked
}
```

Named counter values can be listed with `foomuuri counter list`. Anonymous
counters can be listed with `foomuuri ruleset list`.


## log

Writes a log entry (journal / syslog) when traffic matches this rule. An
optional log prefix can be added; the default prefix is
`szone-dzone STATEMENT`, for example `localhost-public REJECT`.

The following variables are supported in the log prefix:

* `$(szone)`
* `$(dzone)`
* `$(statement)`

Additional text can be appended to the default log prefix with
`log + " my text"`, resulting in `localhost-public REJECT my text`.

Example:

```
public-localhost {
  # Drop and log SSH with the default prefix "public-localhost DROP"
  ssh drop log

  # Drop and log HTTP with a custom prefix, "incoming-http dropped"
  http drop log "incoming-http dropped"

  # Drop and log HTTPS with a custom prefix using variables. This results
  # in the prefix "public => localhost: DROP"
  https drop log "$(szone) => $(dzone): $(statement)"

  # Drop and log telnet with the custom prefix "public-localhost DROP:telnet"
  telnet drop log + ":telnet"         # no space, so the result is "DROP:telnet"

  # Drop and log ftp with the custom prefix "public-localhost DROP ftp-is-disabled"
  ftp drop log + " ftp-is-disabled"   # a space is included here

  # Use the default prefix "public-localhost DROP"
  drop log
}
```

Foomuuri limits logging to the [log_rate](../section/foomuuri.md) rate. By
default, the first three entries per source IP are logged, followed by one
additional entry per second.


## log_level

Overrides the global `foomuuri { log_level ... }` logging level for this
single rule.

Possible values are:

* `level emerg`
* `level alert`
* `level crit`
* `level err`
* `level warn`
* `level notice`
* `level info`
* `level debug`

Flags can optionally be appended:

* `flags tcp sequence,options` enables logging of TCP sequence and options
* `flags ip options` enables IP options
* `flags skuid` enables the socket UID
* `flags ether` enables the Ethernet link-layer address
* `flags all` enables all flags

To use the nflog infrastructure instead of syslog, specify `group 0` (or
any other number) instead of `level x`. Nflog options can be appended:

* `snaplen 256` specifies the length of packet payload to include
* `queue-threshold 20` queues packets in the kernel before sending them to
  userspace

Example:

```
public-localhost {
  # Drop and log incoming http requests at critical level, with all flags
  http drop log log_level "level crit flags all"
  ...
}
```
