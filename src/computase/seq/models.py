"""Structured result models for sequence operations."""

from typing import Literal

from pydantic import Field

from computase.core.models import ProvenanceModel


class SequenceSummary(ProvenanceModel):
    """Composition and GC metrics for a nucleotide sequence."""

    sequence_type: Literal["dna", "rna"] = Field(description="Detected nucleotide alphabet.")
    length: int = Field(ge=1, description="Normalized sequence length.")
    composition: dict[str, int] = Field(description="Counts for every residue present.")
    dinucleotides: dict[str, int] = Field(
        description="Counts of overlapping adjacent residue pairs."
    )
    gc_percent: float = Field(
        ge=0,
        le=100,
        description="GC percentage over residues with determinate GC status.",
    )
    gc_min_percent: float = Field(
        ge=0,
        le=100,
        description="Minimum possible GC percentage under IUPAC resolutions.",
    )
    gc_max_percent: float = Field(
        ge=0,
        le=100,
        description="Maximum possible GC percentage under IUPAC resolutions.",
    )
    ambiguous_count: int = Field(
        ge=0,
        description="Number of non-ACGT or non-ACGU IUPAC residues.",
    )
    gc_skew: float | None = Field(
        description="Concrete-base (G-C)/(G+C), or null when no concrete G/C exists."
    )
