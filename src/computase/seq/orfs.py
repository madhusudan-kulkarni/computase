"""Six-frame candidate open reading frame enumeration."""

from typing import Literal

from Bio.Data import CodonTable
from Bio.Seq import Seq

from computase.core.validation import MAX_ORF_RESULTS, normalize_sequence
from computase.errors import InvalidParameterError

from .models import Orf, OrfEnumeration

StartCodonPolicy = Literal["table-starts", "atg-only"]
_START_POLICIES = frozenset({"table-starts", "atg-only"})


def _validate_parameters(
    table_id: int,
    start_codons: str,
    include_nested: bool,
    require_stop: bool,
    min_length_nt: int,
    max_results: int,
) -> CodonTable.CodonTable:
    if not isinstance(table_id, int) or isinstance(table_id, bool):
        raise InvalidParameterError("table_id must be an integer NCBI genetic-code identifier")
    try:
        table = CodonTable.unambiguous_dna_by_id[table_id]
    except KeyError:
        raise InvalidParameterError(
            f"unknown table_id {table_id}; choose a supported NCBI table"
        ) from None
    if start_codons not in _START_POLICIES:
        raise InvalidParameterError("start_codons must be 'table-starts' or 'atg-only'")
    if not isinstance(include_nested, bool):
        raise InvalidParameterError("include_nested must be true or false")
    if not isinstance(require_stop, bool):
        raise InvalidParameterError("require_stop must be true or false")
    if not isinstance(min_length_nt, int) or isinstance(min_length_nt, bool) or min_length_nt < 1:
        raise InvalidParameterError("min_length_nt must be an integer of at least 1")
    if (
        not isinstance(max_results, int)
        or isinstance(max_results, bool)
        or not 1 <= max_results <= MAX_ORF_RESULTS
    ):
        raise InvalidParameterError(
            f"max_results must be between 1 and {MAX_ORF_RESULTS:,}; got {max_results!r}"
        )
    return table


def _candidate(
    oriented: str,
    sequence_length: int,
    start: int,
    end: int,
    strand: Literal["+", "-"],
    frame: int,
    table_id: int,
    complete: bool,
) -> Orf:
    coding = oriented[start:end]
    if complete:
        protein = str(Seq(coding).translate(table=table_id, cds=True))
    else:
        protein = str(Seq(coding).translate(table=table_id))
        if protein:
            protein = "M" + protein[1:]
    forward_start, forward_end = (
        (start, end) if strand == "+" else (sequence_length - end, sequence_length - start)
    )
    return Orf(
        start=forward_start,
        end=forward_end,
        strand=strand,
        frame=frame,
        length_nt=end - start,
        protein=protein,
        complete=complete,
        parameters={},
    )


def enumerate_orfs(
    sequence: str,
    table_id: int = 1,
    start_codons: StartCodonPolicy = "table-starts",
    include_nested: bool = False,
    require_stop: bool = True,
    min_length_nt: int = 30,
    max_results: int = 1000,
) -> OrfEnumeration:
    """Enumerate candidate ORFs across all six DNA/RNA reading frames.

    Args:
        sequence: Raw or single-record FASTA nucleotide input.
        table_id: NCBI genetic-code table identifier. Defaults to ``1``.
        start_codons: Use all selected-table starts or restrict to ATG.
        include_nested: Include in-frame starts nested before the same stop.
        require_stop: Require a terminal in-frame stop when true.
        min_length_nt: Minimum nucleotide span, including a stop codon.
        max_results: Maximum returned candidates (1 to 10,000).

    Returns:
        Candidates ordered by forward start then longer first, with 0-based,
        end-exclusive forward-reference coordinates and truthful truncation.

    Raises:
        InvalidSequenceError: If sequence validation fails.
        InvalidParameterError: If a table, policy, or limit is invalid.

    Example:
        ``enumerate_orfs("ATGAAATAA", min_length_nt=3)`` returns one
        complete forward-strand candidate.
    """
    table = _validate_parameters(
        table_id,
        start_codons,
        include_nested,
        require_stop,
        min_length_nt,
        max_results,
    )
    normalized = normalize_sequence(sequence)
    forward = normalized.sequence.replace("U", "T")
    start_set = (
        frozenset(table.start_codons) if start_codons == "table-starts" else frozenset({"ATG"})
    )
    stop_set = frozenset(table.stop_codons)
    candidates: list[Orf] = []

    strands: tuple[tuple[Literal["+", "-"], str], ...] = (
        ("+", forward),
        ("-", str(Seq(forward).reverse_complement())),
    )
    for strand, oriented in strands:
        for offset in range(3):
            active_starts: list[int] = []
            final_codon_end = offset
            for position in range(offset, len(oriented) - 2, 3):
                final_codon_end = position + 3
                codon = oriented[position : position + 3]
                if codon in start_set and (include_nested or not active_starts):
                    active_starts.append(position)
                if codon in stop_set and active_starts:
                    for start in active_starts:
                        if position + 3 - start >= min_length_nt:
                            candidates.append(
                                _candidate(
                                    oriented,
                                    len(forward),
                                    start,
                                    position + 3,
                                    strand,
                                    offset + 1,
                                    table_id,
                                    True,
                                )
                            )
                    active_starts.clear()
            if not require_stop:
                for start in active_starts:
                    if final_codon_end - start >= min_length_nt:
                        candidates.append(
                            _candidate(
                                oriented,
                                len(forward),
                                start,
                                final_codon_end,
                                strand,
                                offset + 1,
                                table_id,
                                False,
                            )
                        )

    candidates.sort(key=lambda orf: (orf.start, -orf.length_nt))
    total_found = len(candidates)
    parameters = {
        "table_id": table_id,
        "start_codons": start_codons,
        "include_nested": include_nested,
        "require_stop": require_stop,
        "min_length_nt": min_length_nt,
        "max_results": max_results,
    }
    return OrfEnumeration(
        orfs=candidates[:max_results],
        total_found=total_found,
        truncated=total_found > max_results,
        parameters=parameters,
    )
