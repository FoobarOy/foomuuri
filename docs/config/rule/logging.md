# Logging


## counter

Add byte and packet counter to rule. All traffic matching this rule will be
counted. Counter can be named or anonymous. To name a counter add name after
`counter`, for example `counter my_counter`.

Example:

```
localhost-public {
  # Add named counter to count all outgoing traffic
  counter outgoing_traffic continue -conntrack

  # Accept ssh and add anonymous counter for it
  ssh counter

  # Accept http + https and add named counter
  http counter web_traffic
  https counter web_traffic

  # Reject SMTP with named counter
  smtp reject counter smtp_blocked
}
```

Named counter values can be listed with `foomuuri list counter`. Anonymous
counters can be listed with `foomuuri list`.


## log

Write log entry (journal / syslog) when traffic matches this rule. Optional
log prefix can be added. Default prefix is `szone-dzone STATEMENT`, for example
`localhost-public REJECT`.

Following variables are supported in log prefix:

* `$(szone)`
* `$(dzone)`
* `$(statement)`

Additional text to default log prefix can be added with `log + " my text"`,
resulting `localhost-public REJECT my text`.

Example:

```
public-localhost {
  # Drop and log ssh with default prefix "public-localhost DROP"
  ssh drop log

  # Drop and log http with custom prefix "incoming-http dropped"
  http drop log "incoming-http dropped"

  # Drop and log https with custom prefix with variables. This results to
  # prefix "public => localhost: DROP"
  https drop log "$(szone) => $(dzone): $(statement)"

  # Drop and log telnet with custom prefix "public-localhost DROP:telnet"
  telnet drop log + ":telnet"         # no space included to get "DROP:telnet"

  # Drop and log ftp with custom prefix "public-localhost DROP ftp-is-disabled"
  ftp drop log + " ftp-is-disabled"   # space is included here

  # Use default prefix "public-localhost DROP"
  drop log
}
```

Foomuuri will limit logging to [log_rate](../section/foomuuri.md) rate.
Default value is to log first three entries per source IP and then one
additional entry per second.


## log_level

This overrides global `foomuuri { log_level ... }` logging level for this
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

Optionally flags can be appended:

* `flags tcp sequence,options` enables logging of TCP sequence and options
* `flags ip options` enables IP options
* `flags skuid` enables socket UID
* `flags ether` enables ethernet link layer address
* `flags all` enables all flags

To use nflog infrastructure instead of syslog specify value `group 0` (or any
other number) instead of `level x`. Nflog options can be appended:

* `snaplen 256` specifies length of packet payload to include
* `queue-threshold 20` will queue packets inside the kernel before sending
  them to userspace

Example:

```
public-localhost {
  # Drop and log incoming http requests with critical level, all flags
  http drop log log_level "level crit flags all"
  ...
}
```

