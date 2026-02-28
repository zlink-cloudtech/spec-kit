"""Tests for scripts/resolve-skills.py"""
import os
import sys
import tempfile
import shutil
import textwrap
import io
from contextlib import redirect_stdout, redirect_stderr

# Add scripts dir to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
import importlib
resolve_skills = importlib.import_module('resolve-skills')


class TestManualParse:
    """Tests for the manual_parse() YAML parser."""

    def test_basic_hook(self):
        text = textwrap.dedent("""\
            name: test-skill
            hooks:
              - phase: plan
                priority: 100
                context: SKILL.md
        """)
        data = resolve_skills.manual_parse(text)
        assert data['name'] == 'test-skill'
        assert len(data['hooks']) == 1
        assert data['hooks'][0]['phase'] == 'plan'
        assert data['hooks'][0]['priority'] == 100
        assert data['hooks'][0]['context'] == 'SKILL.md'

    def test_multiple_hooks(self):
        text = textwrap.dedent("""\
            name: multi-skill
            hooks:
              - phase: tasks
                priority: 90
                context: SKILL.md
              - phase: implement
                priority: 100
                context: SKILL.md
        """)
        data = resolve_skills.manual_parse(text)
        assert len(data['hooks']) == 2
        assert data['hooks'][0]['phase'] == 'tasks'
        assert data['hooks'][1]['phase'] == 'implement'

    def test_instructions_block_scalar(self):
        text = textwrap.dedent("""\
            name: skill-with-instructions
            hooks:
              - phase: plan
                priority: 100
                context: SKILL.md
                instructions: |
                  ## SpecKit Integration
                  - Read system-map.md
                  - Update documentation
        """)
        data = resolve_skills.manual_parse(text)
        assert len(data['hooks']) == 1
        instructions = data['hooks'][0].get('instructions', '')
        assert '## SpecKit Integration' in instructions
        assert 'Read system-map.md' in instructions

    def test_missing_name(self):
        text = textwrap.dedent("""\
            hooks:
              - phase: plan
                priority: 50
                context: SKILL.md
        """)
        data = resolve_skills.manual_parse(text)
        assert 'name' not in data
        assert len(data['hooks']) == 1

    def test_malformed_yaml(self):
        text = "this is not yaml at all\njust random text"
        data = resolve_skills.manual_parse(text)
        assert data['hooks'] == []


