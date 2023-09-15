---
title: FOOMUURI
section: 8
header: User Manual
footer: Foomuuri 0.20
date: May 17, 2023
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


# COMMANDS

**start**
: load configuration files, generate new ruleset and load it to kernel

**start-or-good**
: same as **start** but fallback to previous "good" ruleset if loading fails

**stop**
: remove ruleset from kernel

**check**
: load configuration files and verify syntax

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


# FILES

**Foomuuri** reads configuration files from */etc/foomuuri/\*.conf*.
See full documentation for configuration syntax.


# AUTHORS

Kim B. Heino, b@bbbs.net, Foobar Oy


# BUG REPORTS

Submit bug reports <https://github.com/FoobarOy/foomuuri/issues>


# SEE ALSO

Full documentation <https://github.com/FoobarOy/foomuuri/wiki>
