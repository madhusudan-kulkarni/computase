---
name: computase
description: Performs verified local nucleotide-sequence computation with Computase. Use when an agent needs sequence composition or GC bounds, a reverse complement, translation, candidate ORFs, or IUPAC motif sites through Computase MCP tools or the isolated Skill runner.
---

# Computase

Use Computase for deterministic nucleotide computation. It accepts raw DNA/RNA or one FASTA record and never needs network access for the scientific operations themselves.

## Choose an operation

- `computase_summarize_sequence` / `summarize_sequence`: composition, dinucleotides, GC percentage/bounds, ambiguity count, or GC skew.
- `computase_reverse_complement` / `reverse_complement`: IUPAC-aware DNA/RNA reverse complement.
- `computase_translate_sequence` / `translate_sequence`: complete-codon translation with an NCBI table and explicit stop handling.
- `computase_enumerate_orfs` / `enumerate_orfs`: bounded six-frame candidate ORFs on both strands.
- `computase_scan_motif` / `scan_motif`: overlapping or non-overlapping IUPAC motif sites on forward, reverse, or both strands.

Do not describe candidate ORFs as genes. Do not use motif scanning as an alignment method.

## Runtime order

1. Prefer the five Computase MCP tools when they are already configured and available.
2. Otherwise run the bundled isolated runner with `uv` (never mutate the active project or global Python):

```bash
uv run --script skills/computase/scripts/run.py <<'EOF'
{"operation":"summarize_sequence","arguments":{"sequence":"ATGC"}}
EOF
```

The runner uses PEP 723 metadata to resolve `computase>=0.1.1,<0.2` into an isolated environment. `uv` may download or cache Computase for that environment only.

3. If `uv` is unavailable, ask before proposing any persistent installation. Do not silently run `pip install`, create a project venv, or modify the user's environment.

## Inputs and limits

Submit one sequence at a time, either raw or single-record FASTA. DNA and RNA are both supported, but mixing T and U is invalid.

- sequence: at most 5,000,000 nt
- motif: at most 500 characters
- ORFs: default 1,000, maximum 10,000 returned
- motif sites: default 10,000, maximum 100,000 returned

If a tool or runner result has `truncated: true`, report the returned count and `total_found`; do not imply the visible list is complete. That is tool truncation, distinct from an agent choosing to show only a partial view of a complete result.

## Coordinates

All coordinates are 0-based and end-exclusive on the forward reference. Strand is separate. For every ORF or motif result, the original normalized sequence slice `[start:end]` is the reported forward-reference span.

## Present results

Default to a concise scientific summary. Do not dump full JSON unless the user asks for raw output.

Include, in order:

1. The direct scientific result.
2. Relevant effective parameters and conventions.
3. Completeness: whether results were truncated (`truncated` / `total_found`) or are complete.
4. Coordinate and strand semantics when the result has positions.
5. Warnings or interpretation boundaries (for example, candidate ORFs are not genes; IUPAC GC bounds preserve uncertainty).
6. The Computase version from the result provenance.

Never echo the full input sequence back to the user.

## Errors

Relay actionable validation errors instead of silently modifying parameters. Ask for one FASTA record when given multiple records, one nucleotide alphabet when T/U are mixed, and complete codons for translation.

## Examples

See [references/usage-examples.md](references/usage-examples.md) for MCP-first and runner fallback calls plus presentation patterns.
