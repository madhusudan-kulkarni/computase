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


class ReverseComplementResult(ProvenanceModel):
    """Reverse complement of a nucleotide sequence."""

    sequence_type: Literal["dna", "rna"] = Field(description="Detected nucleotide alphabet.")
    length: int = Field(ge=1, description="Normalized input sequence length.")
    reverse_complement: str = Field(
        description="Reverse complement in the same DNA or RNA alphabet."
    )


class TranslationResult(ProvenanceModel):
    """Protein translation under an NCBI genetic code."""

    protein: str = Field(description="Translated protein, with stops represented as '*'.")
    table_id: int = Field(description="NCBI genetic-code table identifier.")
    table_name: str = Field(description="Primary NCBI genetic-code table name.")
    stop_handling: Literal["translate-through", "truncate-at-first-stop"] = Field(
        description="Effective stop-codon handling policy."
    )
    codon_count: int = Field(ge=1, description="Number of complete input codons.")
    stopped_early: bool = Field(
        description="Whether translation was truncated at an encountered stop codon."
    )


class Orf(ProvenanceModel):
    """One candidate open reading frame."""

    start: int = Field(ge=0, description="Forward-reference start coordinate.")
    end: int = Field(gt=0, description="Forward-reference end-exclusive coordinate.")
    strand: Literal["+", "-"] = Field(description="Coding strand.")
    frame: int = Field(ge=1, le=3, description="Reading frame relative to the coding strand.")
    length_nt: int = Field(ge=3, description="Candidate length in nucleotides.")
    protein: str = Field(description="Translated protein without a terminal stop marker.")
    complete: bool = Field(description="Whether an in-frame terminal stop codon was found.")


class OrfEnumeration(ProvenanceModel):
    """Bounded collection of candidate open reading frames."""

    orfs: list[Orf] = Field(description="Candidate ORFs in deterministic coordinate order.")
    total_found: int = Field(ge=0, description="Total candidates found before result limiting.")
    truncated: bool = Field(description="Whether candidates were omitted by max_results.")
    coordinate_system: Literal["0-based-half-open"] = "0-based-half-open"
    note: str = Field(
        default="These are candidate ORFs, not gene predictions.",
        description="Scientific interpretation boundary.",
    )


class MotifMatch(ProvenanceModel):
    """One motif occurrence on the forward reference."""

    start: int = Field(ge=0, description="Forward-reference start coordinate.")
    end: int = Field(gt=0, description="Forward-reference end-exclusive coordinate.")
    strand: Literal["+", "-", "both"] = Field(description="Matching motif orientation.")
    matched_sequence: str = Field(description="Forward-reference sequence span.")


class MotifScanResult(ProvenanceModel):
    """Bounded motif scan result."""

    motif: str = Field(description="Normalized IUPAC motif.")
    strand: Literal["forward", "reverse", "both"] = Field(description="Requested strand policy.")
    matches: list[MotifMatch] = Field(description="Motif occurrences in coordinate order.")
    total_found: int = Field(ge=0, description="Total occurrences before result limiting.")
    truncated: bool = Field(description="Whether occurrences were omitted by max_matches.")
    coordinate_system: Literal["0-based-half-open"] = "0-based-half-open"
