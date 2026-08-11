import pytest

from computase.core.validation import MAX_SEQUENCE_LENGTH, normalize_sequence
from computase.errors import InvalidSequenceError


def test_normalize_raw_dna() -> None:
    normalized = normalize_sequence(" acg t\nnr ")

    assert normalized.sequence == "ACGTNR"
    assert normalized.sequence_type == "dna"


def test_normalize_single_record_fasta_rna() -> None:
    normalized = normalize_sequence(">example sequence\naug c\nn\n")

    assert normalized.sequence == "AUGCN"
    assert normalized.sequence_type == "rna"


def test_reject_multi_record_fasta() -> None:
    with pytest.raises(InvalidSequenceError, match="one record at a time"):
        normalize_sequence(">first\nACGT\n>second\nTGCA")


def test_reject_empty_sequence() -> None:
    with pytest.raises(InvalidSequenceError, match="empty"):
        normalize_sequence(" \n\t")


def test_reject_invalid_iupac_character_with_position() -> None:
    with pytest.raises(InvalidSequenceError, match=r"'X'.*position 3"):
        normalize_sequence("ACXG")


def test_reject_mixed_dna_and_rna_alphabets() -> None:
    with pytest.raises(InvalidSequenceError, match=r"both T and U"):
        normalize_sequence("ACTUG")


def test_reject_sequence_over_cap() -> None:
    with pytest.raises(InvalidSequenceError, match=f"maximum is {MAX_SEQUENCE_LENGTH:,}"):
        normalize_sequence("A" * (MAX_SEQUENCE_LENGTH + 1))
