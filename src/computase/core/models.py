"""Shared Pydantic result-model infrastructure."""

from typing import Any

from pydantic import BaseModel, Field

from computase import __version__


class ProvenanceModel(BaseModel):
    """Base for results that record software and effective parameters."""

    computase_version: str = Field(
        default=__version__,
        description="Computase version used for the computation.",
    )
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="Effective operation parameters, excluding the input sequence.",
    )
