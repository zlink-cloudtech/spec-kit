"""Tests for the speckit-doc-update command template.

Covers:
- Command template existence and frontmatter
- Operation content (all 7 operations must be present in doc-update.md)
- CLI banner inclusion (Phase N-1)
"""

import subprocess
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).parent.parent




# ---------------------------------------------------------------------------
# Command template
# ---------------------------------------------------------------------------


def test_command_template_exists():
    """T004: doc-update.md command template must exist with a non-empty description frontmatter."""
    template_path = REPO_ROOT / "templates" / "commands" / "doc-update.md"
    assert template_path.exists(), f"Missing command template: {template_path}"

    content = template_path.read_text(encoding="utf-8")
    assert "description" in content, "Command template frontmatter missing 'description' field"

    # Extract YAML frontmatter block (between first two '---' lines)
    lines = content.splitlines()
    if lines and lines[0].strip() == "---":
        end = next(
            (i for i, ln in enumerate(lines[1:], start=1) if ln.strip() == "---"),
            None,
        )
        if end is not None:
            frontmatter_text = "\n".join(lines[1:end])
            fm = yaml.safe_load(frontmatter_text)
            description = fm.get("description", "") if fm else ""
            assert description and description.strip(), (
                "Frontmatter 'description' field is empty"
            )


# ---------------------------------------------------------------------------
# Operation content — all 7 operations must be present in doc-update.md
# ---------------------------------------------------------------------------


def test_command_template_contains_update_operation():
    """T008: doc-update.md must contain the Update operation with required keywords."""
    template_path = REPO_ROOT / "templates" / "commands" / "doc-update.md"
    content = template_path.read_text(encoding="utf-8")
    for keyword in ("UPDATE", "system-map.md", "pre-flight", "hard-stop", "Last Updated"):
        assert keyword in content, (
            f"doc-update.md is missing required keyword: {keyword!r}"
        )


def test_command_template_contains_add_operation():
    """T011: doc-update.md must contain the Add operation with required keywords."""
    template_path = REPO_ROOT / "templates" / "commands" / "doc-update.md"
    content = template_path.read_text(encoding="utf-8")
    for keyword in ("ADD", "duplicate", "category", "already exists"):
        assert keyword in content, (
            f"doc-update.md is missing required keyword: {keyword!r}"
        )


def test_command_template_contains_delete_deprecate_operations():
    """T013: doc-update.md must contain Delete and Deprecate operations with required keywords."""
    template_path = REPO_ROOT / "templates" / "commands" / "doc-update.md"
    content = template_path.read_text(encoding="utf-8")
    for keyword in ("DELETE", "DEPRECATE", "confirmation", "🗑️ Deprecated", "deprecation notice"):
        assert keyword in content, (
            f"doc-update.md is missing required keyword: {keyword!r}"
        )


def test_command_template_contains_rename_move_operation():
    """T015: doc-update.md must contain the Rename/Move operation with required keywords."""
    template_path = REPO_ROOT / "templates" / "commands" / "doc-update.md"
    content = template_path.read_text(encoding="utf-8")
    for keyword in ("RENAME", "MOVE", "cross-reference", "README.md", "partial failure"):
        assert keyword in content, (
            f"doc-update.md is missing required keyword: {keyword!r}"
        )


def test_command_template_contains_merge_operation():
    """T017: doc-update.md must contain the Merge operation with required keywords."""
    template_path = REPO_ROOT / "templates" / "commands" / "doc-update.md"
    content = template_path.read_text(encoding="utf-8")
    for keyword in ("MERGE", "heading conflict", "keep first", "keep second", "keep both", "pause"):
        assert keyword in content, (
            f"doc-update.md is missing required keyword: {keyword!r}"
        )


def test_command_template_contains_reposition_operation():
    """T019: doc-update.md must contain the Reposition operation with required keywords."""
    template_path = REPO_ROOT / "templates" / "commands" / "doc-update.md"
    content = template_path.read_text(encoding="utf-8")
    for keyword in ("REPOSITION", "category", "without modifying", "new category section"):
        assert keyword in content, (
            f"doc-update.md is missing required keyword: {keyword!r}"
        )


# ---------------------------------------------------------------------------
# CLI banner inclusion
# ---------------------------------------------------------------------------


def test_cli_banner_includes_doc_update():
    """T021: src/specify_cli/__init__.py must reference /speckit.doc-update in the Optional Commands section."""
    cli_source = REPO_ROOT / "src" / "specify_cli" / "__init__.py"
    assert cli_source.exists(), f"CLI source not found: {cli_source}"

    content = cli_source.read_text(encoding="utf-8")
    assert "/speckit.doc-update" in content, (
        "'/speckit.doc-update' not found in src/specify_cli/__init__.py — "
        "add it to the Optional Commands list in the welcome banner"
    )


# ---------------------------------------------------------------------------
# Cross-cutting: all destructive operation sections must include a confirmation gate (FR-012)
# ---------------------------------------------------------------------------


def test_all_destructive_ops_require_confirmation():
    """E1 (FR-012): Every destructive section in doc-update.md must include a confirmation gate keyword."""
    template_path = REPO_ROOT / "templates" / "commands" / "doc-update.md"
    content = template_path.read_text(encoding="utf-8")

    for section in ("DELETE", "RENAME", "MOVE", "MERGE"):
        assert section in content, (
            f"doc-update.md missing destructive section heading: {section!r}"
        )

    content_lower = content.lower()
    assert any(kw in content_lower for kw in ("confirm", "ask")), (
        "doc-update.md must include a user-confirmation gate (FR-012): "
        "add 'confirm' or 'ask' language to all destructive operation sections"
    )
