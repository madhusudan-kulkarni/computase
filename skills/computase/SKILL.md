---
name: computase
description: Performs verified local nucleotide-sequence computation with Computase. Use when an agent needs sequence composition or GC bounds, a reverse complement, translation, candidate ORFs, or IUPAC motif sites through the five Computase MCP tools.
---

# Computase

Use Computase for deterministic nucleotide computation. It accepts raw DNA/RNA or one FASTA record and never needs network access.

## Choose a tool

- `computase_summarize_sequence`: composition, dinucleotides, GC percentage/bounds, ambiguity count, or GC skew.
- `computase_reverse_complement`: IUPAC-aware DNA/RNA reverse complement.
- `computase_translate_sequence`: complete-codon translation with an NCBI table and explicit stop handling.
- `computase_enumerate_orfs`: bounded six-frame candidate ORFs on both strands.
- `computase_scan_motif`: overlapping or non-overlapping IUPAC motif sites on forward, reverse, or both strands.

Do not describe candidate ORFs as genes. Do not use motif scanning as an alignment method.

## Inputs and limits

Submit one sequence at a time, either raw or single-record FASTA. DNA and RNA are both supported, but mixing T and U is invalid.

- sequence: at most 5,000,000 nt
- motif: at most 500 characters
- ORFs: default 1,000, maximum 10,000 returned
- motif sites: default 10,000, maximum 100,000 returned

If a tool returns `truncated: true`, report the returned count and `total_found`; do not imply the visible list is complete.

## Coordinates

All coordinates are 0-based and end-exclusive on the forward reference. Strand is separate. For every ORF or motif result, the original normalized sequence slice `[start:end]` is the reported forward-reference span.

## Errors

Relay actionable validation errors instead of silently modifying parameters. Ask for one FASTA record when given multiple records, one nucleotide alphabet when T/U are mixed, and complete codons for translation.

## Examples

See [references/usage-examples.md](references/usage-examples.md) for compact Python and MCP calls.
