# hook

Foomuuri can run external command before/after starting and stopping. This
section configures those commands. Example:

```
hook {
  pre_start  command-to-run with arguments before loading ruleset
  post_start echo firewall started
  pre_stop   /etc/foomuuri/pre_stop.sh
  post_stop  /etc/foomuuri/post_stop.sh with arguments
}
```
