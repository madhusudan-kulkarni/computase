from computase import __version__
from computase.core.models import ProvenanceModel
from computase.errors import InvalidParameterError, InvalidSequenceError


def test_public_errors_are_value_errors() -> None:
    assert issubclass(InvalidSequenceError, ValueError)
    assert issubclass(InvalidParameterError, ValueError)


def test_provenance_model_records_version_and_effective_parameters() -> None:
    result = ProvenanceModel(parameters={"table_id": 1})

    assert result.computase_version == __version__
    assert result.parameters == {"table_id": 1}
