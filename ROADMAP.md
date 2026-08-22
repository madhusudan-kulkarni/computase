# Computase roadmap

Planned work beyond the 0.1.x series. Items here are directions, not commitments. Ordering reflects current priority.

Every future feature must keep what makes Computase useful: verified computation with independent test vectors, explicit coordinate contracts, truthful truncation metadata, and provenance fields. No thin Biopython wrappers without that layer.

## 0.2.0: Common lab tools

- Primer and oligo analysis: melting temperature with published Tm methods from `Bio.SeqUtils.MeltingTemp`, GC clamp, self-complementarity checks
- Restriction digestion via `Bio.Restriction`: cut sites, fragment sizes, and unique cutters, using the forward-reference coordinate contract
- Protein sequence properties via `Bio.SeqUtils.ProtParam`: molecular weight, isoelectric point, extinction coefficient, instability index
- Codon-usage tables and CAI from coding sequences
- Human CLI subcommands (`computase revcomp ...`, JSON output) alongside the MCP server

## 0.3.0: Alignment and file parsing

- Pairwise alignment via `Bio.Align.PairwiseAligner` with global or local modes and selectable scoring
- GenBank, FASTA, and FASTQ parsing via `Bio.SeqIO`: record summaries, feature and CDS extraction by coordinate
- Multi-record FASTA input with per-record results
- Open question: NCBI Entrez fetching by accession. This enables agent workflows but requires network calls. If added, ship it as a distinct network tool with explicit timeouts.

## Web app: Client-side tool

- Preferred approach: run client-side in the browser with Pyodide and WebAssembly. No server, no hosting cost, and no sequence data leaves the machine.
- Visualizations: linear feature maps, ORF and motif tracks, GC skew plots, circular plasmid SVG maps
- Fallback approach: FastAPI backend with a React interface if WebAssembly bundles prove too large

## Community

- Benchmark report: LLM accuracy on sequence tasks with and without Computase MCP tools
- Zenodo DOI archiving and a JOSS submission once the API stabilizes
- Conda-forge package distribution

## Non-goals

- Phylogenetics, BLAST wrappers, protein structure prediction, and NGS pipelines. These require heavy dependencies, external binaries, or long-running jobs that do not fit a fast, verified local library.

