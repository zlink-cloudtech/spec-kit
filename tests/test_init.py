"""
Tests for ensure_system_map_from_template(), ensure_speckit_config_from_template(), and init().

Coverage:
  - US1: System map created on init (happy path + tracker protocol + parent dirs)
  - US2: Existing system map preserved on reinit (idempotent / skip)
  - US3: Missing-template and IO-error paths for system map (silent no-op without tracker)
  - US4: Full mirror of US1–US3 coverage for speckit config
  - Integration: init() orchestrates both helpers; memory.system_map path is consistent

Ref: specs/010-system-map-no-init/plan.md § Test Design
"""

import shutil
from pathlib import Path
from unittest.mock import ANY, MagicMock, patch

import pytest
import yaml

# ---------------------------------------------------------------------------
# Module-level constants — real repo templates are used as fixture sources to
# avoid content drift between tests and production code (FR-008, FR-009).
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent
SYSTEM_MAP_TEMPLATE_SRC = REPO_ROOT / "templates" / "system-map-template.md"
SPECKIT_CONFIG_TEMPLATE_SRC = REPO_ROOT / "templates" / "speckit-config-template.yaml"
CONSTITUTION_TEMPLATE_SRC = REPO_ROOT / "templates" / "constitution-template.md"

# ---------------------------------------------------------------------------
# Import functions under test
# ---------------------------------------------------------------------------

from specify_cli import (  # noqa: E402
    ensure_system_map_from_template,
    ensure_speckit_config_from_template,
    init,
)


# ---------------------------------------------------------------------------
# Shared fixture helper
# ---------------------------------------------------------------------------

def _setup_project(
    tmp_path: Path,
    *,
    with_system_map_template: bool = True,
    with_speckit_config_template: bool = True,
) -> Path:
    """Create an isolated project directory with .specify/templates/ populated.

    Parameters
    ----------
    tmp_path:
        Pytest-provided temporary directory (isolated per test).
    with_system_map_template:
        When True, copy the real system-map-template.md into the project's
        templates directory so the function under test can find it.
    with_speckit_config_template:
        When True, copy the real speckit-config-template.yaml into the
        project's templates directory.

    Returns
    -------
    Path
        The project root (``tmp_path`` itself), ready for use as
        ``project_path`` in calls to the functions under test.
    """
    tmpl_dir = tmp_path / ".specify" / "templates"
    tmpl_dir.mkdir(parents=True)
    if with_system_map_template:
        shutil.copy(SYSTEM_MAP_TEMPLATE_SRC, tmpl_dir / "system-map-template.md")
    if with_speckit_config_template:
        shutil.copy(SPECKIT_CONFIG_TEMPLATE_SRC, tmpl_dir / "speckit-config-template.yaml")
    return tmp_path


# ---------------------------------------------------------------------------
# Integration test helper (Phase 7)
# ---------------------------------------------------------------------------

def _fake_download_and_extract(
    project_path: Path,
    ai_assistant: str,
    script_type: str,
    is_current_dir: bool = False,
    *,
    verbose: bool = True,
    tracker=None,
    client=None,
    debug: bool = False,
    github_token=None,
    template_url=None,
) -> None:
    """Fake download: copies real templates into project_path/.specify/templates/."""
    tmpl_dir = project_path / ".specify" / "templates"
    tmpl_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(SYSTEM_MAP_TEMPLATE_SRC, tmpl_dir / "system-map-template.md")
    shutil.copy(SPECKIT_CONFIG_TEMPLATE_SRC, tmpl_dir / "speckit-config-template.yaml")
    shutil.copy(CONSTITUTION_TEMPLATE_SRC, tmpl_dir / "constitution-template.md")
    if tracker:
        tracker.add("fetch", "Download template")
        tracker.complete("fetch", "mock")
        tracker.add("download", "Download template")
        tracker.complete("download", "mock")
        tracker.add("extract", "Extract template")
        tracker.complete("extract", "mock")


# ===========================================================================
# Phase 3 — US1: System Map happy path (T004-T008)
# ===========================================================================


