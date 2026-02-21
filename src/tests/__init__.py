"""Hack to import foomuuri without .py extension and proper package tree."""
import sys
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader

spec = spec_from_loader(
    "foomuuri", SourceFileLoader("foomuuri", "./src/foomuuri")
)
foomuuri = module_from_spec(spec)
spec.loader.exec_module(foomuuri)
sys.modules['foomuuri'] = foomuuri
