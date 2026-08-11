import json
import tomllib
import zipfile
from pathlib import Path

import pytest

from scripts.check_release import biotools_versions, main, project_identity, wheel_identity

ROOT = Path(__file__).resolve().parents[1]
PROJECT_VERSION = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]


def test_project_identity_is_metadata_driven() -> None:
    assert project_identity(ROOT / "pyproject.toml") == ("computase", PROJECT_VERSION)


def test_wheel_identity_is_metadata_driven(tmp_path: Path) -> None:
    wheel = tmp_path / "computase-0.1.0-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr(
            "computase-0.1.0.dist-info/METADATA",
            "Name: computase\nVersion: 0.1.0\n",
        )

    assert wheel_identity(tmp_path, "computase") == ("computase", "0.1.0")


def test_biotools_versions_include_release_and_downloads(tmp_path: Path) -> None:
    metadata = tmp_path / "biotools.json"
    metadata.write_text(
        json.dumps(
            [
                {
                    "version": ["0.1.0"],
                    "download": [
                        {
                            "type": "Software package",
                            "url": "https://pypi.org/project/computase/",
                            "version": "0.1.0",
                        },
                        {
                            "type": "Source code",
                            "url": (
                                "https://github.com/example/computase/"
                                "archive/refs/tags/v0.1.0.tar.gz"
                            ),
                            "version": "0.1.0",
                        },
                    ],
                }
            ]
        )
    )

    assert biotools_versions(metadata) == ["0.1.0", "0.1.0", "0.1.0", "0.1.0"]


@pytest.mark.parametrize(  # type: ignore[untyped-decorator]
    "payload",
    [{}, [], [{}, {}], [{"version": ["0.1.0"], "download": []}]],
)
def test_biotools_versions_reject_malformed_metadata(tmp_path: Path, payload: object) -> None:
    metadata = tmp_path / "biotools.json"
    metadata.write_text(json.dumps(payload))

    with pytest.raises(ValueError):
        biotools_versions(metadata)


def test_release_check_rejects_bad_tag(tmp_path: Path) -> None:
    assert main(["--tag", "0.1.0", "--dist", str(tmp_path)]) == 1


def test_release_check_validates_all_release_versions(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    dist.mkdir()
    wheel = dist / "computase-0.1.0-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr(
            "computase-0.1.0.dist-info/METADATA",
            "Name: computase\nVersion: 0.1.0\n",
        )

    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "computase"\nversion = "0.1.0"\n')
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text("## [0.1.0]\n")
    citation = tmp_path / "CITATION.cff"
    citation.write_text("version: 0.1.0\n")
    package_init = tmp_path / "__init__.py"
    package_init.write_text('__version__ = "0.1.0"\n')
    biotools = tmp_path / "biotools.json"
    biotools.write_text(
        json.dumps(
            [
                {
                    "version": ["0.1.0"],
                    "download": [
                        {
                            "type": "Software package",
                            "url": "https://pypi.org/project/computase/",
                            "version": "0.1.0",
                        },
                        {
                            "type": "Source code",
                            "url": (
                                "https://github.com/example/computase/"
                                "archive/refs/tags/v0.1.0.tar.gz"
                            ),
                            "version": "0.1.0",
                        },
                    ],
                }
            ]
        )
    )
    arguments = [
        "--tag",
        "v0.1.0",
        "--dist",
        str(dist),
        "--pyproject",
        str(pyproject),
        "--changelog",
        str(changelog),
        "--citation",
        str(citation),
        "--package-init",
        str(package_init),
        "--biotools",
        str(biotools),
    ]

    assert main(arguments) == 0
    citation.write_text("version: 0.2.0\n")
    assert main(arguments) == 1
    citation.write_text("version: 0.1.0\n")
    biotools.write_text(
        json.dumps(
            [
                {
                    "version": ["0.1.0"],
                    "download": [
                        {
                            "type": "Software package",
                            "url": "https://pypi.org/project/computase/",
                            "version": "0.2.0",
                        },
                        {
                            "type": "Source code",
                            "url": (
                                "https://github.com/example/computase/"
                                "archive/refs/tags/v0.1.0.tar.gz"
                            ),
                            "version": "0.1.0",
                        },
                    ],
                }
            ]
        )
    )
    assert main(arguments) == 1
    biotools.write_text("{")
    assert main(arguments) == 1
