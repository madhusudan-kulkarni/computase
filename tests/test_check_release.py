import zipfile
from pathlib import Path

from scripts.check_release import main, project_identity, wheel_identity

ROOT = Path(__file__).resolve().parents[1]


def test_project_identity_is_metadata_driven() -> None:
    assert project_identity(ROOT / "pyproject.toml") == ("computase", "0.1.0")


def test_wheel_identity_is_metadata_driven(tmp_path: Path) -> None:
    wheel = tmp_path / "computase-0.1.0-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr(
            "computase-0.1.0.dist-info/METADATA",
            "Name: computase\nVersion: 0.1.0\n",
        )

    assert wheel_identity(tmp_path, "computase") == ("computase", "0.1.0")


def test_release_check_rejects_bad_tag(tmp_path: Path) -> None:
    assert main(["--tag", "0.1.0", "--dist", str(tmp_path)]) == 1
