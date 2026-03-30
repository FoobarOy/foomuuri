"""Hack to import foomuuri without .py extension and proper package tree."""

import sys
from importlib.abc import Loader
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader

if (  # noqa: RUF100,RUF067
    (
        spec := spec_from_loader(
            'foomuuri', SourceFileLoader('foomuuri', './src/foomuuri')
        )
    )
    and (foomuuri := module_from_spec(spec))
    and isinstance(spec.loader, Loader)
):
    spec.loader.exec_module(foomuuri)
    sys.modules['foomuuri'] = foomuuri
else:
    raise SystemError('Failed to add foomuuri to sys.modules')
