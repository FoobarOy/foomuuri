# Foomuuri Monitor

Foomuuri includes a simple network connectivity monitor. It monitors your
internet connection by pinging an external server, and can run a command
whenever the network link goes up or down. An example
[command](https://github.com/FoobarOy/foomuuri/blob/main/misc/monitor.event)
that sends an email notification to root is included in the doc directory.
Another example for [multiple ISP](../example/multiple-isp.md)
configurations and commands, is also available.


## target

The minimal configuration is:

```
target google {
  command fping 8.8.4.4
}
```

This creates a monitor called `google` that runs the `fping` command,
pinging IP address 8.8.4.4 every second. Foomuuri parses the output and
logs up and down events. Multiple targets can be defined.

A more realistic example:

```
target my-isp-router {
  command      fping --interval=2000 172.25.31.149
  command_up   /etc/foomuuri/monitor.event
  command_down /etc/foomuuri/monitor.event
}
```

This pings IP address 172.25.31.149 every two seconds and runs the
`monitor.event` command whenever the link goes up or down. That command
sends an email notification to root.

See `man fping` or the [fping website](https://www.fping.org/) for a
description of `fping`'s parameters. Foomuuri supports both `interval` and
`squiet` modes; it is recommended to use whole seconds in `--interval`.

"Up" and "down" states are defined with the following parameters:

```
target my-isp-router {
  history_size     100       # how many results are saved
  history_up       80        # count of UPs => n     => UP
  history_down     30        # count of DOWNs >= n   => DOWN
  consecutive_up   20        # last n were UP        => UP
  consecutive_down 10        # last n were DOWN      => DOWN
  ...
}
```

A target is considered up if 80 of the last 100 pings succeeded (failures
in between are allowed) or if the last 20 pings succeeded (no failures
allowed).

A target is considered down if 30 of the last 100 pings failed, or if the
last 10 pings failed.

`curl` and other programs can also be used instead of `fping`. See the
example [shell script](https://github.com/FoobarOy/foomuuri/blob/main/misc/monitor-example-command.sh)
for how to use them.

It is recommended to use an IP address rather than a hostname as the
`fping` target. Hostname lookups will fail if the network is down when
`fping` starts. Foomuuri handles this case, but it causes a 30-second
delay and a possible `fping` restart loop.

The optional `command_down_interval` setting can be specified. Foomuuri
will run it every `down_interval` seconds (default: 600, i.e., every 10
minutes). Example:

```
target my-isp-router {
   # Connectivity is still down. Ask NetworkManager to re-initialize
   # the eth0 connection.
   command_down_interval nmcli connection up eth0

   # Run it every 15 minutes.
   down_interval 900
   ...
}
```

The up/down command receives status information via environment variables:

* `FOOMUURI_CHANGE_TYPE`: type, `target` or `group`
* `FOOMUURI_CHANGE_NAME`: name of the target or group changing state
* `FOOMUURI_CHANGE_STATE`: state, `up` or `down`
* `FOOMUURI_CHANGE_LOG`: additional logging information
* `FOOMUURI_CHANGE_HISTORY`: a list of `!` (error) or `.` (ok) characters
  indicating the status of recent checks
* `FOOMUURI_ALL_TARGET`: list of all configured targets
* `FOOMUURI_ALL_GROUP`: list of all configured groups
* `FOOMUURI_TARGET_xxx`: state (`up` or `down`) for target `xxx` (the target
  name is sanitized to remove non-alphanumeric characters)
* `FOOMUURI_GROUP_xxx`: state (`up` or `down`) for group `xxx` (the group
  name is sanitized to remove non-alphanumeric characters)

Only a single command can be specified. If you need to run multiple
commands, use a shell wrapper script to run them.

Monitor statistics are written to a file periodically. This interval can be
changed with `statistics_interval 60`. The default value is 60 seconds
(once a minute).

The number of statistics kept can be changed with `statistics_size 300`.
The default value is 300, keeping the last 300 results.


## group

Multiple monitor [targets](monitor.md#target) can be grouped into a single
monitor. Example:

```
group my-isp-group {
  target       my-isp-router google
  command_up   /etc/foomuuri/monitor.event
  command_down /etc/foomuuri/monitor.event
}
```

This creates a monitor called `my-isp-group` that includes two targets. A
group is considered up if any of its targets is up, and down only if all
of its targets are down. It is generally safer to run up/down commands in
a `group` section with multiple targets than in a single `target` section.

The optional `command_down_interval` and `down_interval` settings can also
be defined here; see [above](monitor.md#target) for details.
