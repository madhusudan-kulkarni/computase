"""Tests for the Computase companion Skill isolated runner."""

from __future__ import annotations

import importlib.util
import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "skills" / "computase" / "scripts" / "run.py"


def _load_runner() -> ModuleType:
    spec = importlib.util.spec_from_file_location("computase_skill_runner", RUNNER_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


runner = _load_runner()


def _run_main(payload: object) -> tuple[int, dict[str, Any]]:
    stdin = io.StringIO(json.dumps(payload))
    stdout = io.StringIO()
    old_stdin = sys.stdin
    sys.stdin = stdin
    try:
        with redirect_stdout(stdout):
            code = runner.main([])
    finally:
        sys.stdin = old_stdin
    parsed: dict[str, Any] = json.loads(stdout.getvalue())
    return code, parsed


def test_runner_succeeds_for_all_five_operations() -> None:
    cases = {
        "summarize_sequence": {"sequence": "ATGC"},
        "reverse_complement": {"sequence": "ATGC"},
        "translate_sequence": {"sequence": "ATGGCC", "table_id": 1},
        "enumerate_orfs": {"sequence": "ATGAAATAA", "min_length_nt": 3},
        "scan_motif": {"sequence": "TTGAATTCAA", "motif": "GAATTC", "strand": "both"},
    }
    for operation, arguments in cases.items():
        response = runner.run_request({"operation": operation, "arguments": arguments})
        assert response["ok"] is True
        assert response["operation"] == operation
        assert isinstance(response["result"], dict)
        assert "computase_version" in response["result"]
        assert "sequence" not in response["result"]


def test_runner_rejects_unknown_operation() -> None:
    response = runner.run_request(
        {"operation": "stats_describe", "arguments": {"sequence": "ATGC"}}
    )
    assert response["ok"] is False
    assert response["error"]["type"] == "InvalidRequest"
    assert "unknown operation" in response["error"]["message"]


def test_runner_rejects_unexpected_arguments() -> None:
    response = runner.run_request(
        {
            "operation": "summarize_sequence",
            "arguments": {"sequence": "ATGC", "extra": True},
        }
    )
    assert response["ok"] is False
    assert response["error"]["type"] == "InvalidRequest"
    assert "unexpected arguments" in response["error"]["message"]


def test_runner_surfaces_package_validation_errors() -> None:
    response = runner.run_request(
        {"operation": "translate_sequence", "arguments": {"sequence": "ATGG"}}
    )
    assert response["ok"] is False
    assert response["error"]["type"] == "InvalidSequenceError"
    assert "complete codons" in response["error"]["message"]
    encoded = json.dumps(response)
    assert "ATGG" not in encoded


def test_runner_main_writes_success_envelope() -> None:
    code, response = _run_main(
        {"operation": "reverse_complement", "arguments": {"sequence": "ATGC"}}
    )
    assert code == 0
    assert response["ok"] is True
    assert response["result"]["reverse_complement"] == "GCAT"


def test_runner_main_writes_error_envelope_for_invalid_json() -> None:
    stdout = io.StringIO()
    old_stdin = sys.stdin
    sys.stdin = io.StringIO("{")
    try:
        with redirect_stdout(stdout):
            code = runner.main([])
    finally:
        sys.stdin = old_stdin
    response = json.loads(stdout.getvalue())
    assert code == 1
    assert response["ok"] is False
    assert response["error"]["type"] == "InvalidRequest"


@pytest.mark.parametrize(  # type: ignore[untyped-decorator]
    "payload",
    [
        {"operation": "summarize_sequence", "arguments": {"sequence": 1}},
        {"operation": "scan_motif", "arguments": {"sequence": "ATGC", "motif": 1}},
        {"operation": "summarize_sequence", "arguments": []},
    ],
)
def test_runner_rejects_malformed_argument_types(payload: dict[str, object]) -> None:
    response = runner.run_request(payload)
    assert response["ok"] is False
    assert response["error"]["type"] == "InvalidRequest"
