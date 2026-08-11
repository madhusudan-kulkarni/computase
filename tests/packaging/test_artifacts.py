import asyncio
import os
import socket
import subprocess
import tarfile
import tomllib
import zipfile
from pathlib import Path

import pytest
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.client.streamable_http import streamable_http_client

ROOT = Path(__file__).resolve().parents[2]
PROJECT = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
PROJECT_NAME = str(PROJECT["name"])
PROJECT_VERSION = str(PROJECT["version"])


@pytest.fixture(scope="module")  # type: ignore[untyped-decorator]
def artifacts(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, Path]:
    configured_dist = os.environ.get("COMPUTASE_DIST_DIR")
    if configured_dist:
        output = Path(configured_dist)
        if not output.is_absolute():
            output = ROOT / output
    else:
        output = tmp_path_factory.mktemp("dist")
        build = subprocess.run(
            ["uv", "build", "--out-dir", str(output)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert build.returncode == 0, build.stderr

    wheels = list(output.glob("*.whl"))
    sdists = list(output.glob("*.tar.gz"))
    assert len(wheels) == 1
    assert len(sdists) == 1
    return wheels[0], sdists[0]


def test_wheel_is_lean_and_typed(artifacts: tuple[Path, Path]) -> None:
    wheel, _ = artifacts
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()

    dist_info = f"{PROJECT_NAME.replace('-', '_')}-{PROJECT_VERSION}.dist-info/"
    package_files = [name for name in names if not name.startswith(dist_info)]
    assert package_files
    assert all(name.startswith("computase/") for name in package_files)
    assert "computase/py.typed" in package_files


def test_sdist_contains_public_sources_but_not_internal_suites(
    artifacts: tuple[Path, Path],
) -> None:
    _, sdist = artifacts
    with tarfile.open(sdist) as archive:
        names = "\n".join(archive.getnames())

    for required in (
        "src/computase",
        "docs/python-examples.md",
        "skills/computase/SKILL.md",
        "skills/computase/references/usage-examples.md",
        "skills/computase/scripts/run.py",
        "README.md",
        "LICENSE",
        "pyproject.toml",
    ):
        assert required in names
    for excluded in ("tests/", "evaluations/", "ROADMAP.md", "IMPLEMENTATION_PLAN.md"):
        assert excluded not in names


def test_built_wheel_imports_in_isolated_environment(artifacts: tuple[Path, Path]) -> None:
    wheel, _ = artifacts
    smoke = subprocess.run(
        [
            "uv",
            "run",
            "--isolated",
            "--with",
            str(wheel),
            "python",
            "-c",
            (
                "import computase; "
                "from computase.seq import reverse_complement; "
                f"assert computase.__version__ == {PROJECT_VERSION!r}; "
                "assert reverse_complement('ATGC').reverse_complement == 'GCAT'"
            ),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert smoke.returncode == 0, smoke.stderr


def test_built_sdist_imports_in_isolated_environment(artifacts: tuple[Path, Path]) -> None:
    _, sdist = artifacts
    smoke = subprocess.run(
        [
            "uv",
            "run",
            "--isolated",
            "--with",
            str(sdist),
            "python",
            "-c",
            f"import computase; assert computase.__version__ == {PROJECT_VERSION!r}",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert smoke.returncode == 0, smoke.stderr


async def test_built_wheel_serves_stdio_mcp(artifacts: tuple[Path, Path]) -> None:
    wheel, _ = artifacts
    parameters = StdioServerParameters(
        command="uvx",
        args=["--from", str(wheel), "computase"],
        cwd=ROOT,
    )
    async with (
        stdio_client(parameters) as (read_stream, write_stream),
        ClientSession(read_stream, write_stream) as session,
    ):
        initialized = await session.initialize()
        tools = await session.list_tools()
        result = await session.call_tool(
            "computase_reverse_complement",
            {"sequence": "ATGC"},
        )

    assert initialized.server_info.name == "computase"
    assert len(tools.tools) == 5
    assert result.is_error is False
    assert result.structured_content["reverse_complement"] == "GCAT"


async def test_built_wheel_serves_streamable_http(artifacts: tuple[Path, Path]) -> None:
    wheel, _ = artifacts
    with socket.socket() as reserved:
        reserved.bind(("127.0.0.1", 0))
        port = int(reserved.getsockname()[1])

    process = subprocess.Popen(
        [
            "uvx",
            "--from",
            str(wheel),
            "computase",
            "--transport",
            "streamable-http",
            "--port",
            str(port),
        ],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(100):
            try:
                reader, writer = await asyncio.open_connection("127.0.0.1", port)
                writer.close()
                await writer.wait_closed()
                del reader
                break
            except OSError:
                await asyncio.sleep(0.05)
        else:
            raise AssertionError("streamable HTTP server did not start")

        async with streamable_http_client(f"http://127.0.0.1:{port}/mcp") as streams:
            read_stream, write_stream = streams
            async with ClientSession(read_stream, write_stream) as session:
                initialized = await session.initialize()
                result = await session.call_tool(
                    "computase_summarize_sequence",
                    {"sequence": "AAGC"},
                )
        assert initialized.server_info.name == "computase"
        assert result.is_error is False
        assert result.structured_content["length"] == 4
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)
