import io
import json
from collections.abc import Callable, Iterator
from contextlib import AbstractContextManager
from typing import BinaryIO

import pytest

from scripts.verify_pypi_release import verify_pypi_release


def _opener(payloads: Iterator[bytes]) -> Callable[[str], AbstractContextManager[BinaryIO]]:
    def open_url(url: str) -> AbstractContextManager[BinaryIO]:
        assert url == "https://pypi.org/pypi/computase/0.1.0/json"
        return io.BytesIO(next(payloads))

    return open_url


def test_verify_pypi_release_retries_malformed_response() -> None:
    payloads = iter(
        [
            b"{",
            json.dumps({"info": {"version": "0.1.0"}}).encode(),
        ]
    )
    sleeps: list[float] = []

    verify_pypi_release(
        "computase",
        "0.1.0",
        attempts=2,
        delay_seconds=0,
        opener=_opener(payloads),
        sleeper=sleeps.append,
    )

    assert sleeps == [0]


def test_verify_pypi_release_reports_retry_exhaustion() -> None:
    payloads = iter([json.dumps({"info": {"version": "0.2.0"}}).encode()])

    with pytest.raises(RuntimeError, match="reported version '0.2.0'"):
        verify_pypi_release(
            "computase",
            "0.1.0",
            attempts=1,
            opener=_opener(payloads),
        )