class TestGetSkillDirs:
    """Tests for .speckit.yaml configuration loading."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.tmpdir)

    def test_defaults_without_config(self):
        dirs = resolve_skills.get_skill_dirs(self.tmpdir)
        expected_suffixes = ['skills', '.specify/skills', '.github/skills', '.claude/skills']
        for d, suffix in zip(dirs, expected_suffixes):
            assert d.endswith(suffix)

    def test_custom_scan_dirs(self):
        config = textwrap.dedent("""\
            version: "2.0.0"
            skills:
              scan_dirs:
                - custom/skills/
                - vendor/skills/
        """)
        with open(os.path.join(self.tmpdir, '.speckit.yaml'), 'w') as f:
            f.write(config)

        dirs = resolve_skills.get_skill_dirs(self.tmpdir)
        assert len(dirs) == 2
        assert dirs[0].endswith('custom/skills/')
        assert dirs[1].endswith('vendor/skills/')

    def test_version_warning_major_mismatch(self):
        config = textwrap.dedent("""\
            version: "3.0.0"
            skills:
              scan_dirs:
                - skills/
        """)
        with open(os.path.join(self.tmpdir, '.speckit.yaml'), 'w') as f:
            f.write(config)

        stderr = io.StringIO()
        with redirect_stderr(stderr):
            resolve_skills.get_skill_dirs(self.tmpdir)
        assert 'incompatible' in stderr.getvalue().lower() or 'Warning' in stderr.getvalue()

    def test_version_no_warning_same_major(self):
        config = textwrap.dedent("""\
            version: "2.1.0"
            skills:
              scan_dirs:
                - skills/
        """)
        with open(os.path.join(self.tmpdir, '.speckit.yaml'), 'w') as f:
            f.write(config)

        stderr = io.StringIO()
        with redirect_stderr(stderr):
            resolve_skills.get_skill_dirs(self.tmpdir)
        assert stderr.getvalue() == ''


class TestSkillResolution:
    """Integration tests for full skill resolution."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        # Create a skill directory structure
        skill_dir = os.path.join(self.tmpdir, 'skills', 'test-skill')
        os.makedirs(skill_dir)
        # Create SKILL.md
        with open(os.path.join(skill_dir, 'SKILL.md'), 'w') as f:
            f.write("---\nname: test-skill\n---\n\n# Test Skill\nYou are a test skill.\n")
        # Create adapter
        with open(os.path.join(skill_dir, 'speckit-adapter.yaml'), 'w') as f:
            f.write(textwrap.dedent("""\
                name: test-skill
                hooks:
                  - phase: plan
                    priority: 100
                    context: SKILL.md
                    instructions: |
                      ## Test Instructions
                      - Do something specific
            """))

    def teardown_method(self):
        shutil.rmtree(self.tmpdir)

    def test_phase_match(self):
        stdout = io.StringIO()
        sys.argv = ['resolve-skills.py', 'plan', self.tmpdir]
        with redirect_stdout(stdout):
            resolve_skills.main()
        output = stdout.getvalue()
        assert 'test-skill' in output
        assert 'Test Skill' in output

    def test_phase_no_match(self):
        stdout = io.StringIO()
        sys.argv = ['resolve-skills.py', 'implement', self.tmpdir]
        with redirect_stdout(stdout):
            resolve_skills.main()
        assert stdout.getvalue() == ''

    def test_instructions_injected(self):
        stdout = io.StringIO()
        sys.argv = ['resolve-skills.py', 'plan', self.tmpdir]
        with redirect_stdout(stdout):
            resolve_skills.main()
        output = stdout.getvalue()
        assert '## Test Instructions' in output
        assert 'Do something specific' in output

    def test_priority_ordering(self):
        # Create a second skill with lower priority
        skill_dir2 = os.path.join(self.tmpdir, 'skills', 'low-priority-skill')
        os.makedirs(skill_dir2)
        with open(os.path.join(skill_dir2, 'SKILL.md'), 'w') as f:
            f.write("# Low Priority Skill\n")
        with open(os.path.join(skill_dir2, 'speckit-adapter.yaml'), 'w') as f:
            f.write(textwrap.dedent("""\
                name: low-priority-skill
                hooks:
                  - phase: plan
                    priority: 50
                    context: SKILL.md
            """))

        stdout = io.StringIO()
        sys.argv = ['resolve-skills.py', 'plan', self.tmpdir]
        with redirect_stdout(stdout):
            resolve_skills.main()
        output = stdout.getvalue()
        # test-skill (priority 100) should appear before low-priority-skill (50)
        idx_high = output.index('test-skill')
        idx_low = output.index('low-priority-skill')
        assert idx_high < idx_low

    def test_missing_adapter_graceful(self):
        # Create a skill dir without adapter
        bad_dir = os.path.join(self.tmpdir, 'skills', 'no-adapter')
        os.makedirs(bad_dir)
        with open(os.path.join(bad_dir, 'SKILL.md'), 'w') as f:
            f.write("# No Adapter Skill\n")

        stdout = io.StringIO()
        sys.argv = ['resolve-skills.py', 'plan', self.tmpdir]
        with redirect_stdout(stdout):
            resolve_skills.main()
        # Should still work, just finding the valid skill
        assert 'test-skill' in stdout.getvalue()

    def test_multi_dir_scanning(self):
        # Create .speckit.yaml pointing to two dirs
        alt_dir = os.path.join(self.tmpdir, 'vendor', 'skills', 'vendor-skill')
        os.makedirs(alt_dir)
        with open(os.path.join(alt_dir, 'SKILL.md'), 'w') as f:
            f.write("# Vendor Skill\n")
        with open(os.path.join(alt_dir, 'speckit-adapter.yaml'), 'w') as f:
            f.write(textwrap.dedent("""\
                name: vendor-skill
                hooks:
                  - phase: plan
                    priority: 80
                    context: SKILL.md
            """))

        config = textwrap.dedent("""\
            version: "2.0.0"
            skills:
              scan_dirs:
                - skills/
                - vendor/skills/
        """)
        with open(os.path.join(self.tmpdir, '.speckit.yaml'), 'w') as f:
            f.write(config)

        stdout = io.StringIO()
        sys.argv = ['resolve-skills.py', 'plan', self.tmpdir]
        with redirect_stdout(stdout):
            resolve_skills.main()
        output = stdout.getvalue()
        assert 'test-skill' in output
        assert 'vendor-skill' in output
