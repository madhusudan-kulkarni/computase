import pytest
from hypothesis import given
from hypothesis import strategies as st

from computase.seq import summarize_sequence

from .fixtures import HBB_CDS


def test_summary_reports_composition_uncertainty_and_no_input_echo() -> None:
    result = summarize_sequence("AAGCSWN")

    assert result.sequence_type == "dna"
    assert result.length == 7
    assert result.composition == {"A": 2, "G": 1, "C": 1, "S": 1, "W": 1, "N": 1}
    assert result.dinucleotides == {"AA": 1, "AG": 1, "GC": 1, "CS": 1, "SW": 1, "WN": 1}
    assert result.gc_percent == pytest.approx(50.0)
    assert result.gc_min_percent == pytest.approx(3 / 7 * 100)
    assert result.gc_max_percent == pytest.approx(4 / 7 * 100)
    assert result.ambiguous_count == 3
    assert result.gc_skew == pytest.approx(0.0)
    assert result.parameters == {}
    assert "sequence" not in result.model_dump()


def test_summary_returns_null_skew_without_concrete_gc() -> None:
    assert summarize_sequence("AAWW").gc_skew is None


def test_summary_accepts_single_record_fasta_rna() -> None:
    result = summarize_sequence(">rna\nAUGC\n")

    assert result.sequence_type == "rna"
    assert result.length == 4
    assert result.gc_percent == pytest.approx(50.0)


def test_summary_matches_hbb_genbank_reference() -> None:
    result = summarize_sequence(HBB_CDS)

    assert result.length == 444
    assert result.composition == {"A": 88, "C": 113, "G": 136, "T": 107}
    assert result.gc_percent == pytest.approx(56.0811, abs=1e-4)
    assert result.gc_skew == pytest.approx(0.092369, abs=1e-6)


@given(st.text(alphabet="ACGT", min_size=1, max_size=100))  # type: ignore[untyped-decorator]
def test_summary_invariants(sequence: str) -> None:
    result = summarize_sequence(sequence)

    assert sum(result.composition.values()) == result.length
    assert result.gc_min_percent <= result.gc_percent <= result.gc_max_percent
    assert summarize_sequence(f">record\n{sequence}\n") == result
