"""DNA and RNA reverse complements."""

from Bio.Seq import Seq

from computase.core.validation import normalize_sequence

from .models import ReverseComplementResult


def reverse_complement(sequence: str) -> ReverseComplementResult:
    """Return the reverse complement of raw or single-record FASTA input.

    Args:
        sequence: DNA or RNA input using the IUPAC nucleotide alphabet.

    Returns:
        The reverse complement in the same alphabet, its length, detected
        sequence type, and provenance. Coordinates are not applicable.

    Raises:
        InvalidSequenceError: If the input is empty, malformed, mixed DNA/RNA,
            or longer than 5,000,000 nucleotides.

    Example:
        ``reverse_complement("ATGC").reverse_complement`` returns ``"GCAT"``.
    """
    normalized = normalize_sequence(sequence)
    value = Seq(normalized.sequence)
    result = (
        str(value.reverse_complement_rna())
        if normalized.sequence_type == "rna"
        else str(value.reverse_complement())
    )
    return ReverseComplementResult(
        sequence_type=normalized.sequence_type,
        length=len(normalized.sequence),
        reverse_complement=result,
        parameters={},
    )
