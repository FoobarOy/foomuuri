---
title: FOOMUURI
section: 8
header: User Manual
footer: Foomuuri 0.26
date: Nov 13, 2024
---

# NAME

foomuuri - multizone bidirectional nftables firewall


# SYNOPSIS

**foomuuri** [*OPTION*] [*COMMAND*]


# DESCRIPTION

**Foomuuri** is a firewall generator for nftables based on the concept of
zones. It is suitable for all systems from personal machines to corporate
firewalls, and supports advanced features such as a rich rule language,
IPv4/IPv6 rule splitting, dynamic DNS lookups, a D-Bus API and FirewallD
emulation for NetworkManager's zone support.


# OPTIONS

`--help`
: display this help and exit

`--version`
: output version information and exit

`--verbose`
: verbose output

`--quiet`
: be quiet

`--force`
: force some operations, don't check anything

`--soft`
: don't force operations, check more

`--set=option=value`
: set config option to value

# COMMANDS

**start**
: load configuration files, generate new ruleset and load it to kernel

**stop**
: remove ruleset from kernel

**reload**
: same as **start**, followed by resolve and iplist refresh

**status**
: show current status: running, zone-interface mapping

**check**
: load configuration files and verify syntax

**block**
: load "block all traffic" ruleset

**list**
: list active ruleset currently loaded to kernel

**list zone-zone {zone-zone...}**
: list active ruleset for **zone-zone** currently loaded to kernel

**list macro**
: list all known macros

**list counter**
: list all named counters

**iplist list**
: list entries in all configured iplists and resolves

**iplist list name {name...}**
: list entries in named iplist/resolve

**iplist add name {timeout} ipaddress {ipaddress...}**
: add or refresh IP address to iplist

**iplist del name ipaddress {ipaddress...}**
: delete IP address from iplist

**iplist flush name {name...}**
: delete all IP addresses from iplist

**iplist refresh name {name...}**
: refresh iplist @name entries now

**set interface {interface} zone {zone}**
: change interface to zone

**set interface {interface} zone -**
: remove interface from all zones

# FILES

**Foomuuri** reads configuration files from */etc/foomuuri/\*.conf*.
See full documentation for configuration syntax.


# AUTHORS

Kim B. Heino, b@bbbs.net, Foobar Oy


# BUG REPORTS

Submit bug reports <https://github.com/FoobarOy/foomuuri/issues>


# SEE ALSO

Full documentation <https://github.com/FoobarOy/foomuuri/wiki>
