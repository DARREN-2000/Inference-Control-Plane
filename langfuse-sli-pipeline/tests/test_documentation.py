"""Documentation is part of the deliverable and must not drift from code."""

from __future__ import annotations

import re
from pathlib import Path

from gateway_sli.governance import METRIC_REGISTRY

ROOT = Path(__file__).parents[1]
DOCS = [
    ROOT / "README.md",
    ROOT / "DESIGN.md",
    *sorted((ROOT / "docs").glob("*.md")),
    ROOT / "deploy" / "README.md",
    ROOT / "monitors" / "README.md",
]


def test_all_local_markdown_links_resolve():
    broken = []
    for doc in DOCS:
        for _, target in re.findall(r"\[([^]]+)\]\(([^)]+)\)", doc.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            local = target.split("#", 1)[0]
            if local and not (doc.parent / local).resolve().exists():
                broken.append((str(doc.relative_to(ROOT)), target))
    assert not broken, broken


def test_design_has_exactly_four_explicit_print_pages():
    text = (ROOT / "DESIGN.md").read_text(encoding="utf-8")
    assert text.count("page-break-after: always") == 3
    for page in range(1, 5):
        assert f"Page {page} of 4" in text


def test_architecture_has_source_and_static_rendering():
    text = (ROOT / "docs" / "architecture.md").read_text(encoding="utf-8")
    assert "```mermaid" in text
    assert "PRIVACY BOUNDARY" in text
    svg = (ROOT / "docs" / "architecture.svg").read_text(encoding="utf-8")
    assert "<svg" in svg and "PRIVACY BOUNDARY" in svg
    assert 'viewBox="0 0 1920 1080"' in svg
    drawio = Path("docs/architecture.drawio")
    assert drawio.is_file() and "Architecture" in drawio.read_text(encoding="utf-8")
    assert "Run sequence" in drawio.read_text(encoding="utf-8")
    assert svg.count('marker-end="url(#') >= 12
    assert all(effect not in svg.lower() for effect in ("gradient", "filter", "drop-shadow"))


def test_readme_catalogues_every_registered_metric():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    missing = sorted(name for name in METRIC_REGISTRY if name not in readme)
    assert not missing, missing


def test_markdown_fences_are_balanced_and_no_trailing_whitespace():
    for doc in DOCS:
        text = doc.read_text(encoding="utf-8")
        assert len(re.findall(r"^```", text, re.MULTILINE)) % 2 == 0, doc
        trailing = [i for i, line in enumerate(text.splitlines(), 1) if line.rstrip() != line]
        assert not trailing, (doc, trailing)
