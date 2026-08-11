"""Shared validation and result-model infrastructure."""

from .models import ProvenanceModel
from .validation import (
    MAX_MOTIF_MATCHES,
    MAX_MOTIF_PATTERN_LENGTH,
    MAX_ORF_RESULTS,
    MAX_SEQUENCE_LENGTH,
    NormalizedSequence,
    normalize_sequence,
)

__all__ = [
    "MAX_MOTIF_MATCHES",
    "MAX_MOTIF_PATTERN_LENGTH",
    "MAX_ORF_RESULTS",
    "MAX_SEQUENCE_LENGTH",
    "NormalizedSequence",
    "ProvenanceModel",
    "normalize_sequence",
]
