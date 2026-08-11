#!/usr/bin/env python3
"""Validate tag, project metadata, changelog, and exact wheel metadata."""

import argparse
import re
import sys
import tomllib
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SEMVER_TAG = re.compile(r"^v(?P<version>(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*))$")


def project_identity(pyproject: Path) -> tuple[str, str]:
    """Read the distribution name and version from project metadata."""
    project = tomllib.loads(pyproject.read_text())["project"]
    return str(project["name"]), str(project["version"])


def wheel_identity(dist: Path, project_name: str) -> tuple[str, str]:
    """Read name and version from the project's built wheel metadata."""
    wheel_prefix = project_name.replace("-", "_")
    wheels = sorted(dist.glob(f"{wheel_prefix}-*.whl"))
    if len(wheels) != 1:
        raise ValueError(f"expected exactly one {wheel_prefix}-*.whl in {dist}")
    with zipfile.ZipFile(wheels[0]) as archive:
        metadata_name = next(
            (name for name in archive.namelist() if name.endswith(".dist-info/METADATA")),
            None,
        )
        if metadata_name is None:
            raise ValueError(f"{wheels[0].name} has no dist-info/METADATA")
        metadata = archive.read(metadata_name).decode()
    name = re.search(r"(?m)^Name:\s*(.+)$", metadata)
    version = re.search(r"(?m)^Version:\s*(.+)$", metadata)
    if name is None or version is None:
        raise ValueError("wheel metadata is missing Name or Version")
    return name.group(1).strip(), version.group(1).strip()


def changelog_has_version(changelog: Path, version: str) -> bool:
    """Return whether the changelog has an exact version heading."""
    return (
        re.search(rf"(?m)^## \[{re.escape(version)}\](?:\s|$)", changelog.read_text()) is not None
    )


def main(argv: list[str] | None = None) -> int:
    """Run release consistency checks."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--dist", type=Path, default=ROOT / "dist")
    parser.add_argument("--pyproject", type=Path, default=ROOT / "pyproject.toml")
    parser.add_argument("--changelog", type=Path, default=ROOT / "CHANGELOG.md")
    args = parser.parse_args(argv)

    match = _SEMVER_TAG.fullmatch(args.tag)
    if match is None:
        print("check_release: tag must be vMAJOR.MINOR.PATCH", file=sys.stderr)
        return 1
    expected = match.group("version")
    project_name, project_version = project_identity(args.pyproject)
    try:
        wheel_name, wheel_version = wheel_identity(args.dist, project_name)
    except ValueError as error:
        print(f"check_release: {error}", file=sys.stderr)
        return 1

    checks = (
        (project_version == expected, f"project version {project_version} != tag {expected}"),
        (wheel_name == project_name, f"wheel name {wheel_name} != project {project_name}"),
        (wheel_version == expected, f"wheel version {wheel_version} != tag {expected}"),
        (
            changelog_has_version(args.changelog, expected),
            f"CHANGELOG.md has no [{expected}] section",
        ),
    )
    failures = [message for passed, message in checks if not passed]
    if failures:
        print("check_release: " + "; ".join(failures), file=sys.stderr)
        return 1
    print(f"check_release: OK {project_name} {expected}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
