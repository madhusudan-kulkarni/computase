# Python examples

These examples use the public API in `computase.seq`. Inputs may be raw
nucleotide strings or a single FASTA record. Result objects are typed Pydantic
models and include the installed Computase version and effective parameters.

## Summarize a sequence

```python
from computase.seq import summarize_sequence

result = summarize_sequence("AAGCRN")

print(result.composition)
print(round(result.gc_min_percent, 2), round(result.gc_max_percent, 2))
print(result.ambiguous_count)
```

Output:

```text
{'A': 2, 'G': 1, 'C': 1, 'R': 1, 'N': 1}
33.33 66.67
2
```

`R` and `N` are retained as ambiguous IUPAC residues. The GC bounds show the
minimum and maximum possible GC content rather than assigning probabilities to
those residues.

## Reverse-complement RNA

```python
from computase.seq import reverse_complement

result = reverse_complement("AUGCRY")

print(result.reverse_complement)
print(result.sequence_type)
```

Output:

```text
RYGCAU
rna
```

The result preserves the RNA alphabet and complements ambiguous IUPAC symbols.

## Translate a coding sequence

```python
from computase.seq import translate_sequence

result = translate_sequence(
    "ATGGCCATTGTAATGGGCCGCTGAAAGGGTGCCCGATAG",
    table_id=1,
)

print(result.protein)
print(result.table_name)
```

Output:

```text
MAIVMGR*KGAR*
Standard
```

The input must contain complete codons. Use
`stop_handling="truncate-at-first-stop"` when translation should stop before
the first stop codon.

## Enumerate candidate ORFs

```python
from computase.seq import enumerate_orfs

result = enumerate_orfs("CCCATGAAATAAGGG", min_length_nt=9)
orf = result.orfs[0]

print(orf.start, orf.end, orf.strand, orf.frame)
print(orf.protein, orf.complete)
```

Output:

```text
3 12 + 1
MK True
```

Coordinates are 0-based and end-exclusive on the normalized forward
reference. These results are sequence candidates, not gene predictions.

## Scan for an IUPAC motif

```python
from computase.seq import scan_motif

result = scan_motif(
    "AAGAATTCTTCTT",
    "GAATTC",
    strand="both",
)
match = result.matches[0]

print(match.start, match.end, match.strand)
print(match.matched_sequence)
```

Output:

```text
2 8 both
GAATTC
```

This palindromic EcoRI site matches both orientations at the same coordinates,
so it is reported once with `strand="both"`.

## Handling invalid input

Invalid sequences and parameters raise explicit Computase exceptions:

```python
from computase.errors import InvalidSequenceError
from computase.seq import translate_sequence

try:
    translate_sequence("ATGG")
except InvalidSequenceError as error:
    print(error)
```

Do not include sensitive sequence data in public issue reports. If a result
differs from an independent reference, submit a minimized example through the
[scientific correctness form](https://github.com/madhusudan-kulkarni/computase/issues/new?template=scientific-correctness.yml).
