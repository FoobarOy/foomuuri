---
title: FOOMUURI
section: 8
header: User Manual
footer: Foomuuri 0.32
date: Mar 11, 2026
---

# NAME

foomuuri - multizone bidirectional nftables firewall


# SYNOPSIS

**foomuuri** [*OPTIONS*] *COMMAND*


# DESCRIPTION

**Foomuuri** is a firewall generator for nftables based on the concept of
zones. It is suitable for all systems from personal machines to corporate
firewalls, and supports advanced features such as a rich rule language,
IPv4/IPv6 rule splitting, dynamic DNS lookups, a D-Bus API and firewalld
emulation for NetworkManager's zone support.


# OPTIONS

**\--help**
: Print help and exit.

**\--version**
: Print version information and exit.

**\--verbose**
: Verbose output.

**\--quiet**
: Be quiet.

**\--force**
: Force some operations, don't check anything.

**\--soft**
: Don't force operations, check more.

**\--fork**
: Fork as a background daemon process.

**\--syslog**
: Enable syslog logging.

**\--set=OPTION=VALUE**
: Set foomuuri{} config OPTION to VALUE.


# COMMANDS

**start**
: Load configuration files, generate new ruleset and load it to kernel.

**stop**
: Remove ruleset from kernel.

**reload**
: Same as **start**, followed by **iplist refresh**.

**try-reload**
: Same as **reload**, ask confirmation to keep new config. Revert back to
old config if no reply.

**status**
: Show current status: running, zone-interface mapping.

**check**
: Load configuration files and verify syntax.

**block**
: Load "block all traffic" ruleset to kernel.

**list [ZONE-ZONE]...**
: List active ruleset currently loaded to kernel. Include whole
ruleset or only specified **ZONE-ZONE**.

**list macro [NAME | VALUE]...**
: List all macros or macros with specified NAME(s) or VALUE(s).

**list counter [COUNTER]...**
: List all or specified named COUNTER(s).

**iplist list [IPLIST]...**
: List entries of all or specified IPLIST(s).

**iplist add IPLIST [TIMEOUT] IPADDRESS [IPADDRESS]...**
: Add or refresh IPADDRESS(es) to IPLIST. TIMEOUT format is the same as in
iplist{} section, for example "4h".

**iplist del IPLIST IPADDRESS [IPADDRESS]...**
: Delete IPADDRESS(es) from IPLIST.

**iplist flush [IPLIST]...**
: Delete all added IP addresses from all or specified IPLIST(s).

**iplist refresh [IPLIST]...**
: Refresh all or specified IPLIST(s) now.

**set interface INTERFACE zone {ZONE | -}**
: Change INTERFACE to ZONE, or remove from all zones.


# FILES

**Foomuuri** reads configuration files from */etc/foomuuri/\*.conf*.
See <https://foomuuri.foobar.fi/latest/Host-Firewall/> for example
configuration.


# AUTHORS

Kim B. Heino, b@bbbs.net, Foobar Oy


# BUG REPORTS

Submit bug reports <https://github.com/FoobarOy/foomuuri/issues>


# SEE ALSO

Full documentation <https://foomuuri.foobar.fi/latest/>
