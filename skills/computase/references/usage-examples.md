# Computase usage examples

## MCP first

When the Computase MCP server is configured, call the matching tool directly:

### `computase_summarize_sequence`

```json
{"sequence": ">record\nAAGCSWN\n"}
```

### `computase_reverse_complement`

```json
{"sequence": "AUGC"}
```

### `computase_translate_sequence`

```json
{"sequence": "ATGGCC", "table_id": 1, "stop_handling": "translate-through"}
```

### `computase_enumerate_orfs`

```json
{
  "sequence": "ATGATGAAATAA",
  "table_id": 1,
  "start_codons": "table-starts",
  "include_nested": true,
  "require_stop": true,
  "min_length_nt": 3,
  "max_results": 1000
}
```

### `computase_scan_motif`

```json
{
  "sequence": "TTGAATTCAA",
  "motif": "GAATTC",
  "strand": "both",
  "overlapping": true,
  "max_matches": 10000
}
```

The palindromic EcoRI site above is returned once with `strand: "both"`.

## Isolated runner fallback

If MCP tools are unavailable and `uv` is installed, run the bundled script from the Skill directory. Do not install Computase into the active project:

```bash
uv run --script skills/computase/scripts/run.py <<'EOF'
{"operation":"reverse_complement","arguments":{"sequence":"AUGC"}}
EOF
```

Successful responses use this envelope:

```json
{
  "ok": true,
  "operation": "reverse_complement",
  "result": {
    "computase_version": "0.1.1",
    "parameters": {},
    "sequence_type": "rna",
    "length": 4,
    "reverse_complement": "GCAU"
  }
}
```

Allowed `operation` values are `summarize_sequence`, `reverse_complement`, `translate_sequence`, `enumerate_orfs`, and `scan_motif`.

## Python API

```python
from computase.seq import (
    enumerate_orfs,
    reverse_complement,
    scan_motif,
    summarize_sequence,
    translate_sequence,
)

summarize_sequence(">record\nAAGCSWN\n")
reverse_complement("AUGC")
translate_sequence("ATGGCC", table_id=1)
enumerate_orfs("ATGAAATAA", min_length_nt=3)
scan_motif("TTGAATTCAA", "GAATTC", strand="both")
```

## Presentation patterns

### Scalar result

For reverse complement or translation, lead with the computed string, then state alphabet or genetic-code table, stop policy when relevant, and Computase version. Offer raw JSON only if requested.

Example summary:

> Reverse complement: `GCAU` (RNA, length 4). Computase 0.1.1.

### Coordinate list

For ORFs or motifs, summarize counts first, then show a compact table or bullets of coordinates. Preserve 0-based end-exclusive spans and strand. If `truncated` is true, say how many were returned versus `total_found`.

Example summary:

> Found 1 complete candidate ORF (not a gene prediction): `[3, 12)` on `+` frame 1, protein `MK`. Results are complete (`truncated=false`). Computase 0.1.1.

### Ambiguous composition

For summaries with IUPAC ambiguity, report GC bounds rather than inventing probabilities:

> Length 6, composition includes ambiguous `R` and `N`. GC bounds 33.33–66.67%. Computase 0.1.1.
