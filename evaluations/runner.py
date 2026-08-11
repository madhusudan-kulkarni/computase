"""Run static reference and recoverable-error evaluations."""

import json
from collections.abc import Callable
from dataclasses import asdict, dataclass
from typing import Any

from computase.seq import (
    enumerate_orfs,
    reverse_complement,
    scan_motif,
    summarize_sequence,
    translate_sequence,
)

_OPERATIONS: dict[str, Callable[..., Any]] = {
    "summarize_sequence": summarize_sequence,
    "reverse_complement": reverse_complement,
    "translate_sequence": translate_sequence,
    "enumerate_orfs": enumerate_orfs,
    "scan_motif": scan_motif,
}


@dataclass(frozen=True)
class EvaluationCase:
    """One static operation-result or recoverable-error check."""

    name: str
    operation: str
    arguments: dict[str, Any]
    expected: Any = None
    extract: tuple[str | int, ...] = ()
    expected_error: str | None = None


@dataclass(frozen=True)
class EvaluationResult:
    """Observed outcome of one evaluation case."""

    name: str
    operation: str
    passed: bool
    expected: Any
    observed: Any


CASES = (
    EvaluationCase(
        "short composition",
        "summarize_sequence",
        {"sequence": "AAGC"},
        expected={"A": 2, "G": 1, "C": 1},
        extract=("composition",),
    ),
    EvaluationCase(
        "M13 reverse complement",
        "reverse_complement",
        {"sequence": "TGTAAAACGACGGCCAGT"},
        expected="ACTGGCCGTCGTTTTACA",
        extract=("reverse_complement",),
    ),
    EvaluationCase(
        "NCBI translation example",
        "translate_sequence",
        {"sequence": "ATGGCCATTGTAATGGGCCGCTGAAAGGGTGCCCGATAG"},
        expected="MAIVMGR*KGAR*",
        extract=("protein",),
    ),
    EvaluationCase(
        "complete candidate ORF",
        "enumerate_orfs",
        {"sequence": "ATGAAATAA", "min_length_nt": 3},
        expected="MK",
        extract=("orfs", 0, "protein"),
    ),
    EvaluationCase(
        "pUC19 EcoRI site",
        "scan_motif",
        {
            "sequence": (
                "ATGACCATGATTACGCCAAGCTTGCATGCCTGCAGGTCGACTCTAGAGGATCCCCGGGTACCGAGCTCGAATTC"
            ),
            "motif": "GAATTC",
        },
        expected=68,
        extract=("matches", 0, "start"),
    ),
    EvaluationCase(
        "mixed alphabet error",
        "reverse_complement",
        {"sequence": "AUTG"},
        expected_error="both T and U",
    ),
    EvaluationCase(
        "unknown genetic code error",
        "translate_sequence",
        {"sequence": "ATG", "table_id": 9999},
        expected_error="table_id",
    ),
)


def _extract(value: Any, path: tuple[str | int, ...]) -> Any:
    current = value
    for part in path:
        if isinstance(part, int) or isinstance(current, dict):
            current = current[part]
        else:
            current = getattr(current, part)
    return current


def run_case(case: EvaluationCase) -> EvaluationResult:
    """Execute and grade one evaluation case."""
    operation = _OPERATIONS[case.operation]
    try:
        result = operation(**case.arguments)
    except Exception as error:  # noqa: BLE001 - unexpected errors are graded failures
        observed = str(error)
        passed = case.expected_error is not None and case.expected_error in observed
        return EvaluationResult(
            case.name,
            case.operation,
            passed,
            case.expected_error,
            observed,
        )

    observed = _extract(result, case.extract)
    return EvaluationResult(
        case.name,
        case.operation,
        case.expected_error is None and observed == case.expected,
        case.expected if case.expected_error is None else case.expected_error,
        observed,
    )


def run_evaluations() -> list[EvaluationResult]:
    """Run all CI-only evaluation cases."""
    return [run_case(case) for case in CASES]


def main() -> int:
    """Print machine-readable results and return a CI-friendly status."""
    results = run_evaluations()
    print(json.dumps([asdict(result) for result in results], indent=2))
    return 0 if all(result.passed for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
