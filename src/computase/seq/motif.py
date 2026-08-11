"""Bounded IUPAC motif scanning on one or both strands."""

from typing import Literal

from computase.core.validation import (
    MAX_MOTIF_MATCHES,
    MAX_MOTIF_PATTERN_LENGTH,
    normalize_sequence,
)
from computase.errors import InvalidParameterError, InvalidSequenceError

from .models import MotifMatch, MotifScanResult

StrandPolicy = Literal["forward", "reverse", "both"]
_STRANDS = frozenset({"forward", "reverse", "both"})
_IUPAC_EXPANSION: dict[str, frozenset[str]] = {
    "A": frozenset("A"),
    "C": frozenset("C"),
    "G": frozenset("G"),
    "T": frozenset("TU"),
    "U": frozenset("TU"),
    "R": frozenset("AG"),
    "Y": frozenset("CTU"),
    "S": frozenset("GC"),
    "W": frozenset("ATU"),
    "K": frozenset("GTU"),
    "M": frozenset("AC"),
    "B": frozenset("CGTU"),
    "D": frozenset("AGTU"),
    "H": frozenset("ACTU"),
    "V": frozenset("ACG"),
    "N": frozenset("ACGTU"),
}
_COMPLEMENT = {
    "A": "T",
    "C": "G",
    "G": "C",
    "T": "A",
    "U": "A",
    "R": "Y",
    "Y": "R",
    "S": "S",
    "W": "W",
    "K": "M",
    "M": "K",
    "B": "V",
    "D": "H",
    "H": "D",
    "V": "B",
    "N": "N",
}


def _normalize_motif(motif: str) -> str:
    normalized = motif.strip().upper()
    if not normalized:
        raise InvalidSequenceError("motif is empty; provide at least one IUPAC nucleotide")
    if len(normalized) > MAX_MOTIF_PATTERN_LENGTH:
        raise InvalidSequenceError(
            f"motif length is {len(normalized)}; maximum is {MAX_MOTIF_PATTERN_LENGTH} characters"
        )
    for position, code in enumerate(normalized, start=1):
        if code not in _IUPAC_EXPANSION:
            raise InvalidSequenceError(
                f"invalid IUPAC character {code!r} at motif position {position}; "
                "use A,C,G,T,U,R,Y,S,W,K,M,B,D,H,V,N"
            )
    return normalized


def _reverse_complement_pattern(motif: str) -> str:
    return "".join(_COMPLEMENT[code] for code in reversed(motif))


def _find_intervals(
    sequence: str,
    motif: str,
    overlapping: bool,
    retain: int,
) -> tuple[int, list[tuple[int, int]]]:
    pattern = [_IUPAC_EXPANSION[code] for code in motif]
    pattern_length = len(pattern)
    intervals: list[tuple[int, int]] = []
    total = 0
    position = 0
    while position + pattern_length <= len(sequence):
        if all(sequence[position + offset] in allowed for offset, allowed in enumerate(pattern)):
            total += 1
            if len(intervals) < retain:
                intervals.append((position, position + pattern_length))
            position += 1 if overlapping else pattern_length
        else:
            position += 1
    return total, intervals


def scan_motif(
    sequence: str,
    motif: str,
    strand: StrandPolicy = "forward",
    overlapping: bool = True,
    max_matches: int = 10_000,
) -> MotifScanResult:
    """Scan a nucleotide sequence for an IUPAC motif.

    Args:
        sequence: Raw or single-record FASTA DNA/RNA input.
        motif: IUPAC nucleotide pattern of at most 500 characters.
        strand: Scan the forward, reverse, or both motif orientations.
        overlapping: Report overlapping sites when true.
        max_matches: Maximum returned sites (1 to 100,000).

    Returns:
        Coordinate-ordered matches using 0-based, end-exclusive coordinates
        on the forward reference, plus truthful total and truncation metadata.

    Raises:
        InvalidSequenceError: If the sequence or motif is malformed or over cap.
        InvalidParameterError: If a strand policy or result limit is invalid.

    Example:
        ``scan_motif("AAGA", "AAR").matches[0].start`` returns ``0``.
    """
    if strand not in _STRANDS:
        raise InvalidParameterError("strand must be 'forward', 'reverse', or 'both'")
    if not isinstance(overlapping, bool):
        raise InvalidParameterError("overlapping must be true or false")
    if (
        not isinstance(max_matches, int)
        or isinstance(max_matches, bool)
        or not 1 <= max_matches <= MAX_MOTIF_MATCHES
    ):
        raise InvalidParameterError(
            f"max_matches must be between 1 and {MAX_MOTIF_MATCHES:,}; got {max_matches!r}"
        )

    normalized_sequence = normalize_sequence(sequence).sequence
    normalized_motif = _normalize_motif(motif)
    reverse_motif = _reverse_complement_pattern(normalized_motif)
    palindromic = normalized_motif.replace("U", "T") == reverse_motif.replace("U", "T")

    oriented_matches: list[tuple[int, int, Literal["+", "-", "both"]]] = []
    total_found = 0
    if strand in {"forward", "both"}:
        total, intervals = _find_intervals(
            normalized_sequence,
            normalized_motif,
            overlapping,
            max_matches,
        )
        total_found += total
        label: Literal["+", "-", "both"] = "both" if strand == "both" and palindromic else "+"
        oriented_matches.extend((start, end, label) for start, end in intervals)

    if strand == "reverse" or (strand == "both" and not palindromic):
        total, intervals = _find_intervals(
            normalized_sequence,
            reverse_motif,
            overlapping,
            max_matches,
        )
        total_found += total
        oriented_matches.extend((start, end, "-") for start, end in intervals)

    oriented_matches.sort(key=lambda match: (match[0], match[1], match[2]))
    retained = oriented_matches[:max_matches]
    matches = [
        MotifMatch(
            start=start,
            end=end,
            strand=match_strand,
            matched_sequence=normalized_sequence[start:end],
            parameters={},
        )
        for start, end, match_strand in retained
    ]
    parameters = {
        "motif": normalized_motif,
        "strand": strand,
        "overlapping": overlapping,
        "max_matches": max_matches,
    }
    return MotifScanResult(
        motif=normalized_motif,
        strand=strand,
        matches=matches,
        total_found=total_found,
        truncated=total_found > max_matches,
        parameters=parameters,
    )
