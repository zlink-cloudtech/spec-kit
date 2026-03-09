"""
Tests for scripts/bash/setup-uml-dir.sh and scripts/powershell/setup-uml-dir.ps1
"""
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
BASH_SCRIPT = REPO_ROOT / "scripts" / "bash" / "setup-uml-dir.sh"
PS1_SCRIPT = REPO_ROOT / "scripts" / "powershell" / "setup-uml-dir.ps1"
PWSH_AVAILABLE = shutil.which("pwsh") is not None


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Bash: scripts/bash/setup-uml-dir.sh
# ---------------------------------------------------------------------------


class TestSetupUmlDirBash:
    """Tests for setup-uml-dir.sh."""

    def test_happy_path_env_var(self, tmp_path):
        """(a) FEATURE_DIR env var set → exits 0, prints absolute uml/ path, dir created."""
        feature_dir = tmp_path / "my-feature"
        feature_dir.mkdir()
        env = {**os.environ, "FEATURE_DIR": str(feature_dir)}
        result = subprocess.run(
            ["bash", str(BASH_SCRIPT)],
            env=env,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstderr: {result.stderr}"
        output = result.stdout.strip()
        assert output.endswith("/uml"), f"Expected output ending in '/uml', got: {output!r}"
        assert Path(output).is_absolute(), f"Expected absolute path, got: {output!r}"
        assert (feature_dir / "uml").is_dir(), "Expected uml/ directory to be created"

    def test_positional_arg_takes_precedence(self, tmp_path):
        """(b) Positional arg $1 takes precedence over FEATURE_DIR env var."""
        positional_dir = tmp_path / "positional-feature"
        env_dir = tmp_path / "env-feature"
        positional_dir.mkdir()
        env_dir.mkdir()
        env = {**os.environ, "FEATURE_DIR": str(env_dir)}
        result = subprocess.run(
            ["bash", str(BASH_SCRIPT), str(positional_dir)],
            env=env,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        output = result.stdout.strip()
        assert str(positional_dir) in output, (
            f"Expected positional dir {positional_dir} in output, got: {output!r}"
        )
        assert (positional_dir / "uml").is_dir(), "Expected positional dir/uml/ to exist"
        assert not (env_dir / "uml").exists(), "env-feature uml/ should NOT be created"

    def test_idempotency(self, tmp_path):
        """(c) Second call exits 0 and prints same path (idempotency)."""
        feature_dir = tmp_path / "idempotent-feature"
        feature_dir.mkdir()
        env = {**os.environ, "FEATURE_DIR": str(feature_dir)}

        result1 = subprocess.run(
            ["bash", str(BASH_SCRIPT)],
            env=env,
            capture_output=True,
            text=True,
        )
        result2 = subprocess.run(
            ["bash", str(BASH_SCRIPT)],
            env=env,
            capture_output=True,
            text=True,
        )
        assert result1.returncode == 0, f"First call failed: {result1.stderr}"
        assert result2.returncode == 0, f"Second call failed: {result2.stderr}"
        assert result1.stdout.strip() == result2.stdout.strip(), (
            f"Output differed: {result1.stdout.strip()!r} vs {result2.stdout.strip()!r}"
        )
        assert (feature_dir / "uml").is_dir()

    def test_missing_feature_dir(self, tmp_path):
        """(d) Missing FEATURE_DIR → exits 1, error written to stderr."""
        env = {k: v for k, v in os.environ.items() if k != "FEATURE_DIR"}
        result = subprocess.run(
            ["bash", str(BASH_SCRIPT)],
            env=env,
            capture_output=True,
            text=True,
            cwd=str(tmp_path),
        )
        assert result.returncode != 0, f"Expected non-zero exit, got 0\nstdout: {result.stdout}"
        assert result.stderr.strip(), f"Expected error message on stderr, got empty"

    def test_feature_dir_is_file(self, tmp_path):
        """(e) FR-012: FEATURE_DIR path exists but is a regular file → exits non-zero, error on stderr."""
        file_path = tmp_path / "not-a-dir"
        file_path.write_text("I am a file, not a directory")
        env = {**os.environ, "FEATURE_DIR": str(file_path)}
        result = subprocess.run(
            ["bash", str(BASH_SCRIPT)],
            env=env,
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0, (
            f"Expected non-zero exit when FEATURE_DIR is a regular file, got 0\nstdout: {result.stdout}"
        )
        assert result.stderr.strip(), "Expected error message on stderr when FEATURE_DIR is a file"


# ---------------------------------------------------------------------------
# PowerShell: scripts/powershell/setup-uml-dir.ps1
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not PWSH_AVAILABLE, reason="pwsh not available")
class TestSetupUmlDirPowerShell:
    """Tests for setup-uml-dir.ps1."""

    def test_happy_path_env_var(self, tmp_path):
        """(a) $env:FEATURE_DIR set → exits 0, prints absolute uml/ path, dir created."""
        feature_dir = tmp_path / "my-feature"
        feature_dir.mkdir()
        env = {**os.environ, "FEATURE_DIR": str(feature_dir)}
        result = subprocess.run(
            ["pwsh", "-NonInteractive", "-File", str(PS1_SCRIPT)],
            env=env,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstderr: {result.stderr}"
        output = result.stdout.strip()
        assert "uml" in output.lower(), f"Expected 'uml' in output, got: {output!r}"
        assert (feature_dir / "uml").is_dir(), "Expected uml/ directory to be created"

    def test_positional_param_takes_precedence(self, tmp_path):
        """(b) -FeatureDir param takes precedence over $env:FEATURE_DIR."""
        positional_dir = tmp_path / "positional-feature"
        env_dir = tmp_path / "env-feature"
        positional_dir.mkdir()
        env_dir.mkdir()
        env = {**os.environ, "FEATURE_DIR": str(env_dir)}
        result = subprocess.run(
            ["pwsh", "-NonInteractive", "-File", str(PS1_SCRIPT), "-FeatureDir", str(positional_dir)],
            env=env,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        output = result.stdout.strip()
        assert str(positional_dir) in output, (
            f"Expected positional dir in output, got: {output!r}"
        )
        assert (positional_dir / "uml").is_dir()
        assert not (env_dir / "uml").exists()

    def test_idempotency(self, tmp_path):
        """(c) Second call exits 0 and prints same path."""
        feature_dir = tmp_path / "idempotent-feature"
        feature_dir.mkdir()
        env = {**os.environ, "FEATURE_DIR": str(feature_dir)}

        result1 = subprocess.run(
            ["pwsh", "-NonInteractive", "-File", str(PS1_SCRIPT)],
            env=env,
            capture_output=True,
            text=True,
        )
        result2 = subprocess.run(
            ["pwsh", "-NonInteractive", "-File", str(PS1_SCRIPT)],
            env=env,
            capture_output=True,
            text=True,
        )
        assert result1.returncode == 0
        assert result2.returncode == 0
        assert result1.stdout.strip() == result2.stdout.strip()
        assert (feature_dir / "uml").is_dir()

    def test_missing_feature_dir(self, tmp_path):
        """(d) Missing FEATURE_DIR → exits 1, error to stderr."""
        env = {k: v for k, v in os.environ.items() if k != "FEATURE_DIR"}
        result = subprocess.run(
            ["pwsh", "-NonInteractive", "-File", str(PS1_SCRIPT)],
            env=env,
            capture_output=True,
            text=True,
            cwd=str(tmp_path),
        )
        assert result.returncode != 0, f"Expected non-zero exit\nstdout: {result.stdout}"
        assert result.stderr.strip() or result.stdout.strip(), "Expected error message output"
