import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from specify_cli.skills import Skills

class TestSkills(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.skills_dir = self.test_dir / "skills"
        self.skills_dir.mkdir()
        self.templates_dir = self.test_dir / "templates" / "instructions"
        self.templates_dir.mkdir(parents=True)
        
        # Create a dummy skill
        (self.skills_dir / "test-skill").mkdir()
        (self.skills_dir / "test-skill" / "SKILL.md").write_text(
            "---\nname: Test Skill\ndescription: A test skill\n---\nContent", encoding='utf-8'
        )
        
        # Create a dummy template
        (self.templates_dir / "speckit-skills.instructions.md").write_text(
            "# Header\n\n{SKILLS_LIST}", encoding='utf-8'
        )
        
        self.skills = Skills(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_generate_protocol_content(self):
        content = self.skills.generate_protocol_content()
        self.assertIn("# Header", content)
        self.assertIn("<available_skills>", content)
        self.assertIn("<name>Test Skill</name>", content)
        self.assertIn("<description>A test skill</description>", content)
        # Check for location tag with workspaceFolder variable
        self.assertIn("<location>${workspaceFolder}/skills/test-skill/SKILL.md</location>", content)

    def test_install_creates_file(self):
        output_file = self.test_dir / ".github" / "instructions" / "speckit-skills.instructions.md"
        self.skills.install(path=output_file, format="copilot-instructions")
        self.assertTrue(output_file.exists())
        content = output_file.read_text(encoding='utf-8')
        self.assertIn("<available_skills>", content)
        self.assertIn("<name>Test Skill</name>", content)
        self.assertIn("name: Spec Kit Skills Protocol", content) # Check for copilot frontmatter

if __name__ == '__main__':
    unittest.main()
