# Computase

[![PyPI](https://img.shields.io/pypi/v/computase)](https://pypi.org/project/computase/)
[![Python](https://img.shields.io/pypi/pyversions/computase)](https://pypi.org/project/computase/)
[![CI](https://github.com/madhusudan-kulkarni/computase/actions/workflows/ci.yml/badge.svg)](https://github.com/madhusudan-kulkarni/computase/actions/workflows/ci.yml)

Computase is a local Python library for small, well-defined DNA and RNA sequence
calculations:

- nucleotide composition, GC bounds, and GC skew
- DNA or RNA reverse complements
- translation with selectable NCBI genetic-code tables
- six-frame candidate ORF enumeration
- IUPAC motif searches on either strand

The Python API is the primary interface. The same operations are also available
through the optional [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
interface for local agent workflows. Computation runs locally; input sequences are
not sent to a service.

## Install

For most Python environments:

```bash
pip install computase
```

For a project managed with [uv](https://docs.astral.sh/uv/):

```bash
uv add computase
```

Python 3.11 or newer is required.

## Quick start

```python
from computase.seq import translate_sequence

sequence = ">synthetic-cds\nATGGCCATTGTAATGGGCCGCTGAAAGGGTGCCCGATAG\n"
result = translate_sequence(sequence, table_id=1)

print(result.model_dump())
```

Representative output (`computase_version` matches the installed release):

```text
{'computase_version': '<installed version>', 'parameters': {'table_id': 1, 'stop_handling': 'translate-through'}, 'protein': 'MAIVMGR*KGAR*', 'table_id': 1, 'table_name': 'Standard', 'stop_handling': 'translate-through', 'codon_count': 13, 'stopped_early': False}
```

Results are typed Pydantic models. They record the Computase version and effective
parameters, but never echo the full input sequence.

See the [Python examples](https://github.com/madhusudan-kulkarni/computase/blob/main/docs/python-examples.md)
for concise, runnable examples of all five sequence operations.

## Capabilities and validation

| Scientific task | Python function | Contract and validation evidence |
| --- | --- | --- |
| Composition, GC content bounds, and GC skew | `summarize_sequence` | Preserves IUPAC uncertainty; checked against the GenBank HBB coding sequence and composition/property invariants |
| DNA/RNA reverse complement | `reverse_complement` | Preserves the input alphabet and IUPAC symbols; checked against an M13 reference sequence and the reverse-complement involution property |
| NCBI genetic-code translation | `translate_sequence` | Uses a selected NCBI table and requires complete codons; checked against an NCBI translation example and table-specific codons |
| Six-frame candidate ORF enumeration | `enumerate_orfs` | Reports forward-reference coordinates and explicit start, stop, and nesting policies; checked with synthetic fixtures spanning all six frames and coordinate round trips |
| IUPAC motif search | `scan_motif` | Supports ambiguous symbols, overlapping matches, and either strand; checked against the pUC19 EcoRI site and interval/property tests |

These checks establish the documented conventions and regression boundaries; they
do not establish correctness for every biological interpretation or use case.
If a result differs from an independent reference, use the
[scientific correctness report](https://github.com/madhusudan-kulkarni/computase/issues/new?template=scientific-correctness.yml)
with a minimized, non-sensitive sequence.

## Scientific scope and conventions

- Inputs are raw nucleotide strings or a single FASTA record, not multi-record files.
- Coordinates are 0-based and end-exclusive on the normalized forward reference,
  after FASTA headers and whitespace are removed.
- Strand is reported separately; `normalized_sequence[start:end]` reproduces each
  reported forward span.
- ORFs are sequence candidates, not gene predictions.
- IUPAC GC bounds preserve uncertainty rather than assigning probabilities.
- Sequence length is capped at 5,000,000 nucleotides; motif and result limits are
  enforced.
- Computase 0.1.x does not fetch records, align sequences, or annotate genes.

## Optional MCP interface

### stdio

With uv installed, `uvx` can run the MCP server without installing Computase
into the current environment:

```json
{
  "mcpServers": {
    "computase": {
      "command": "uvx",
      "args": ["computase"]
    }
  }
}
```

If Computase was installed with `pip` into an environment available to the MCP
client, use `computase` as the command and omit the arguments. For a uv-managed
project, run `uv run computase` from the project root; configure the MCP client
with `uv` as the command and `["run", "computase"]` as the arguments.

The five tools are `computase_summarize_sequence`, `computase_reverse_complement`, `computase_translate_sequence`, `computase_enumerate_orfs`, and `computase_scan_motif`.

### Streamable HTTP

```bash
uvx computase --transport streamable-http --host 127.0.0.1 --port 8000
```

Connect an MCP client to `http://127.0.0.1:8000/mcp`. HTTP binds to localhost by default.

Do not expose the Computase HTTP server directly to a public network. Non-loopback
deployment requires a separately managed TLS boundary that authenticates every
request and enforces request-size, concurrency, and rate limits.

## Companion Skill

`skills/computase/SKILL.md` teaches agents when and how to choose the five MCP tools. Longer examples are in `skills/computase/references/usage-examples.md`.

## Development

Use `uv sync --locked --extra dev`, then run:

```bash
uv lock --check
uv run --locked ruff format --check src tests evaluations scripts
uv run --locked ruff check src tests evaluations scripts
uv run --locked mypy src tests evaluations scripts
uv run --locked pytest -q
uv run --locked python -m evaluations.runner
```

See [CONTRIBUTING.md](https://github.com/madhusudan-kulkarni/computase/blob/main/CONTRIBUTING.md)
for reference-vector requirements.

## Citation

If Computase contributes to your work, cite the software metadata in
[CITATION.cff](https://github.com/madhusudan-kulkarni/computase/blob/main/CITATION.cff).
GitHub also exposes this through **Cite this repository**.

## License

Computase is licensed under the
[MIT License](https://github.com/madhusudan-kulkarni/computase/blob/main/LICENSE).
