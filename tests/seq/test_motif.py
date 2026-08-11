import pytest
from hypothesis import given
from hypothesis import strategies as st

from computase.errors import InvalidParameterError, InvalidSequenceError
from computase.seq import scan_motif

from .fixtures import PUC19_MCS


def test_forward_palindromic_site_matches_puc19_reference() -> None:
    result = scan_motif(PUC19_MCS, "GAATTC")

    assert [(match.start, match.end, match.strand) for match in result.matches] == [(68, 74, "+")]
    assert result.matches[0].matched_sequence == "GAATTC"


def test_reverse_strand_coordinates_use_forward_reference() -> None:
    result = scan_motif("AAAGCATCCC", "ATGC", strand="reverse")

    assert [(match.start, match.end, match.strand) for match in result.matches] == [(3, 7, "-")]
    assert result.matches[0].matched_sequence == "GCAT"


def test_both_strands_deduplicate_palindromic_sites() -> None:
    result = scan_motif(PUC19_MCS, "GAATTC", strand="both")

    assert [(match.start, match.end, match.strand) for match in result.matches] == [
        (68, 74, "both")
    ]


def test_iupac_pattern_and_overlap_policies() -> None:
    assert [match.start for match in scan_motif("AAAA", "AAR").matches] == [0, 1]
    assert [match.start for match in scan_motif("AAAA", "AAA", overlapping=False).matches] == [0]


def test_truthful_match_limit() -> None:
    result = scan_motif("AAAA", "A", max_matches=2)

    assert result.total_found == 4
    assert result.truncated is True
    assert len(result.matches) == 2


def test_motif_result_records_parameters_without_input() -> None:
    result = scan_motif(">record\nATGC\n", "ATG")

    assert result.parameters == {
        "motif": "ATG",
        "strand": "forward",
        "overlapping": True,
        "max_matches": 10_000,
    }
    assert result.coordinate_system == "0-based-half-open"
    assert "sequence" not in result.model_dump()


def test_rejects_invalid_pattern_and_limits() -> None:
    with pytest.raises(InvalidSequenceError, match="motif"):
        scan_motif("ATGC", "X")
    with pytest.raises(InvalidSequenceError, match="500"):
        scan_motif("ATGC", "A" * 501)
    with pytest.raises(InvalidParameterError, match="max_matches"):
        scan_motif("ATGC", "A", max_matches=100_001)


@given(st.text(alphabet="ACGT", min_size=1, max_size=100))  # type: ignore[untyped-decorator]
def test_reported_intervals_round_trip(sequence: str) -> None:
    result = scan_motif(sequence, "N", max_matches=100)

    assert all(
        0 <= match.start < match.end <= len(sequence)
        and sequence[match.start : match.end] == match.matched_sequence
        for match in result.matches
    )