def test_system_map_happy_path_with_tracker(tmp_path):
    """FR-001, FR-010: happy path with tracker — file created, add+complete called once."""
    project_dir = _setup_project(tmp_path)
    tracker = MagicMock()
    ensure_system_map_from_template(project_dir, tracker=tracker)
    memory_file = project_dir / ".specify" / "memory" / "system-map.md"
    assert memory_file.exists()
    tracker.add.assert_called_once_with("system-map", ANY)
    tracker.complete.assert_called_once()


def test_system_map_happy_path_without_tracker(tmp_path):
    """FR-001, FR-005: happy path without tracker — file created, no exception raised."""
    project_dir = _setup_project(tmp_path)
    ensure_system_map_from_template(project_dir, tracker=None)
    memory_file = project_dir / ".specify" / "memory" / "system-map.md"
    assert memory_file.exists()


def test_system_map_content_matches_template(tmp_path):
    """FR-001: created file content equals the real template source content."""
    project_dir = _setup_project(tmp_path)
    ensure_system_map_from_template(project_dir, tracker=None)
    memory_file = project_dir / ".specify" / "memory" / "system-map.md"
    assert memory_file.read_text() == SYSTEM_MAP_TEMPLATE_SRC.read_text()


def test_system_map_creates_parent_directories(tmp_path):
    """US-1 AC-3: .specify/memory/ is absent before call; created by the function."""
    project_dir = _setup_project(tmp_path)
    # Verify the memory directory does not yet exist
    assert not (project_dir / ".specify" / "memory").exists()
    ensure_system_map_from_template(project_dir, tracker=MagicMock())
    assert (project_dir / ".specify" / "memory" / "system-map.md").exists()


def test_system_map_tracker_add_called_first(tmp_path):
    """FR-010: tracker.add must appear before tracker.complete in the call list."""
    project_dir = _setup_project(tmp_path)
    tracker = MagicMock()
    ensure_system_map_from_template(project_dir, tracker=tracker)
    add_idx = next(
        (i for i, c in enumerate(tracker.method_calls) if c[0] == "add"),
        None,
    )
    complete_idx = next(
        (i for i, c in enumerate(tracker.method_calls) if c[0] == "complete"),
        None,
    )
    assert add_idx is not None, "tracker.add was never called"
    assert complete_idx is not None, "tracker.complete was never called"
    assert add_idx < complete_idx, "tracker.add must be called before tracker.complete"


# ===========================================================================
# Phase 4 — US2: System Map skip/idempotent (T010-T012)
# ===========================================================================


def test_system_map_skip_when_exists_with_tracker(tmp_path):
    """FR-002: pre-existing memory file is preserved; tracker.skip called once."""
    project_dir = _setup_project(tmp_path)
    memory_dir = project_dir / ".specify" / "memory"
    memory_dir.mkdir(parents=True)
    memory_file = memory_dir / "system-map.md"
    original_content = "PRE-EXISTING SYSTEM MAP CONTENT"
    memory_file.write_text(original_content)
    tracker = MagicMock()
    ensure_system_map_from_template(project_dir, tracker=tracker)
    assert memory_file.read_text() == original_content
    tracker.skip.assert_called_once_with("system-map", ANY)


def test_system_map_skip_when_exists_without_tracker(tmp_path):
    """FR-002, FR-005: pre-existing file unchanged; no tracker, no exception."""
    project_dir = _setup_project(tmp_path)
    memory_dir = project_dir / ".specify" / "memory"
    memory_dir.mkdir(parents=True)
    memory_file = memory_dir / "system-map.md"
    original_content = "PRE-EXISTING SYSTEM MAP CONTENT"
    memory_file.write_text(original_content)
    ensure_system_map_from_template(project_dir, tracker=None)
    assert memory_file.read_text() == original_content


def test_system_map_skip_preserves_custom_content(tmp_path):
    """US-2 AC-1: unique marker in existing file is still present after call."""
    project_dir = _setup_project(tmp_path)
    memory_dir = project_dir / ".specify" / "memory"
    memory_dir.mkdir(parents=True)
    memory_file = memory_dir / "system-map.md"
    memory_file.write_text("CUSTOM_MARKER_DO_NOT_OVERWRITE")
    tracker = MagicMock()
    ensure_system_map_from_template(project_dir, tracker=tracker)
    assert "CUSTOM_MARKER_DO_NOT_OVERWRITE" in memory_file.read_text()


