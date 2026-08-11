# Contributing

## Setup

```bash
uv sync --locked --extra dev
```

## Checks

```bash
uv lock --check
uv run --locked ruff format --check src tests evaluations scripts skills/computase/scripts
uv run --locked ruff check src tests evaluations scripts skills/computase/scripts
uv run --locked mypy src tests evaluations scripts skills/computase/scripts
uv run --locked pytest -q
uv run --locked python -m evaluations.runner
```

## Conventions

- Keep public operations typed and documented.
- Preserve 0-based, end-exclusive forward-reference coordinates.
- Use `InvalidSequenceError` for sequence/pattern input and `InvalidParameterError` for operation settings.
- Do not echo full input sequences in results.
- Keep MCP adapters thin; scientific behavior belongs in the Python core.

## Scientific tests

Behavior changes require independent expected values. Prefer static vectors from GenBank, NCBI, or published sources and cite the accession or publication in the fixture. Do not derive expected values by calling the wrapper under test. Add Hypothesis invariants where they can expose coordinate, normalization, or complement errors.

Report a discrepancy through the
[scientific correctness form](https://github.com/madhusudan-kulkarni/computase/issues/new?template=scientific-correctness.yml)
using a minimized, non-sensitive sequence. Security vulnerabilities belong in
[private vulnerability reporting](https://github.com/madhusudan-kulkarni/computase/security/advisories/new).

Open one focused pull request per operation or concern. CI must be green before merge.
