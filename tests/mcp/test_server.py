from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from mcp.client.client import Client

from computase import __version__
from computase.mcp.server import build_parser, main, server

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
        assert result.structured_content["computase_version"] == __version__
        assert "parameters" in result.structured_content


async def test_public_validation_errors_are_actionable_tool_errors() -> None:
    cases: dict[str, tuple[dict[str, Any], str]] = {
        "computase_summarize_sequence": ({"sequence": "AUTG"}, "both T and U"),
        "computase_reverse_complement": ({"sequence": "AUTG"}, "both T and U"),
        "computase_translate_sequence": (
            {"sequence": "ATG", "table_id": 9999},
            "table_id",
        ),
        "computase_enumerate_orfs": (
            {"sequence": "ATG", "table_id": 9999},
            "table_id",
        ),
        "computase_scan_motif": ({"sequence": "ATG", "motif": "X"}, "motif"),
    }

    for name, (arguments, expected_message) in cases.items():
        result = await _call(name, arguments)
        assert result.is_error is True
        assert expected_message in result.content[0].text


def test_build_parser_defaults() -> None:
    parser = build_parser()
    args = parser.parse_args([])
    assert args.transport == "stdio"
    assert args.host == "127.0.0.1"
    assert args.port == 8000


def test_build_parser_streamable_http() -> None:
    parser = build_parser()
    args = parser.parse_args(
        ["--transport", "streamable-http", "--host", "0.0.0.0", "--port", "9000"]
    )
    assert args.transport == "streamable-http"
    assert args.host == "0.0.0.0"
    assert args.port == 9000


def test_build_parser_version(capsys: Any) -> None:
    parser = build_parser()
    try:
        parser.parse_args(["--version"])
    except SystemExit as exc:
        assert exc.code == 0
    captured = capsys.readouterr()
    assert __version__ in captured.out or __version__ in captured.err


def test_main_stdio(monkeypatch: Any) -> None:
    called_with: dict[str, Any] = {}

    def mock_run(**kwargs: Any) -> None:
        called_with.update(kwargs)

    monkeypatch.setattr(server, "run", mock_run)
    main([])
    assert called_with == {"transport": "stdio"}


def test_main_streamable_http(monkeypatch: Any) -> None:
    called_with: dict[str, Any] = {}

    def mock_run(**kwargs: Any) -> None:
        called_with.update(kwargs)

    monkeypatch.setattr(server, "run", mock_run)
    main(["--transport", "streamable-http", "--host", "127.0.0.1", "--port", "8080"])
    assert called_with == {
        "transport": "streamable-http",
        "host": "127.0.0.1",
        "port": 8080,
    }
