import pytest

from computase.errors import InvalidParameterError, InvalidSequenceError
from computase.seq import translate_sequence

from .fixtures import NCBI_TRANSLATION_PROTEIN, NCBI_TRANSLATION_SEQUENCE


def test_translate_through_matches_ncbi_reference() -> None:
    result = translate_sequence(NCBI_TRANSLATION_SEQUENCE)

    assert result.protein == NCBI_TRANSLATION_PROTEIN
    assert result.table_id == 1
    assert result.table_name == "Standard"
    assert result.stop_handling == "translate-through"
    assert result.codon_count == 13
    assert result.stopped_early is False
    assert result.parameters == {"table_id": 1, "stop_handling": "translate-through"}


def test_truncate_at_first_stop() -> None:
    result = translate_sequence(
        NCBI_TRANSLATION_SEQUENCE,
        stop_handling="truncate-at-first-stop",
    )

    assert result.protein == "MAIVMGR"
    assert result.stopped_early is True
    assert result.codon_count == 13


def test_translate_uses_selected_ncbi_table() -> None:
    standard = translate_sequence("ATGAGA", table_id=1)
    mitochondrial = translate_sequence("ATGAGA", table_id=2)

    assert standard.protein == "MR"
    assert mitochondrial.protein == "M*"
    assert mitochondrial.table_name == "Vertebrate Mitochondrial"


def test_translate_accepts_fasta_rna() -> None:
    assert translate_sequence(">rna\nAUGGCC\n").protein == "MA"


def test_translate_rejects_partial_codon() -> None:
    with pytest.raises(InvalidSequenceError, match="complete codons"):
        translate_sequence("ATGG")


def test_translate_rejects_unknown_table() -> None:
    with pytest.raises(InvalidParameterError, match="table_id"):
        translate_sequence("ATG", table_id=9999)


def test_translate_rejects_bad_stop_policy() -> None:
    with pytest.raises(InvalidParameterError, match="stop_handling"):
        translate_sequence("ATG", stop_handling="bad-policy")  # type: ignore[arg-type]
