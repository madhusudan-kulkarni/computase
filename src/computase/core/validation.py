"""Nucleotide input normalization and shared limits."""

from dataclasses import dataclass
from typing import Literal

from computase.errors import InvalidSequenceError

MAX_SEQUENCE_LENGTH = 5_000_000
MAX_MOTIF_PATTERN_LENGTH = 500
MAX_ORF_RESULTS = 10_000
MAX_ORF_PROTEIN_RESIDUES = 5_000_000
MAX_MOTIF_MATCHES = 100_000

IUPAC_DNA = frozenset("ACGTRYSWKMBDHVN")
IUPAC_RNA = frozenset("ACGURYSWKMBDHVN")


@dataclass(frozen=True, slots=True)
class NormalizedSequence:
    """A validated sequence and its inferred nucleotide alphabet."""

    sequence: str
    sequence_type: Literal["dna", "rna"]


def _strip_fasta(sequence: str, max_length: int) -> str:
    text = sequence.strip()
    if not text:
        raise InvalidSequenceError("sequence is empty; provide at least one nucleotide")

    payload = text
    if text.startswith(">"):
        lines = text.splitlines()
        if any(line.lstrip().startswith(">") for line in lines[1:]):
            raise InvalidSequenceError(
                "sequence contains multiple FASTA records; submit one record at a time"
            )
        payload = "\n".join(lines[1:])

    residues: list[str] = []
    for character in payload:
        if character.isspace():
            continue
        residues.append(character)
        if len(residues) > max_length:
            raise InvalidSequenceError(
                f"sequence length exceeds {max_length:,} nucleotides; maximum is {max_length:,}"
            )
    return "".join(residues)


def normalize_sequence(
    sequence: str,
    *,
    max_length: int = MAX_SEQUENCE_LENGTH,
) -> NormalizedSequence:
    """Normalize raw or single-record FASTA nucleotide input.

    Whitespace and one leading FASTA header are removed, lowercase letters are
    uppercased, and the sequence is validated against the DNA or RNA IUPAC
    alphabet. Inputs longer than ``max_length`` and mixed T/U alphabets are
    rejected.
    """
    normalized = _strip_fasta(sequence, max_length).upper()
    if not normalized:
        raise InvalidSequenceError(
            "sequence is empty after removing the FASTA header and whitespace; "
            "provide at least one nucleotide"
        )
    if "T" in normalized and "U" in normalized:
        raise InvalidSequenceError(
            "sequence contains both T and U; provide one DNA or RNA alphabet, not a mixture"
        )

    sequence_type: Literal["dna", "rna"] = "rna" if "U" in normalized else "dna"
    alphabet = IUPAC_RNA if sequence_type == "rna" else IUPAC_DNA
    for position, residue in enumerate(normalized, start=1):
        if residue not in alphabet:
            valid = "".join(sorted(alphabet))
            raise InvalidSequenceError(
                f"invalid IUPAC character {residue!r} at position {position}; "
                f"valid {sequence_type.upper()} characters are {valid}"
            )

    return NormalizedSequence(normalized, sequence_type)
