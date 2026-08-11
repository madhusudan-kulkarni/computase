"""Public exceptions raised for invalid Computase inputs."""


class InvalidSequenceError(ValueError):
    """Raised when a nucleotide sequence is malformed or unsupported."""


class InvalidParameterError(ValueError):
    """Raised when an operation parameter is invalid or inconsistent."""


__all__ = ["InvalidParameterError", "InvalidSequenceError"]
