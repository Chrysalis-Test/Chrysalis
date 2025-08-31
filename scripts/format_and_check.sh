#!/bin/bash
set -e

any_failed=0

echo "Formatting code with ruff..."
if ! uv run ruff format; then
  any_failed=1
fi
echo ""

echo "Linting code with ruff..."
if ! uv run ruff check --fix; then
  any_failed=1
fi
echo ""

echo "Type checking with mypy..."
if ! uv run mypy .; then
  any_failed=1
fi
echo ""

if [ $any_failed -eq 0 ]; then
  echo "✅ All checks passed!"
else
  echo "❌ Some checks failed!"
  exit 1
fi
