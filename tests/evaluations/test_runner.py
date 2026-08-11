from evaluations.runner import CASES, run_evaluations


def test_evaluations_cover_all_operations_and_errors() -> None:
    operations = {case.operation for case in CASES if case.expected_error is None}

    assert operations == {
        "summarize_sequence",
        "reverse_complement",
        "translate_sequence",
        "enumerate_orfs",
        "scan_motif",
    }
    assert sum(case.expected_error is not None for case in CASES) >= 2


def test_evaluation_suite_passes() -> None:
    results = run_evaluations()

    assert all(result.passed for result in results), [
        result for result in results if not result.passed
    ]
