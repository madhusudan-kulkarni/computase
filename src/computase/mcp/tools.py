"""Thin MCP adapters over the public Computase Python API."""

import asyncio
from typing import Annotated, Literal

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import Field

from computase.core.validation import (
    MAX_MOTIF_MATCHES,
    MAX_MOTIF_PATTERN_LENGTH,
    MAX_ORF_RESULTS,
    MAX_SEQUENCE_LENGTH,
)
from computase.errors import InvalidParameterError, InvalidSequenceError
from computase.seq import (
    MotifScanResult,
    OrfEnumeration,
    ReverseComplementResult,
    SequenceSummary,
    TranslationResult,
    enumerate_orfs,
    reverse_complement,
    scan_motif,
    summarize_sequence,
    translate_sequence,
)

NucleotideSequence = Annotated[
    str,
    Field(
        min_length=1,
        description=(
            "Raw nucleotide sequence or one FASTA record; IUPAC codes are accepted. "
            f"The normalized sequence is limited to {MAX_SEQUENCE_LENGTH:,} nucleotides."
        ),
    ),
]
_ANNOTATIONS = {
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": False,
}


def _tool_error(error: InvalidSequenceError | InvalidParameterError) -> ToolError:
    return ToolError(str(error))


def register_tools(server: MCPServer) -> None:
    """Register the five sequence-only Computase tools."""

    @server.tool(  # type: ignore[untyped-decorator]
        name="computase_summarize_sequence",
        title="Summarize sequence",
        description="Summarize composition, GC uncertainty, and GC skew.",
        annotations=_ANNOTATIONS,
        structured_output=True,
    )
    async def summarize(sequence: NucleotideSequence) -> SequenceSummary:
        try:
            return await asyncio.to_thread(summarize_sequence, sequence)
        except (InvalidSequenceError, InvalidParameterError) as error:
            raise _tool_error(error) from None

    @server.tool(  # type: ignore[untyped-decorator]
        name="computase_reverse_complement",
        title="Reverse complement",
        description="Compute an IUPAC-aware DNA or RNA reverse complement.",
        annotations=_ANNOTATIONS,
        structured_output=True,
    )
    async def complement(sequence: NucleotideSequence) -> ReverseComplementResult:
        try:
            return await asyncio.to_thread(reverse_complement, sequence)
        except (InvalidSequenceError, InvalidParameterError) as error:
            raise _tool_error(error) from None

    @server.tool(  # type: ignore[untyped-decorator]
        name="computase_translate_sequence",
        title="Translate sequence",
        description="Translate complete codons with a selected NCBI genetic code.",
        annotations=_ANNOTATIONS,
        structured_output=True,
    )
    async def translate(
        sequence: NucleotideSequence,
        table_id: Annotated[
            int,
            Field(default=1, ge=1, description="NCBI genetic-code table identifier."),
        ] = 1,
        stop_handling: Annotated[
            Literal["translate-through", "truncate-at-first-stop"],
            Field(default="translate-through", description="Stop-codon handling policy."),
        ] = "translate-through",
    ) -> TranslationResult:
        try:
            return await asyncio.to_thread(
                translate_sequence,
                sequence,
                table_id=table_id,
                stop_handling=stop_handling,
            )
        except (InvalidSequenceError, InvalidParameterError) as error:
            raise _tool_error(error) from None

    @server.tool(  # type: ignore[untyped-decorator]
        name="computase_enumerate_orfs",
        title="Enumerate candidate ORFs",
        description="Enumerate bounded candidate ORFs across all six reading frames.",
        annotations=_ANNOTATIONS,
        structured_output=True,
    )
    async def orfs(
        sequence: NucleotideSequence,
        table_id: Annotated[
            int,
            Field(default=1, ge=1, description="NCBI genetic-code table identifier."),
        ] = 1,
        start_codons: Annotated[
            Literal["table-starts", "atg-only"],
            Field(default="table-starts", description="Allowed start-codon policy."),
        ] = "table-starts",
        include_nested: Annotated[
            bool,
            Field(default=False, description="Report starts nested before the same stop."),
        ] = False,
        require_stop: Annotated[
            bool,
            Field(default=True, description="Require an in-frame terminal stop codon."),
        ] = True,
        min_length_nt: Annotated[
            int,
            Field(default=30, ge=1, description="Minimum nucleotide span including stop."),
        ] = 30,
        max_results: Annotated[
            int,
            Field(
                default=1000,
                ge=1,
                le=MAX_ORF_RESULTS,
                description="Maximum returned candidates.",
            ),
        ] = 1000,
    ) -> OrfEnumeration:
        try:
            return await asyncio.to_thread(
                enumerate_orfs,
                sequence,
                table_id=table_id,
                start_codons=start_codons,
                include_nested=include_nested,
                require_stop=require_stop,
                min_length_nt=min_length_nt,
                max_results=max_results,
            )
        except (InvalidSequenceError, InvalidParameterError) as error:
            raise _tool_error(error) from None

    @server.tool(  # type: ignore[untyped-decorator]
        name="computase_scan_motif",
        title="Scan motif",
        description="Scan an IUPAC motif on the forward, reverse, or both strands.",
        annotations=_ANNOTATIONS,
        structured_output=True,
    )
    async def motif(
        sequence: NucleotideSequence,
        motif: Annotated[
            str,
            Field(
                min_length=1,
                max_length=MAX_MOTIF_PATTERN_LENGTH,
                description="IUPAC nucleotide pattern.",
            ),
        ],
        strand: Annotated[
            Literal["forward", "reverse", "both"],
            Field(default="forward", description="Strand orientation to scan."),
        ] = "forward",
        overlapping: Annotated[
            bool,
            Field(default=True, description="Report overlapping sites."),
        ] = True,
        max_matches: Annotated[
            int,
            Field(
                default=10_000,
                ge=1,
                le=MAX_MOTIF_MATCHES,
                description="Maximum returned sites.",
            ),
        ] = 10_000,
    ) -> MotifScanResult:
        try:
            return await asyncio.to_thread(
                scan_motif,
                sequence,
                motif,
                strand=strand,
                overlapping=overlapping,
                max_matches=max_matches,
            )
        except (InvalidSequenceError, InvalidParameterError) as error:
            raise _tool_error(error) from None
