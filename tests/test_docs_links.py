from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LINK_PATTERN = re.compile(r"!?(?:\[[^\]]*\])\(([^)]+)\)")
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.*\S)\s*$", re.MULTILINE)
DOC_ROOTS = [
    REPO_ROOT / "README.md",
    REPO_ROOT / "CHANGELOG.md",
    REPO_ROOT / "docs",
    REPO_ROOT / "examples",
    REPO_ROOT / "ai-instructions.md",
]
IGNORED_PREFIXES = ("http://", "https://", "mailto:")


def _iter_markdown_files() -> list[Path]:
    files: list[Path] = []
    for root in DOC_ROOTS:
        if root.is_file():
            files.append(root)
            continue
        files.extend(sorted(root.rglob("*.md")))
    return files


def _normalize_target(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    return target


def _is_external(target: str) -> bool:
    return target.startswith(IGNORED_PREFIXES)


def _resolve_target(source_file: Path, target: str) -> Path:
    if target.startswith("/"):
        return (REPO_ROOT / target.lstrip("/")).resolve()
    return (source_file.parent / target).resolve()


def _slugify_heading(title: str) -> str:
    normalized = title.strip().lower()
    normalized = re.sub(r"[`*_\[\]<>()]", "", normalized)
    normalized = re.sub(r"[^\w\-\u4e00-\u9fff ]+", "", normalized)
    normalized = re.sub(r"[\s\-]+", "-", normalized).strip("-")
    return normalized


def _heading_slug_map(markdown_file: Path) -> dict[str, list[int]]:
    content = markdown_file.read_text(encoding="utf-8")
    slug_map: dict[str, list[int]] = {}
    for match in HEADING_PATTERN.finditer(content):
        title = match.group(2).strip()
        slug = _slugify_heading(title)
        if not slug:
            continue
        slug_map.setdefault(slug, []).append(content[: match.start()].count("\n") + 1)
    return slug_map


def test_markdown_relative_links_exist() -> None:
    failures: list[str] = []

    for markdown_file in _iter_markdown_files():
        content = markdown_file.read_text(encoding="utf-8")
        for raw_target in LINK_PATTERN.findall(content):
            target = _normalize_target(raw_target)
            if not target or _is_external(target):
                continue
            path_part, _, fragment = target.partition("#")
            resolved = markdown_file if not path_part else _resolve_target(markdown_file, path_part)
            if not resolved.exists():
                relative_source = markdown_file.relative_to(REPO_ROOT)
                failures.append(f"{relative_source}: {target}")
                continue

            if fragment and resolved.suffix.lower() == ".md":
                slug_map = _heading_slug_map(resolved)
                if fragment not in slug_map:
                    relative_source = markdown_file.relative_to(REPO_ROOT)
                    failures.append(f"{relative_source}: missing anchor {target}")

    assert not failures, "Broken markdown links found:\n" + "\n".join(failures)


def test_markdown_heading_slugs_are_unique() -> None:
    failures: list[str] = []

    for markdown_file in _iter_markdown_files():
        slug_map = _heading_slug_map(markdown_file)
        duplicates = {slug: lines for slug, lines in slug_map.items() if len(lines) > 1}
        if duplicates:
            relative_source = markdown_file.relative_to(REPO_ROOT)
            for slug, lines in sorted(duplicates.items()):
                failures.append(
                    f"{relative_source}: duplicate heading slug '{slug}' at lines {lines}"
                )

    assert not failures, "Duplicate markdown heading slugs found:\n" + "\n".join(failures)
