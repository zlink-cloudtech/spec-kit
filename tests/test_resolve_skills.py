"""Tests for scripts/bash/resolve-skills.sh"""
import os
import subprocess
import tempfile
import shutil
import textwrap

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SCRIPT = os.path.join(REPO_ROOT, 'scripts', 'bash', 'resolve-skills.sh')


def run_script(*args, cwd=None):
    """Run resolve-skills.sh with given args, return (stdout, stderr, returncode)."""
    result = subprocess.run(
        ['bash', SCRIPT] + list(args),
        capture_output=True,
        text=True,
        cwd=cwd or REPO_ROOT,
    )
    return result.stdout, result.stderr, result.returncode


class TestGetSkillDirs:
    """Tests for .speckit.yaml configuration loading."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.tmpdir)

    def test_defaults_without_config(self):
        # No adapter files — output should be empty-skills envelope with count=0
        stdout, _, rc = run_script('plan', self.tmpdir)
        assert rc == 0
        assert 'count="0"' in stdout

    def test_custom_scan_dirs(self):
        # Skill in a custom directory listed in .speckit.yaml
        alt_dir = os.path.join(self.tmpdir, 'custom', 'skills', 'my-skill')
        os.makedirs(alt_dir)
        _write_skill_md(alt_dir, 'my-skill')
        _write_adapter(alt_dir, 'my-skill', 'plan', priority=50)

        config = textwrap.dedent("""\
            version: "2.0.0"
            skills:
              scan_dirs:
                - custom/skills/
        """)
        with open(os.path.join(self.tmpdir, '.speckit.yaml'), 'w') as f:
            f.write(config)

        stdout, _, rc = run_script('plan', self.tmpdir)
        assert rc == 0
        assert 'my-skill' in stdout

    def test_version_warning_major_mismatch(self):
        _write_skill_for_phase(self.tmpdir, 'plan')
        config = textwrap.dedent("""\
            version: "99.0.0"
            skills:
              scan_dirs:
                - skills/
        """)
        with open(os.path.join(self.tmpdir, '.speckit.yaml'), 'w') as f:
            f.write(config)

        _, stderr, rc = run_script('plan', self.tmpdir)
        assert rc == 0
        assert 'incompatible' in stderr.lower() or 'Warning' in stderr or 'warning' in stderr.lower()

    def test_version_no_warning_same_major(self):
        _write_skill_for_phase(self.tmpdir, 'plan')
        config = textwrap.dedent("""\
            version: "2.9.9"
            skills:
              scan_dirs:
                - skills/
        """)
        with open(os.path.join(self.tmpdir, '.speckit.yaml'), 'w') as f:
            f.write(config)

        _, stderr, rc = run_script('plan', self.tmpdir)
        assert rc == 0
        assert stderr.strip() == ''


class TestSkillResolution:
    """Integration tests for full skill resolution."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        # Create a standard skill structure
        skill_dir = os.path.join(self.tmpdir, 'skills', 'test-skill')
        os.makedirs(skill_dir)
        _write_skill_md(skill_dir, 'test-skill')
        _write_adapter(skill_dir, 'test-skill', 'plan', priority=100,
                        instructions="## Test Instructions\n- Do something specific")

    def teardown_method(self):
        shutil.rmtree(self.tmpdir)

    def test_phase_match(self):
        stdout, _, rc = run_script('plan', self.tmpdir)
        assert rc == 0
        assert 'test-skill' in stdout

    def test_phase_no_match(self):
        stdout, _, rc = run_script('implement', self.tmpdir)
        assert rc == 0
        assert 'count="0"' in stdout

    def test_instructions_injected(self):
        stdout, _, rc = run_script('plan', self.tmpdir)
        assert rc == 0
        assert '## Test Instructions' in stdout
        assert 'Do something specific' in stdout

    def test_priority_ordering(self):
        skill_dir2 = os.path.join(self.tmpdir, 'skills', 'low-priority-skill')
        os.makedirs(skill_dir2)
        _write_skill_md(skill_dir2, 'low-priority-skill')
        _write_adapter(skill_dir2, 'low-priority-skill', 'plan', priority=50)

        stdout, _, rc = run_script('plan', self.tmpdir)
        assert rc == 0
        # test-skill (priority 100) must appear before low-priority-skill (50)
        assert stdout.index('test-skill') < stdout.index('low-priority-skill')

    def test_missing_adapter_graceful(self):
        # Directory with SKILL.md but no adapter — should be ignored for phase output
        bad_dir = os.path.join(self.tmpdir, 'skills', 'no-adapter')
        os.makedirs(bad_dir)
        _write_skill_md(bad_dir, 'no-adapter')

        stdout, _, rc = run_script('plan', self.tmpdir)
        assert rc == 0
        assert 'test-skill' in stdout

    def test_multi_dir_scanning(self):
        # Create a second skill directory referenced via .speckit.yaml
        vendor_dir = os.path.join(self.tmpdir, 'vendor', 'skills', 'vendor-skill')
        os.makedirs(vendor_dir)
        _write_skill_md(vendor_dir, 'vendor-skill')
        _write_adapter(vendor_dir, 'vendor-skill', 'plan', priority=80)

        config = textwrap.dedent("""\
            version: "2.0.0"
            skills:
              scan_dirs:
                - skills/
                - vendor/skills/
        """)
        with open(os.path.join(self.tmpdir, '.speckit.yaml'), 'w') as f:
            f.write(config)

        stdout, _, rc = run_script('plan', self.tmpdir)
        assert rc == 0
        assert 'test-skill' in stdout
        assert 'vendor-skill' in stdout


