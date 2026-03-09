"""
Tests for skills/speckit-architect/SKILL.md and speckit-adapter.yaml diagram strategy.

T008: test_skill_md_structure — SKILL.md frontmatter + Diagram Strategy section
T012: test_adapter_sequence_rule — adapter plan hook contains sequence diagram trigger
T015: test_adapter_er_diagram_rule — adapter plan hook contains ER diagram trigger
T018: test_adapter_state_diagram_rule — adapter plan hook contains state diagram trigger
T021: test_adapter_flowchart_rule — adapter plan hook contains flowchart trigger
T024: test_adapter_class_diagram_rule — adapter plan hook contains class diagram trigger
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
# T008 — SKILL.md structure
# ---------------------------------------------------------------------------


def test_skill_md_structure():
    """T008: SKILL.md has valid frontmatter and Diagram Strategy section (SC-007)."""
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
# T012 — Adapter: sequence diagram trigger rule
# ---------------------------------------------------------------------------


def test_adapter_sequence_rule():
    """T012: adapter plan hook contains sequence diagram trigger rule (SC-005)."""
    instructions = _get_adapter_plan_instructions()

    assert "setup-uml-dir" in instructions, (
        "Adapter plan hook must reference 'setup-uml-dir' script"
    )
    assert "sequenceDiagram" in instructions, (
        "Adapter plan hook must contain 'sequenceDiagram' trigger"
    )
    assert "uml/sequence.md" in instructions, (
        "Adapter plan hook must specify output path 'uml/sequence.md'"
    )
    # MUST obligation near cross-component trigger
    assert re.search(r"must|MUST", instructions), (
        "Adapter plan hook must use MUST/must obligation level for sequence diagram"
    )
    cross_component = re.search(r"cross.component|cross.service", instructions, re.IGNORECASE)
    assert cross_component, (
        "Adapter plan hook must mention 'cross-component' or 'cross-service' trigger condition"
    )
    # FR-011: diagrams must be wrapped in ```mermaid blocks
    assert "```mermaid" in instructions, (
        "Adapter plan hook must instruct agents to wrap diagrams in ```mermaid fenced blocks (FR-011)"
    )


# ---------------------------------------------------------------------------
# T015 — Adapter: ER diagram trigger rule
# ---------------------------------------------------------------------------


def test_adapter_er_diagram_rule():
    """T015: adapter plan hook contains ER diagram trigger rule (SC-005)."""
    instructions = _get_adapter_plan_instructions()

    assert "erDiagram" in instructions, (
        "Adapter plan hook must contain 'erDiagram' trigger"
    )
    assert "data-model.md" in instructions, (
        "Adapter plan hook must reference 'data-model.md' for ER diagram output"
    )
    assert re.search(r"must|MUST", instructions), (
        "Adapter plan hook must use MUST/must obligation level for ER diagram"
    )
    assert re.search(r"persistent|entities", instructions, re.IGNORECASE), (
        "Adapter plan hook must mention 'persistent' or 'entities' for ER trigger"
    )
    # Ordering: erDiagram must appear before stateDiagram-v2
    er_idx = instructions.find("erDiagram")
    state_idx = instructions.find("stateDiagram-v2")
    if state_idx != -1:
        assert er_idx < state_idx, (
            "erDiagram rule must appear before stateDiagram-v2 rule in adapter instructions"
        )


# ---------------------------------------------------------------------------
# T018 — Adapter: state diagram trigger rule
# ---------------------------------------------------------------------------


def test_adapter_state_diagram_rule():
    """T018: adapter plan hook contains state machine trigger rule."""
    instructions = _get_adapter_plan_instructions()

    assert "stateDiagram-v2" in instructions, (
        "Adapter plan hook must contain 'stateDiagram-v2' trigger"
    )
    assert "data-model.md" in instructions, (
        "Adapter plan hook must reference 'data-model.md' for state diagram"
    )
    assert re.search(r"must|MUST", instructions), (
        "Adapter plan hook must use MUST/must obligation level for state diagram"
    )
    assert re.search(r"state|transition", instructions, re.IGNORECASE), (
        "Adapter plan hook must mention 'state' or 'transition' phrasing for state diagram trigger"
    )


# ---------------------------------------------------------------------------
# T021 — Adapter: flowchart trigger rule
# ---------------------------------------------------------------------------


def test_adapter_flowchart_rule():
    """T021: adapter plan hook contains flowchart trigger rule."""
    instructions = _get_adapter_plan_instructions()

    assert "flowchart" in instructions, (
        "Adapter plan hook must contain 'flowchart' trigger"
    )
    assert "uml/flow.md" in instructions, (
        "Adapter plan hook must specify output path 'uml/flow.md'"
    )
    assert re.search(r"should|SHOULD", instructions), (
        "Adapter plan hook must use SHOULD/should obligation level for flowchart"
    )
    assert re.search(r"decision|conditional", instructions, re.IGNORECASE), (
        "Adapter plan hook must mention 'decision' or 'conditional' phrasing for flowchart trigger"
    )


# ---------------------------------------------------------------------------
# T024 — Adapter: class diagram trigger rule
# ---------------------------------------------------------------------------


def test_adapter_class_diagram_rule():
    """T024: adapter plan hook contains class diagram trigger rule."""
    instructions = _get_adapter_plan_instructions()

    assert "classDiagram" in instructions, (
        "Adapter plan hook must contain 'classDiagram' trigger"
    )
    assert "uml/class-diagram.md" in instructions, (
        "Adapter plan hook must specify output path 'uml/class-diagram.md'"
    )
    assert re.search(r"should|SHOULD", instructions), (
        "Adapter plan hook must use SHOULD/should obligation level for class diagram"
    )
    assert re.search(r"inheritance|composition", instructions, re.IGNORECASE), (
        "Adapter plan hook must mention 'inheritance' or 'composition' phrasing for class diagram trigger"
    )