# ===========================================================================
# Phase 5 — US3: System Map missing-template and IO-error (T014-T017)
# ===========================================================================


def test_system_map_missing_template_with_tracker(tmp_path):
    """FR-003: no template present → no memory file created, tracker.error called."""
    project_dir = _setup_project(tmp_path, with_system_map_template=False)
    tracker = MagicMock()
    ensure_system_map_from_template(project_dir, tracker=tracker)
    memory_file = project_dir / ".specify" / "memory" / "system-map.md"
    assert not memory_file.exists()
    tracker.error.assert_called_once_with("system-map", ANY)


def test_system_map_missing_template_without_tracker(tmp_path, capsys):
    """FR-003, FR-005: no template, no tracker → no file, no exception, no output."""
    project_dir = _setup_project(tmp_path, with_system_map_template=False)
    ensure_system_map_from_template(project_dir, tracker=None)
    memory_file = project_dir / ".specify" / "memory" / "system-map.md"
    assert not memory_file.exists()
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_system_map_io_error_with_tracker(tmp_path):
    """FR-004: shutil.copy2 raises OSError → tracker.error called, no exception raised."""
    project_dir = _setup_project(tmp_path)
    tracker = MagicMock()
    with patch("specify_cli.shutil.copy2", side_effect=OSError("permission denied")):
        ensure_system_map_from_template(project_dir, tracker=tracker)
    tracker.error.assert_called_once_with("system-map", ANY)


def test_system_map_io_error_without_tracker(tmp_path, capsys):
    """FR-004, FR-005: copy2 raises OSError, no tracker → silent no-op, no exception."""
    project_dir = _setup_project(tmp_path)
    with patch("specify_cli.shutil.copy2", side_effect=OSError("permission denied")):
        ensure_system_map_from_template(project_dir, tracker=None)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


# ===========================================================================
# Phase 6 — US4: SpecKit Config — full mirror (T021-T030)
# ===========================================================================


def test_speckit_config_happy_path_with_tracker(tmp_path):
    """FR-006: happy path with tracker — .speckit.yaml created, add+complete called once."""
    project_dir = _setup_project(tmp_path)
    tracker = MagicMock()
    ensure_speckit_config_from_template(project_dir, tracker=tracker)
    config_file = project_dir / ".speckit.yaml"
    assert config_file.exists()
    tracker.add.assert_called_once_with("speckit-config", ANY)
    tracker.complete.assert_called_once()


def test_speckit_config_happy_path_without_tracker(tmp_path):
    """FR-006, FR-005: happy path without tracker — .speckit.yaml created, no exception."""
    project_dir = _setup_project(tmp_path)
    ensure_speckit_config_from_template(project_dir, tracker=None)
    assert (project_dir / ".speckit.yaml").exists()


def test_speckit_config_skills_and_memory_fields(tmp_path):
    """FR-011: parsed YAML has skills.scan_dirs (non-empty) and memory.system_map path."""
    project_dir = _setup_project(tmp_path)
    ensure_speckit_config_from_template(project_dir, tracker=None)
    config_file = project_dir / ".speckit.yaml"
    data = yaml.safe_load(config_file.read_text())
    assert isinstance(data["skills"]["scan_dirs"], list)
    assert len(data["skills"]["scan_dirs"]) > 0
    assert data["memory"]["system_map"] == ".specify/memory/system-map.md"


def test_speckit_config_skip_when_exists_with_tracker(tmp_path):
    """FR-006: pre-existing .speckit.yaml preserved; tracker.skip called once."""
    project_dir = _setup_project(tmp_path)
    config_file = project_dir / ".speckit.yaml"
    original_content = "# Custom speckit config\nversion: custom"
    config_file.write_text(original_content)
    tracker = MagicMock()
    ensure_speckit_config_from_template(project_dir, tracker=tracker)
    assert config_file.read_text() == original_content
    tracker.skip.assert_called_once_with("speckit-config", ANY)


def test_speckit_config_skip_when_exists_without_tracker(tmp_path):
    """FR-006, FR-005: pre-existing .speckit.yaml unchanged; no tracker, no exception."""
    project_dir = _setup_project(tmp_path)
    config_file = project_dir / ".speckit.yaml"
    original_content = "# Custom speckit config\nversion: custom"
    config_file.write_text(original_content)
    ensure_speckit_config_from_template(project_dir, tracker=None)
    assert config_file.read_text() == original_content


