from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_MARKDOWN = {
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "ROADMAP.md",
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
    candidates = list(ROOT.glob("*.md")) + list((ROOT / "skills").rglob("*.md"))
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


def test_citation_matches_release_identity() -> None:
    citation = (ROOT / "CITATION.cff").read_text()

    assert 'title: "Computase"' in citation
    assert "version: 0.1.0" in citation
    assert "license: MIT" in citation
