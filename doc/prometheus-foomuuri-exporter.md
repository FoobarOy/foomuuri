---
title: PROMETHEUS-FOOMUURI-EXPORTER
section: 1
header: User Manual
footer: prometheus-foomuuri-exporter 0.32
date: Mar 11, 2026
---

# NAME

prometheus-foomuuri-exporter - Prometheus exporter for Foomuuri metrics


# SYNOPSIS

**prometheus-foomuuri-exporter** [*OPTIONS*]


# DESCRIPTION

**prometheus-foomuuri-exporter** reads Foomuuri metrics and exports them
to Prometheus.


# OPTIONS

**\--help**
: Print help and exit.

**\--address ADDRESS**
: Listen address. (default: ::)

**\--port PORT**
: Listen port number. (default: 11041)

**\--tls-certificate FILENAME**
: TLS certificate file name.

**\--tls-key FILENAME**
: TLS key file name.

**\--no-monitor-statistics**
: Do not export Foomuuri Monitor statistics.

**\--no-ruleset-statistics**
: Do not export ruleset statistics.

**\--statistics-file FILENAME**
: Foomuuri Monitor statistics file name.

**\--set-include REGEXP**
: Set names to be included to ruleset size statistics.

**\--set-exclude REGEXP**
: Set names to be excluded from ruleset size statistics.

**\--counter-include REGEXP**
: Counter names to be included to ruleset traffic statistics.

**\--counter-exclude REGEXP**
: Counter names to be excluded from ruleset traffic statistics.


# AUTHORS

Kim B. Heino, b@bbbs.net, Foobar Oy


# BUG REPORTS

Submit bug reports <https://github.com/FoobarOy/foomuuri/issues>


# SEE ALSO

Full documentation <https://github.com/FoobarOy/foomuuri/wiki>