def test_speckit_config_missing_template_with_tracker(tmp_path):
    """FR-006: no template present → no .speckit.yaml, tracker.error called."""
    project_dir = _setup_project(tmp_path, with_speckit_config_template=False)
    tracker = MagicMock()
    ensure_speckit_config_from_template(project_dir, tracker=tracker)
    assert not (project_dir / ".speckit.yaml").exists()
    tracker.error.assert_called_once_with("speckit-config", ANY)


def test_speckit_config_missing_template_without_tracker(tmp_path, capsys):
    """FR-006, FR-005: no template, no tracker → no file, no exception, no output."""
    project_dir = _setup_project(tmp_path, with_speckit_config_template=False)
    ensure_speckit_config_from_template(project_dir, tracker=None)
    assert not (project_dir / ".speckit.yaml").exists()
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_speckit_config_io_error_with_tracker(tmp_path):
    """FR-006: copy2 raises OSError → tracker.error called, no exception raised."""
    project_dir = _setup_project(tmp_path)
    tracker = MagicMock()
    with patch("specify_cli.shutil.copy2", side_effect=OSError("permission denied")):
        ensure_speckit_config_from_template(project_dir, tracker=tracker)
    tracker.error.assert_called_once_with("speckit-config", ANY)


def test_speckit_config_io_error_without_tracker(tmp_path, capsys):
    """FR-006, FR-005: copy2 raises OSError, no tracker → silent no-op, no exception."""
    project_dir = _setup_project(tmp_path)
    with patch("specify_cli.shutil.copy2", side_effect=OSError("permission denied")):
        ensure_speckit_config_from_template(project_dir, tracker=None)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_speckit_config_tracker_add_called_first(tmp_path):
    """FR-012: tracker.add("speckit-config") must appear before tracker.complete."""
    project_dir = _setup_project(tmp_path)
    tracker = MagicMock()
    ensure_speckit_config_from_template(project_dir, tracker=tracker)
    add_idx = next(
        (i for i, c in enumerate(tracker.method_calls) if c[0] == "add"),
        None,
    )
    complete_idx = next(
        (i for i, c in enumerate(tracker.method_calls) if c[0] == "complete"),
        None,
    )
    assert add_idx is not None, "tracker.add was never called"
    assert complete_idx is not None, "tracker.complete was never called"
    assert add_idx < complete_idx, "tracker.add must be called before tracker.complete"


# ===========================================================================
# Phase 7 — Integration: init() orchestrates both helpers (T034-T035)
# ===========================================================================


def test_init_creates_system_map_and_speckit_config(tmp_path, monkeypatch):
    """FR-007, SC-003: init() in tmp_path creates both memory/system-map.md and .speckit.yaml."""
    monkeypatch.chdir(tmp_path)
    with patch(
        "specify_cli.download_and_extract_template",
        side_effect=_fake_download_and_extract,
    ):
        init(
            project_name=None,
            here=True,
            force=True,
            no_git=True,
            ignore_agent_tools=True,
            ai_assistant="copilot",
            script_type="sh",
            skip_tls=False,
            debug=False,
            github_token=None,
            template_url=None,
        )
    assert (tmp_path / ".specify" / "memory" / "system-map.md").exists()
    assert (tmp_path / ".speckit.yaml").exists()


def test_init_memory_system_map_path_consistency(tmp_path, monkeypatch):
    """FR-007, SC-006: memory.system_map in .speckit.yaml matches the actual file path."""
    monkeypatch.chdir(tmp_path)
    with patch(
        "specify_cli.download_and_extract_template",
        side_effect=_fake_download_and_extract,
    ):
        init(
            project_name=None,
            here=True,
            force=True,
            no_git=True,
            ignore_agent_tools=True,
            ai_assistant="copilot",
            script_type="sh",
            skip_tls=False,
            debug=False,
            github_token=None,
            template_url=None,
        )
    config_file = tmp_path / ".speckit.yaml"
    data = yaml.safe_load(config_file.read_text())
    assert data["memory"]["system_map"] == ".specify/memory/system-map.md"
