import pytest
from hypothesis import given
from hypothesis import strategies as st

from computase.errors import InvalidSequenceError
from computase.seq import reverse_complement

from .fixtures import M13_FORWARD, M13_REVERSE_COMPLEMENT


def test_reverse_complement_matches_m13_reference() -> None:
    result = reverse_complement(M13_FORWARD)

    assert result.sequence_type == "dna"
    assert result.length == len(M13_FORWARD)
    assert result.reverse_complement == M13_REVERSE_COMPLEMENT
    assert result.parameters == {}


def test_reverse_complement_preserves_rna_alphabet_and_iupac_codes() -> None:
    result = reverse_complement(">rna\nAUGCRY\n")

    assert result.sequence_type == "rna"
    assert result.reverse_complement == "RYGCAU"


def test_reverse_complement_fasta_matches_raw_input() -> None:
    assert reverse_complement(">record\nATG C\n") == reverse_complement("ATGC")


def test_reverse_complement_rejects_mixed_t_and_u() -> None:
    with pytest.raises(InvalidSequenceError, match="both T and U"):
        reverse_complement("AUTG")


@given(  # type: ignore[untyped-decorator]
    st.text(alphabet="ACGTRYSWKMBDHVN", min_size=1, max_size=100)
)
def test_reverse_complement_is_an_involution(sequence: str) -> None:
    restored = reverse_complement(reverse_complement(sequence).reverse_complement)

    assert restored.reverse_complement == sequence
