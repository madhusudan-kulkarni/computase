"""Nucleotide composition and uncertainty-preserving GC summaries."""

from collections import Counter
from itertools import pairwise

from computase.core.validation import normalize_sequence

from .models import SequenceSummary

_DEFINITE_GC = frozenset("GCS")
_DEFINITE_AT = frozenset("ATUW")
_POSSIBLE_GC = frozenset("GCSRYKMBDHVN")


def summarize_sequence(sequence: str) -> SequenceSummary:
    """Summarize a raw or single-record FASTA nucleotide sequence.

    Args:
        sequence: DNA or RNA in raw or single-record FASTA form. Whitespace
            and a leading FASTA header are ignored; IUPAC codes are accepted.

    Returns:
        Composition, overlapping dinucleotides, concrete GC skew, and
        uncertainty-preserving GC bounds. Coordinates are not applicable.

    Raises:
        InvalidSequenceError: If the input is empty, malformed, mixed DNA/RNA,
            or longer than 5,000,000 nucleotides.

    Example:
        ``summarize_sequence("AAGC").gc_percent`` returns ``50.0``.
    """
    normalized = normalize_sequence(sequence)
    residues = normalized.sequence
    composition = dict(Counter(residues))
    dinucleotides = dict(Counter(map("".join, pairwise(residues))))

    determinate_count = sum(composition.get(code, 0) for code in _DEFINITE_GC | _DEFINITE_AT)
    definite_gc_count = sum(composition.get(code, 0) for code in _DEFINITE_GC)
    gc_percent = 100.0 * definite_gc_count / determinate_count if determinate_count else 0.0

    possible_gc_count = sum(composition.get(code, 0) for code in _POSSIBLE_GC)
    length = len(residues)
    gc_min_percent = 100.0 * definite_gc_count / length
    gc_max_percent = 100.0 * possible_gc_count / length

    concrete = frozenset("ACGU" if normalized.sequence_type == "rna" else "ACGT")
    ambiguous_count = sum(count for code, count in composition.items() if code not in concrete)
    g_count = composition.get("G", 0)
    c_count = composition.get("C", 0)
    gc_skew = (g_count - c_count) / (g_count + c_count) if g_count + c_count else None

    return SequenceSummary(
        sequence_type=normalized.sequence_type,
        length=length,
        composition=composition,
        dinucleotides=dinucleotides,
        gc_percent=gc_percent,
        gc_min_percent=gc_min_percent,
        gc_max_percent=gc_max_percent,
        ambiguous_count=ambiguous_count,
        gc_skew=gc_skew,
        parameters={},
    )
