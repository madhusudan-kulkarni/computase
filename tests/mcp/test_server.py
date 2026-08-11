from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from mcp.client.client import Client

from computase.mcp.server import server

TOOL_NAMES = {
    "computase_summarize_sequence",
    "computase_reverse_complement",
    "computase_translate_sequence",
    "computase_enumerate_orfs",
    "computase_scan_motif",
}


@asynccontextmanager
async def _client() -> AsyncIterator[Client]:
    async with Client(server) as client:
        yield client


async def _call(name: str, arguments: dict[str, Any]) -> Any:
    async with _client() as client:
        return await client.call_tool(name, arguments)


async def test_registers_exact_five_tools_with_closed_world_annotations() -> None:
    async with _client() as client:
        tools = (await client.list_tools()).tools

    assert {tool.name for tool in tools} == TOOL_NAMES
    for tool in tools:
        assert tool.output_schema
        assert tool.annotations is not None
        annotations = tool.annotations.model_dump()
        assert annotations["read_only_hint"] is True
        assert annotations["destructive_hint"] is False
        assert annotations["idempotent_hint"] is True
        assert annotations["open_world_hint"] is False


async def test_tool_schemas_expose_fixed_defaults_and_caps() -> None:
    async with _client() as client:
        tools = {tool.name: tool for tool in (await client.list_tools()).tools}

    translate = tools["computase_translate_sequence"].input_schema["properties"]
    assert translate["table_id"]["default"] == 1
    assert translate["stop_handling"]["default"] == "translate-through"

    orfs = tools["computase_enumerate_orfs"].input_schema["properties"]
    assert orfs["max_results"]["default"] == 1000
    assert orfs["max_results"]["maximum"] == 10_000

    motif = tools["computase_scan_motif"].input_schema["properties"]
    assert motif["max_matches"]["default"] == 10_000
    assert motif["max_matches"]["maximum"] == 100_000
    assert motif["motif"]["maxLength"] == 500


async def test_all_tools_return_structured_results() -> None:
    calls: dict[str, dict[str, Any]] = {
        "computase_summarize_sequence": {"sequence": "AAGC"},
        "computase_reverse_complement": {"sequence": "ATGC"},
        "computase_translate_sequence": {"sequence": "ATGGCC"},
        "computase_enumerate_orfs": {"sequence": "ATGAAATAA", "min_length_nt": 3},
        "computase_scan_motif": {"sequence": "AAGA", "motif": "AAR"},
    }

    for name, arguments in calls.items():
        result = await _call(name, arguments)
        assert result.is_error is False, name
        assert result.structured_content
        assert result.structured_content["computase_version"] == "0.1.0"
        assert "parameters" in result.structured_content


async def test_public_validation_errors_are_actionable_tool_errors() -> None:
    invalid_sequence = await _call(
        "computase_reverse_complement",
        {"sequence": "AUTG"},
    )
    invalid_parameter = await _call(
        "computase_translate_sequence",
        {"sequence": "ATG", "table_id": 9999},
    )

    assert invalid_sequence.is_error is True
    assert "both T and U" in invalid_sequence.content[0].text
    assert invalid_parameter.is_error is True
    assert "table_id" in invalid_parameter.content[0].text
