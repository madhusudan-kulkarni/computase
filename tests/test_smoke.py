from importlib.metadata import version

from computase import __version__


def test_package_version() -> None:
    assert __version__ == version("computase")
