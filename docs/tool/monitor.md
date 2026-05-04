# Foomuuri Monitor

Foomuuri includes simple network connectivity monitor. It can monitor your
internet connection by pinging some external server. Command can
be run if network link goes up or down. Example
[command](https://github.com/FoobarOy/foomuuri/blob/main/misc/monitor.event)
to send an email notification to root is included in doc directory. Another
examples are [multiple ISP](../example/multiple-isp.md) configurations and commands.


## target

Minimal configuration is:

```
target google {
  command fping 8.8.4.4
}
```

This creates monitor called `google` and runs `fping` command pinging
IP 8.8.4.4 every second. Foomuuri parses its output and logs up and down
events. Multiple targets can be defined.

Better real life example is:

```
target my-isp-router {
  command      fping --interval=2000 172.25.31.149
  command_up   /etc/foomuuri/monitor.event
  command_down /etc/foomuuri/monitor.event
}
```

This pings IP 172.25.31.149 every two seconds and runs `monitor.event`
command when link goes up or down. That command sends an email notification
to root.

See `man fping` or its [website](https://www.fping.org/) for description
of `fping` parameters. Foomuuri supports both `interval` and `squiet` modes.
It is recommended to use full seconds in `--interval`.

"Up" and "down" are defined with parameters:

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

Target is considered up if 80 of the last 100 pings were successful (allowing
failures in between) and last 20 pings were successful (no failures allowed).

Target is considered down if 30 of the last 100 pings were failures or
last 10 pings were failures.

`curl` and other programs can also be used instead of `fping`. See example
[shell script](https://github.com/FoobarOy/foomuuri/blob/main/misc/monitor-example-command.sh)
how to use them.

It is recommended to use IP address instead of hostname as `fping` target.
Hostname lookup will fail if network is down when `fping` starts. Foomuuri
will handle this but it will cause 30 second delay and possible `fping`
restart loop.

Optional `command_down_interval` can be specified. Foomuuri will run it every
`down_interval` seconds (default to 600, every 10 minutes). Example:

```
target my-isp-router {
   # Connectivity is still down. Ask NetworkManager to re-initialize
   # eth0 connection.
   command_down_interval nmcli connection up eth0

   # Run it every 15 minutes
   down_interval 900
   ...
}
```

Up/down command receives status information in environment variables:

* `FOOMUURI_CHANGE_TYPE`: type `target` or `group`
* `FOOMUURI_CHANGE_NAME`: name of target or group changing state
* `FOOMUURI_CHANGE_STATE`: state `up` or `down`
* `FOOMUURI_CHANGE_LOG`: extra logging information
* `FOOMUURI_CHANGE_HISTORY`: list of `!` (error) or `.` (ok)
   indicating status of last checks
* `FOOMUURI_ALL_TARGET`: list of all configured targets
* `FOOMUURI_ALL_GROUP`: list of all configured groups
* `FOOMUURI_TARGET_xxx`: state `up` or `down` for target `xxx`
* `FOOMUURI_GROUP_xxx`: state `up` or `down` for group `xxx`

Only single command can be specified. If you need to run multiple commands
use a shell wrapper script to run them.

Monitor statistics are written to a file once a minute.


## group

Multiple monitor [targets](monitor.md#target) can be grouped to single
monitor. Example:

```
group my-isp-group {
  target       my-isp-router google
  command_up   /etc/foomuuri/monitor.event
  command_down /etc/foomuuri/monitor.event
}
```

This creates a monitor called `my-isp-group` which includes two targets.
Group is considered up if any of the targets is up. It is considered down
if all of the targets are down. It is usually safer to run up and down
commands in `group {}` with multiple targets than in single `target {}`.

Optional `command_down_interval` and `down_interval` can also be defined.
See [above](monitor.md#target) for description.
