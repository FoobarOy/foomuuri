# Rule

Each line in configuration section is a single rule. Single rule contains
optional matching parts and statement part.

Order of the matchers and statement in a rule does not matter. This document
uses "what - source - destination - other-matchers - statement - log" order,
for example `http  saddr 10.1.1.1  drop  log`.
