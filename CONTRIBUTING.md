# Contributing

## Setup

```bash
uv sync --locked --extra dev
```

## Checks

```bash
uv lock --check
uv run ruff format --check src tests evaluations
uv run ruff check src tests evaluations
uv run mypy src tests evaluations
uv run pytest -q
uv run python -m evaluations.runner
```

## Conventions

- Keep public operations typed and documented.
- Preserve 0-based, end-exclusive forward-reference coordinates.
- Use `InvalidSequenceError` for sequence/pattern input and `InvalidParameterError` for operation settings.
- Do not echo full input sequences in results.
- Keep MCP adapters thin; scientific behavior belongs in the Python core.

## Scientific tests

Behavior changes require independent expected values. Prefer static vectors from GenBank, NCBI, or published sources and cite the accession or publication in the fixture. Do not derive expected values by calling the wrapper under test. Add Hypothesis invariants where they can expose coordinate, normalization, or complement errors.

Open one focused pull request per operation or concern. CI must be green before merge.
