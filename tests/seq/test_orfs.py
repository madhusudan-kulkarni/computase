import pytest

import computase.seq.orfs as orf_module
from computase.errors import InvalidParameterError
from computase.seq import enumerate_orfs, reverse_complement


@pytest.mark.parametrize("frame", [1, 2, 3])  # type: ignore[untyped-decorator]
@pytest.mark.parametrize("strand", ["+", "-"])  # type: ignore[untyped-decorator]
def test_enumerates_all_six_frames(frame: int, strand: str) -> None:
    oriented = "A" * (frame - 1) + "ATGAAATAA"
    sequence = oriented if strand == "+" else reverse_complement(oriented).reverse_complement

    result = enumerate_orfs(sequence, min_length_nt=3)

    assert len(result.orfs) == 1
    assert result.orfs[0].strand == strand
    assert result.orfs[0].frame == frame
    assert result.orfs[0].protein == "MK"
    assert result.orfs[0].complete is True
    expected_coordinates = (frame - 1, frame + 8) if strand == "+" else (0, 9)
    assert (result.orfs[0].start, result.orfs[0].end) == expected_coordinates
    expected_span = oriented[frame - 1 : frame + 8]
    if strand == "-":
        expected_span = reverse_complement(expected_span).reverse_complement
    assert sequence[result.orfs[0].start : result.orfs[0].end] == expected_span
    assert result.coordinate_system == "0-based-half-open"


def test_nested_starts_are_optional() -> None:
    outer_only = enumerate_orfs("ATGATGAAATAA", min_length_nt=3)
    nested = enumerate_orfs("ATGATGAAATAA", include_nested=True, min_length_nt=3)

    assert [(orf.start, orf.end) for orf in outer_only.orfs] == [(0, 12)]
    assert [(orf.start, orf.end) for orf in nested.orfs] == [(0, 12), (3, 12)]


def test_orf_fasta_matches_raw_input() -> None:
    raw = enumerate_orfs("ATGAAATAA", min_length_nt=3)
    assert enumerate_orfs(">record\nATG AAA TAA\n", min_length_nt=3) == raw


def test_open_ended_orf_policy() -> None:
    complete_only = enumerate_orfs("ATGAAA", min_length_nt=3)
    open_ended = enumerate_orfs("ATGAAA", require_stop=False, min_length_nt=3)

    assert complete_only.orfs == []
    assert len(open_ended.orfs) == 1
    assert open_ended.orfs[0].complete is False
    assert open_ended.orfs[0].protein == "MK"


def test_table_start_policy() -> None:
    table_starts = enumerate_orfs("GTGAAATAA", table_id=11, min_length_nt=3)
    atg_only = enumerate_orfs(
        "GTGAAATAA",
        table_id=11,
        start_codons="atg-only",
        min_length_nt=3,
    )

    assert len(table_starts.orfs) == 1
    assert atg_only.orfs == []


def test_truthful_truncation_and_ordering() -> None:
    result = enumerate_orfs(
        "ATGAAATAAATGAAAAAATAA",
        min_length_nt=3,
        max_results=1,
    )

    assert result.total_found == 2
    assert result.truncated is True
    assert len(result.orfs) == 1
    assert result.orfs[0].start == 0


def test_truthful_truncation_when_protein_output_budget_is_reached(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(orf_module, "MAX_ORF_PROTEIN_RESIDUES", 2)

    result = enumerate_orfs(
        "ATGAAATAAATGAAATAA",
        min_length_nt=3,
        max_results=10,
    )

    assert result.total_found == 2
    assert result.truncated is True
    assert len(result.orfs) == 1
    assert result.orfs[0].protein == "MK"


def test_orf_result_records_effective_parameters_without_input() -> None:
    result = enumerate_orfs("ATGAAATAA", min_length_nt=3)

    assert result.parameters == {
        "table_id": 1,
        "start_codons": "table-starts",
        "include_nested": False,
        "require_stop": True,
        "min_length_nt": 3,
        "max_results": 1000,
    }
    assert "sequence" not in result.model_dump()
    assert "not gene predictions" in result.note


@pytest.mark.parametrize("max_results", [0, 10_001])  # type: ignore[untyped-decorator]
def test_rejects_invalid_result_limits(max_results: int) -> None:
    with pytest.raises(InvalidParameterError, match="max_results"):
        enumerate_orfs("ATGAAATAA", max_results=max_results)
