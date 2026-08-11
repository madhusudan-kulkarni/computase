import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT_VERSION = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]
PUBLIC_MARKDOWN = {
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "ROADMAP.md",
    "docs/python-examples.md",
    "skills/computase/SKILL.md",
    "skills/computase/references/usage-examples.md",
}
TOOL_NAMES = {
    "computase_summarize_sequence",
    "computase_reverse_complement",
    "computase_translate_sequence",
    "computase_enumerate_orfs",
    "computase_scan_motif",
}


def test_public_markdown_inventory_is_exact() -> None:
    candidates = (
        list(ROOT.glob("*.md"))
        + list((ROOT / "docs").rglob("*.md"))
        + list((ROOT / "skills").rglob("*.md"))
    )
    paths = {
        path.relative_to(ROOT).as_posix()
        for path in candidates
        if path.name != "IMPLEMENTATION_PLAN.md"
    }

    assert paths == PUBLIC_MARKDOWN


def test_skill_references_exact_tool_inventory() -> None:
    skill = (ROOT / "skills/computase/SKILL.md").read_text()

    assert all(f"`{name}`" in skill for name in TOOL_NAMES)
    assert "stats_" not in skill
    assert "uv run --script skills/computase/scripts/run.py" in skill
    assert "never mutate the active project or global Python" in skill
    assert (ROOT / "skills/computase/scripts/run.py").is_file()
    assert "Present results" in skill
    assert "raw output" in skill


def test_citation_matches_release_identity() -> None:
    citation = (ROOT / "CITATION.cff").read_text()

    assert 'title: "Computase"' in citation
    assert "type: software" in citation
    assert f"version: {PROJECT_VERSION}" in citation
    assert "license: MIT" in citation
    assert "family-names: Kulkarni" in citation
    assert "given-names: Madhusudan" in citation


def test_biotools_draft_matches_release_identity() -> None:
    records = json.loads((ROOT / "metadata" / "biotools.json").read_text())

    assert len(records) == 1
    assert records[0]["name"] == "Computase"
    assert records[0]["biotoolsID"] == "computase"
    assert records[0]["version"] == [PROJECT_VERSION]
    assert records[0]["license"] == "MIT"
    assert len(records[0]["function"]) == 5
    assert all(download["version"] == PROJECT_VERSION for download in records[0]["download"])
