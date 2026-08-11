"""Translation with selectable NCBI genetic codes."""

from typing import Literal

from Bio.Data import CodonTable
from Bio.Seq import Seq

from computase.core.validation import normalize_sequence
from computase.errors import InvalidParameterError, InvalidSequenceError

from .models import TranslationResult

StopHandling = Literal["translate-through", "truncate-at-first-stop"]
_STOP_POLICIES = frozenset({"translate-through", "truncate-at-first-stop"})


def translate_sequence(
    sequence: str,
    table_id: int = 1,
    stop_handling: StopHandling = "translate-through",
) -> TranslationResult:
    """Translate raw or single-record FASTA nucleotide input.

    Args:
        sequence: DNA or RNA input containing complete codons.
        table_id: NCBI genetic-code table identifier. Defaults to ``1``.
        stop_handling: ``"translate-through"`` retains ``*`` stop markers;
            ``"truncate-at-first-stop"`` returns only the preceding protein.

    Returns:
        Protein, selected table metadata, codon count, stop behavior, and
        provenance. Coordinates are not applicable.

    Raises:
        InvalidSequenceError: If sequence validation fails or the normalized
            length is not divisible by three.
        InvalidParameterError: If ``table_id`` or ``stop_handling`` is invalid.

    Example:
        ``translate_sequence("ATGGCC").protein`` returns ``"MA"``.
    """
    if not isinstance(table_id, int) or isinstance(table_id, bool):
        raise InvalidParameterError("table_id must be an integer NCBI genetic-code identifier")
    try:
        table = CodonTable.generic_by_id[table_id]
    except KeyError:
        valid = ", ".join(str(value) for value in sorted(CodonTable.generic_by_id))
        raise InvalidParameterError(
            f"unknown table_id {table_id}; choose a supported NCBI table: {valid}"
        ) from None
    if stop_handling not in _STOP_POLICIES:
        raise InvalidParameterError(
            "stop_handling must be 'translate-through' or 'truncate-at-first-stop'"
        )

    normalized = normalize_sequence(sequence)
    if len(normalized.sequence) % 3:
        raise InvalidSequenceError(
            f"sequence length is {len(normalized.sequence)}; translation requires complete "
            "codons, so the length must be divisible by 3"
        )

    translated = str(Seq(normalized.sequence).translate(table=table_id))
    stopped_early = stop_handling == "truncate-at-first-stop" and "*" in translated
    protein = translated.split("*", maxsplit=1)[0] if stopped_early else translated
    return TranslationResult(
        protein=protein,
        table_id=table_id,
        table_name=table.names[0],
        stop_handling=stop_handling,
        codon_count=len(normalized.sequence) // 3,
        stopped_early=stopped_early,
        parameters={"table_id": table_id, "stop_handling": stop_handling},
    )
