#!/bin/bash
set -e

uv run sphinx-build -M clean docs/source docs/_build
uv run sphinx-build -M html docs/source docs/_build
open docs/_build/html/index.html
