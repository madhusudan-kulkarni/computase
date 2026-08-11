# Computase usage examples

## Python

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

## MCP arguments

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
