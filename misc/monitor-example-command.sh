#!/bin/sh

# This is an example shell script how to use curl instead of fping to monitor
# network connectivity.
#
# target foobar {
#   command /etc/foomuuri/monitor-example-command.sh
#   command_up /etc/foomuuri/monitor.event
#   command_down /etc/foomuuri/monitor.event
# }

while true; do
    # Echoed text must be "OK" or "ERROR", everything else is ignored
    [ "$(curl --silent http://foobar.fi/test/connectivity)" = "OK" ] && echo OK || echo ERROR

    # Small wait and repeat
    sleep 5
done
