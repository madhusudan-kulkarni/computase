#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "computase>=0.1.1,<0.2",
# ]
# ///
"""Isolated JSON runner for the Computase companion Skill.

Reads one JSON object from stdin::

    {"operation": "summarize_sequence", "arguments": {"sequence": "ATGC"}}

Writes one JSON envelope to stdout. Never dispatches arbitrary callables and
never echoes the full input sequence.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Callable, Mapping
from typing import Any

from computase.errors import InvalidParameterError, InvalidSequenceError
from computase.seq import (
    enumerate_orfs,
    reverse_complement,
    scan_motif,
    summarize_sequence,
    translate_sequence,
)

OPERATIONS: dict[str, tuple[Callable[..., Any], frozenset[str]]] = {
    "summarize_sequence": (summarize_sequence, frozenset({"sequence"})),
    "reverse_complement": (reverse_complement, frozenset({"sequence"})),
    "translate_sequence": (
        translate_sequence,
        frozenset({"sequence", "table_id", "stop_handling"}),
    ),
    "enumerate_orfs": (
        enumerate_orfs,
        frozenset(
            {
                "sequence",
                "table_id",
                "start_codons",
                "include_nested",
                "require_stop",
                "min_length_nt",
                "max_results",
            }
        ),
    ),
    "scan_motif": (
        scan_motif,
        frozenset({"sequence", "motif", "strand", "overlapping", "max_matches"}),
    ),
}


def _error_envelope(
    *,
    operation: str | None,
    error_type: str,
    message: str,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "ok": False,
        "error": {"type": error_type, "message": message},
    }
    if operation is not None:
        payload["operation"] = operation
    return payload


def _success_envelope(operation: str, result: Any) -> dict[str, Any]:
    return {
        "ok": True,
        "operation": operation,
        "result": result.model_dump(mode="json"),
    }


def run_request(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Execute one allowlisted Computase operation request."""
    if set(payload) - {"operation", "arguments"}:
        unexpected = sorted(set(payload) - {"operation", "arguments"})
        return _error_envelope(
            operation=None,
            error_type="InvalidRequest",
            message=f"unexpected request fields: {', '.join(unexpected)}",
        )

    operation = payload.get("operation")
    if not isinstance(operation, str) or not operation:
        return _error_envelope(
            operation=None,
            error_type="InvalidRequest",
            message="operation must be a non-empty string",
        )

    if operation not in OPERATIONS:
        allowed = ", ".join(sorted(OPERATIONS))
        return _error_envelope(
            operation=operation,
            error_type="InvalidRequest",
            message=f"unknown operation {operation!r}; allowed: {allowed}",
        )

    arguments = payload.get("arguments", {})
    if not isinstance(arguments, dict):
        return _error_envelope(
            operation=operation,
            error_type="InvalidRequest",
            message="arguments must be a JSON object",
        )

    function, allowed_keys = OPERATIONS[operation]
    unexpected = sorted(set(arguments) - allowed_keys)
    if unexpected:
        return _error_envelope(
            operation=operation,
            error_type="InvalidRequest",
            message=f"unexpected arguments for {operation}: {', '.join(unexpected)}",
        )

    if "sequence" not in arguments or not isinstance(arguments["sequence"], str):
        return _error_envelope(
            operation=operation,
            error_type="InvalidRequest",
            message="arguments.sequence must be a string",
        )

    if operation == "scan_motif":
        motif = arguments.get("motif")
        if not isinstance(motif, str):
            return _error_envelope(
                operation=operation,
                error_type="InvalidRequest",
                message="arguments.motif must be a string",
            )

    try:
        result = function(**arguments)
    except (InvalidSequenceError, InvalidParameterError) as error:
        return _error_envelope(
            operation=operation,
            error_type=type(error).__name__,
            message=str(error),
        )
    except TypeError as error:
        return _error_envelope(
            operation=operation,
            error_type="InvalidRequest",
            message=f"invalid arguments for {operation}: {error}",
        )

    return _success_envelope(operation, result)


def main(argv: list[str] | None = None) -> int:
    """Read one JSON request from stdin and write one JSON response."""
    del argv  # CLI accepts no flags; keep signature stable for tests.
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else None
    except json.JSONDecodeError as error:
        json.dump(
            _error_envelope(
                operation=None,
                error_type="InvalidRequest",
                message=f"stdin must be valid JSON: {error.msg}",
            ),
            sys.stdout,
            separators=(",", ":"),
        )
        sys.stdout.write("\n")
        return 1

    if not isinstance(payload, dict):
        json.dump(
            _error_envelope(
                operation=None,
                error_type="InvalidRequest",
                message="request must be a JSON object",
            ),
            sys.stdout,
            separators=(",", ":"),
        )
        sys.stdout.write("\n")
        return 1

    response = run_request(payload)
    json.dump(response, sys.stdout, separators=(",", ":"))
    sys.stdout.write("\n")
    return 0 if response.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