class TestListDomain:
    """Tests for the --list-domain command."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.tmpdir)

    def test_lists_skills_without_adapter(self):
        skill_dir = os.path.join(self.tmpdir, 'skills', 'domain-skill')
        os.makedirs(skill_dir)
        _write_skill_md(skill_dir, 'domain-skill',
                        description='A domain-level skill for testing.')
        # No speckit-adapter.yaml

        stdout, _, rc = run_script('--list-domain', self.tmpdir)
        assert rc == 0
        assert 'domain-skill' in stdout
        assert 'A domain-level skill for testing.' in stdout

    def test_excludes_adapter_skills(self):
        # skill with adapter should NOT appear in --list-domain
        adapted_dir = os.path.join(self.tmpdir, 'skills', 'adapted-skill')
        os.makedirs(adapted_dir)
        _write_skill_md(adapted_dir, 'adapted-skill')
        _write_adapter(adapted_dir, 'adapted-skill', 'plan', priority=100)

        stdout, _, rc = run_script('--list-domain', self.tmpdir)
        assert rc == 0
        assert 'adapted-skill' not in stdout

    def test_empty_skills(self):
        stdout, _, rc = run_script('--list-domain', self.tmpdir)
        assert rc == 0
        assert '_No domain skills found' in stdout


class TestNoMatchPhase:
    """Tests for phases with no matching skills."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.tmpdir)

    def test_empty_output_envelope(self):
        stdout, _, rc = run_script('nonexistent-phase', self.tmpdir)
        assert rc == 0
        assert 'count="0"' in stdout
        assert 'No specialist skills' in stdout


class TestLiveRepo:
    """Smoke tests against the actual repository skills."""

    def test_plan_loads_architect(self):
        stdout, _, rc = run_script('plan', REPO_ROOT)
        assert rc == 0
        assert 'speckit-architect' in stdout

    def test_implement_loads_developer(self):
        stdout, _, rc = run_script('implement', REPO_ROOT)
        assert rc == 0
        assert 'speckit-developer' in stdout

    def test_converge_loads_librarian(self):
        stdout, _, rc = run_script('converge', REPO_ROOT)
        assert rc == 0
        assert 'speckit-librarian' in stdout

    def test_tasks_loads_tech_lead_and_developer(self):
        stdout, _, rc = run_script('tasks', REPO_ROOT)
        assert rc == 0
        assert 'speckit-tech-lead' in stdout
        assert 'speckit-developer' in stdout


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _write_skill_md(skill_dir, name, description=''):
    frontmatter = f'---\nname: {name}\n'
    if description:
        frontmatter += f'description: "{description}"\n'
    frontmatter += '---\n\n# {name}\nYou are a test skill.\n'
    with open(os.path.join(skill_dir, 'SKILL.md'), 'w') as f:
        f.write(frontmatter)


def _write_adapter(skill_dir, name, phase, priority=100, instructions=None):
    content = textwrap.dedent(f"""\
        name: {name}
        hooks:
          - phase: {phase}
            priority: {priority}
            context: SKILL.md
    """)
    if instructions:
        content += '    instructions: |\n'
        for line in instructions.splitlines():
            content += f'      {line}\n'
    with open(os.path.join(skill_dir, 'speckit-adapter.yaml'), 'w') as f:
        f.write(content)


def _write_skill_for_phase(root, phase, skill_name='simple-skill', priority=100):
    """Create a minimal skill+adapter pair under root/skills/."""
    skill_dir = os.path.join(root, 'skills', skill_name)
    os.makedirs(skill_dir, exist_ok=True)
    _write_skill_md(skill_dir, skill_name)
    _write_adapter(skill_dir, skill_name, phase, priority)

