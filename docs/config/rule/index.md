# Rule

Each line in a configuration section is a single rule. A rule consists of
optional matchers and a statement.

The order of matchers and the statement within a rule does not matter.
This document uses the order "service - source - destination -
other-matchers - statement - log", for example:
`http  saddr 10.1.1.1  drop  log`.
