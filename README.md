# Computase

Verified local bioinformatics computation.

Computase provides five sequence operations through equally supported Python and MCP interfaces:

- sequence composition, GC bounds, and GC skew
- DNA/RNA reverse complements
- translation with selectable NCBI genetic codes
- six-frame candidate ORF enumeration
- IUPAC motif scanning on either strand

Computase is sequence-only in 0.1.0. It does not predict genes, fetch remote records, run alignments, or provide generic statistics.

## Install

```bash
pip install computase
```

Python 3.11 or newer is required. Computation is local; input sequences are not sent to a service.

## Python

```python
from computase.seq import reverse_complement, summarize_sequence

summary = summarize_sequence(">example\nAAGCSWN\n")
print(summary.gc_min_percent, summary.gc_max_percent)

result = reverse_complement("AUGC")
print(result.reverse_complement)
```

All operations accept raw sequences or one FASTA record. Results include the Computase version and effective parameters but never echo the full input sequence.

## MCP over stdio

```json
{
  "mcpServers": {
    "computase": {
      "command": "computase"
    }
  }
}
```

The five tools are `computase_summarize_sequence`, `computase_reverse_complement`, `computase_translate_sequence`, `computase_enumerate_orfs`, and `computase_scan_motif`.

## MCP over streamable HTTP

```bash
computase --transport streamable-http --host 127.0.0.1 --port 8000
```

Connect an MCP client to `http://127.0.0.1:8000/mcp`. HTTP binds to localhost by default.

## Scientific conventions

- Coordinates are 0-based and end-exclusive on the forward reference.
- Coordinates index the normalized sequence after FASTA headers and whitespace are removed.
- Strand is reported separately; `normalized_sequence[start:end]` reproduces each forward span.
- ORFs are candidates, not gene predictions.
- IUPAC GC bounds preserve uncertainty rather than assigning probabilities.
- Sequence length is capped at 5,000,000 nucleotides; motif and result limits are enforced.

## Companion Skill

`skills/computase/SKILL.md` teaches agents when and how to choose the five MCP tools. Longer examples are in `skills/computase/references/usage-examples.md`.

## Development

Use `uv sync --locked --extra dev`, then run:

```bash
uv run ruff format --check src tests evaluations
uv run ruff check src tests evaluations
uv run mypy src tests evaluations
uv run pytest -q
uv run python -m evaluations.runner
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for reference-vector requirements.

## License

MIT. See `LICENSE`.
