"""
Tests for skills/speckit-architect/SKILL.md and speckit-adapter.yaml diagram strategy.
"""
import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).parent.parent
SKILL_MD = REPO_ROOT / "skills" / "speckit-architect" / "SKILL.md"
ADAPTER_YAML = REPO_ROOT / "skills" / "speckit-architect" / "speckit-adapter.yaml"

FIVE_DIAGRAM_TYPES = [
    "sequenceDiagram",
    "erDiagram",
    "stateDiagram-v2",
    "flowchart",
    "classDiagram",
]


def _parse_skill_md(path: Path):
    """Return (frontmatter_dict, body_text) from a skill markdown file."""
    content = path.read_text()
    # Strip outer markdown code fences if present (some files wrap content)
    stripped = content.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        # Remove first and last fence line
        stripped = "\n".join(lines[1:-1])

    # Extract YAML frontmatter between --- delimiters
    if stripped.startswith("---"):
        parts = stripped.split("---", 2)
        if len(parts) >= 3:
            fm = yaml.safe_load(parts[1])
            body = parts[2]
            return fm, body

    return {}, stripped


def _get_adapter_plan_instructions() -> str:
    """Return the plan hook instructions text from speckit-adapter.yaml."""
    content = ADAPTER_YAML.read_text()
    # Strip outer markdown fences if present
    stripped = content.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        stripped = "\n".join(lines[1:-1])

    data = yaml.safe_load(stripped)
    hooks = data.get("hooks", [])
    for hook in hooks:
        if hook.get("phase") == "plan":
            return hook.get("instructions", "")
    pytest.fail("No 'plan' hook found in speckit-adapter.yaml")


# ---------------------------------------------------------------------------
# SKILL.md structure
# ---------------------------------------------------------------------------


def test_skill_md_structure():
    """SKILL.md has valid frontmatter and Diagram Strategy section."""
    fm, body = _parse_skill_md(SKILL_MD)

    # Frontmatter checks
    assert "name" in fm, "SKILL.md frontmatter missing 'name' field"
    assert fm["name"], "SKILL.md frontmatter 'name' is empty"
    assert "description" in fm, "SKILL.md frontmatter missing 'description' field"
    assert fm["description"], "SKILL.md frontmatter 'description' is empty"

    # Body must contain Diagram Strategy section
    assert "## Diagram Strategy" in body, "SKILL.md body missing '## Diagram Strategy' section"

    # All 5 diagram types must appear
    for diagram_type in FIVE_DIAGRAM_TYPES:
        assert diagram_type in body, f"SKILL.md missing diagram type: {diagram_type}"

    # PlantUML must appear alongside PROHIBITED
    plantuml_idx = body.find("PlantUML")
    assert plantuml_idx != -1, "SKILL.md must mention 'PlantUML'"
    # PROHIBITED should appear near PlantUML (within 200 chars)
    vicinity = body[max(0, plantuml_idx - 50) : plantuml_idx + 200]
    assert "PROHIBITED" in vicinity, (
        f"'PROHIBITED' not found near 'PlantUML' in SKILL.md. Context: {vicinity!r}"
    )

    # No inline Mermaid example blocks inside Diagram Strategy section
    # Extract Diagram Strategy section
    ds_match = re.search(r"## Diagram Strategy(.+?)(?=\n## |\Z)", body, re.DOTALL)
    assert ds_match, "Could not extract ## Diagram Strategy section body"
    ds_body = ds_match.group(1)
    assert "```mermaid" not in ds_body, (
        "Diagram Strategy section must NOT contain inline ```mermaid example blocks"
    )


# ---------------------------------------------------------------------------
# Adapter: diagram rules are delegated to SKILL.md (not duplicated in adapter)
# ---------------------------------------------------------------------------


def test_adapter_delegates_diagrams_to_skill():
    """Adapter plan hook delegates diagram decisions to SKILL.md Diagram Matrix."""
    instructions = _get_adapter_plan_instructions()

    # The adapter must reference SKILL.md for diagram strategy
    assert re.search(r"SKILL\.md", instructions), (
        "Adapter plan hook must reference SKILL.md for diagram decisions"
    )
    assert re.search(r"[Dd]iagram\s+[Mm]atrix|Diagram Matrix", instructions), (
        "Adapter plan hook must reference the 'Diagram Matrix' in SKILL.md"
    )

    # Specific diagram types must NOT be duplicated in the adapter —
    # they live exclusively in SKILL.md
    for diagram_type in FIVE_DIAGRAM_TYPES:
        assert diagram_type not in instructions, (
            f"Adapter plan hook must NOT duplicate diagram type '{diagram_type}' "
            f"— diagram rules belong exclusively in SKILL.md"
        )


def test_adapter_sequence_rule():
    """Sequence diagram rules live in SKILL.md, not in the adapter."""
    instructions = _get_adapter_plan_instructions()
    assert "sequenceDiagram" not in instructions, (
        "sequenceDiagram trigger must not be duplicated in the adapter hook"
    )


def test_adapter_er_diagram_rule():
    """ER diagram rules live in SKILL.md, not in the adapter."""
    instructions = _get_adapter_plan_instructions()
    assert "erDiagram" not in instructions, (
        "erDiagram trigger must not be duplicated in the adapter hook"
    )


def test_adapter_state_diagram_rule():
    """State diagram rules live in SKILL.md, not in the adapter."""
    instructions = _get_adapter_plan_instructions()
    assert "stateDiagram-v2" not in instructions, (
        "stateDiagram-v2 trigger must not be duplicated in the adapter hook"
    )


def test_adapter_flowchart_rule():
    """Flowchart rules live in SKILL.md, not in the adapter."""
    instructions = _get_adapter_plan_instructions()
    assert "flowchart" not in instructions, (
        "flowchart trigger must not be duplicated in the adapter hook"
    )


def test_adapter_class_diagram_rule():
    """Class diagram rules live in SKILL.md, not in the adapter."""
    instructions = _get_adapter_plan_instructions()
    assert "classDiagram" not in instructions, (
        "classDiagram trigger must not be duplicated in the adapter hook"
    )
