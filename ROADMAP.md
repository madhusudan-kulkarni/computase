# Computase roadmap

Planned work beyond the 0.1.0 release. Items here are directions, not commitments; ordering reflects current priority.

Guiding rule for every future feature: it must keep the Computase distinctive value — verified computation with independent test vectors, explicit coordinate contracts, honest truncation metadata, and provenance fields. No thin BioPython wrappers without that added layer.

## 0.2.0 — high-frequency lab tools

- Primer/oligo analysis: melting temperature (published Tm methods via `Bio.SeqUtils.MeltingTemp`), GC clamp, self-complementarity checks
- Restriction digestion via `Bio.Restriction`: cut sites, fragment sizes, unique cutters, using the same coordinate contract
- Protein sequence properties via `Bio.SeqUtils.ProtParam`: molecular weight, isoelectric point, extinction coefficient, instability index (pairs with `translate_sequence`)
- Codon-usage tables and CAI from coding sequences
- Human CLI subcommands (`computase revcomp ...`, JSON output) alongside the MCP server

## 0.3.0 — alignment and files

- Pairwise alignment via `Bio.Align.PairwiseAligner` (global/local, selectable scoring); large enough to anchor its own release
- GenBank/FASTA/FASTQ record parsing via `Bio.SeqIO`: record summaries, feature/CDS extraction by coordinate
- Multi-record FASTA input with per-record results
- Open question (decide at the time): NCBI Entrez fetch by accession — enables end-to-end agent workflows but breaks the "verified local computation" positioning; if added, ship as a clearly separated non-idempotent network tool

## Web app — flagship phase

- Preferred approach: fully client-side via Pyodide/WASM — no server, no hosting cost, no data leaves the user's machine, which extends the local-computation story
- Sequence visualizations: linear feature maps, ORF/motif tracks, GC-skew plots, circular plasmid-style SVG maps
- Fallback approach if Pyodide proves impractical: FastAPI over the same core plus a React frontend

## Community and credibility

- Benchmark write-up: LLM accuracy on sequence tasks with vs. without Computase MCP tools, published as a blog post or repo page
- Zenodo DOI archiving, then a JOSS submission once the API is stable
- Conda-forge packaging once PyPI distribution is stable

## Non-goals

- Phylogenetics, BLAST wrappers, protein structure analysis, NGS pipelines — heavy dependencies, external binaries, or long-running jobs that do not fit the fast, verified, local, agent-callable shape
