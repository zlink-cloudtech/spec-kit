import os
import re
import sys
from pathlib import Path
from typing import Dict, Tuple, Optional

class Skills:
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.skills_dir = workspace_root / "skills"
        
    def _parse_frontmatter(self, content: str) -> Tuple[Dict[str, str], str]:
        """
        Simple frontmatter parser.
        Returns a dict of metadata and the content body.
        """
        if not content.startswith("---"):
            return {}, content
        
        parts = re.split(r'^---$', content, maxsplit=2, flags=re.MULTILINE)
        if len(parts) < 3:
            return {}, content
        
        frontmatter_raw = parts[1]
        body = parts[2].strip()
        
        metadata = {}
        for line in frontmatter_raw.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()
                
        return metadata, body

    def _generate_skills_xml(self) -> str:
        if not self.skills_dir.exists():
            return ""

        xml_content = ["<available_skills>"]
        skills_found = False
        
        # Sort for deterministic output
        for skill_dir in sorted(self.skills_dir.iterdir()):
            if skill_dir.is_dir():
                skill_file = skill_dir / "SKILL.md"
                if skill_file.exists():
                    skills_found = True
                    
                    try:
                        content = skill_file.read_text(encoding='utf-8')
                        metadata, _ = self._parse_frontmatter(content)
                        
                        name = metadata.get('name', skill_dir.name)
                        description = metadata.get('description', '')
                        relative_path = skill_file.relative_to(self.workspace_root).as_posix()
                        location = f"${{workspaceFolder}}/{relative_path}"
                        
                        xml_content.append("  <skill>")
                        xml_content.append(f"    <name>{name}</name>")
                        if description:
                            xml_content.append(f"    <description>{description}</description>")
                        xml_content.append(f"    <location>{location}</location>")
                        xml_content.append("  </skill>")
                        
                    except Exception as e:
                        print(f"Error processing {skill_file}: {e}", file=sys.stderr)

        xml_content.append("</available_skills>")

        if skills_found:
            return "\n".join(xml_content)
        return ""

    def generate_prompt_content(self) -> str:
        skills_xml = self._generate_skills_xml()
        if not skills_xml:
            return ""

        prompt_content = []
        
        prompt_content.append("# Agent Skills Configuration")
        prompt_content.append("")
        prompt_content.append("You have access to a library of specialized skills defined in this workspace. These skills provide specific workflows, instructions, and strategies for complex tasks.")
        prompt_content.append("")
        prompt_content.append("## Core Directive")
        prompt_content.append("You MUST prioritize using these skills over your general knowledge whenever they are relevant to the user's request. Skills represent the \"gold standard\" for how tasks should be performed in this project.")
        prompt_content.append("")
        prompt_content.append("## Skill Usage Protocol")
        prompt_content.append("")
        prompt_content.append("1. **Discovery**: When you receive a task, first check the `<available_skills>` list below.")
        prompt_content.append("2. **Activation**: If a skill's `<description>` matches the task or seems relevant, you MUST read the skill definition file at the provided `<location>`.")
        prompt_content.append("3. **Execution**: Follow the instructions in the skill file. Prioritize the skill's specific strategies over your general knowledge.")
        prompt_content.append("")
        prompt_content.append(skills_xml)

        return "\n".join(prompt_content)

    def _generate_skills_protocol_content(self) -> str:
        template_path = self.workspace_root / "templates" / "instructions" / "speckit-skills.instructions.md"
        if not template_path.exists():
            # Try .specify/templates (for release packages)
            template_path = self.workspace_root / ".specify" / "templates" / "instructions" / "speckit-skills.instructions.md"

        if not template_path.exists():
            return ""
            
        template_content = template_path.read_text(encoding='utf-8')
        
        skills_xml = self._generate_skills_xml()
        if not skills_xml:
            content = template_content.replace("{SKILLS_LIST}", "No skills found.")
        else:
            content = template_content.replace("{SKILLS_LIST}", skills_xml)
            
        return content

    def _copilot_generate_protocol_instruction(self, content: str) -> str:
        # Add metadata to the main file
        metadata_block = [
            "---",
            "name: Spec Kit Skills Protocol",
            "description: Protocol for discovering and using specialized skills.",
            "applyTo: \"**\"",
            "---",
            ""
        ]
        
        return "\n".join(metadata_block) + content

    def generate_protocol_content(self) -> str:
        return self._generate_skills_protocol_content()

    def install(self, path: Optional[Path] = None, format: str = "command-markdown"):
        """
        Generates the skills file based on provided path and format.
        
        Args:
            path: Path to write the skills file.
            format: Format of the skills file (command-markdown, copilot-instructions).
        """
        if not path:
            return

        content = ""
        if format == "copilot-instructions":
            # Generate base content from template
            base_content = self.generate_protocol_content()
            # Add Copilot-specific frontmatter
            content = self._copilot_generate_protocol_instruction(base_content)
        elif format == "markdown":
            content = self.generate_prompt_content()
        else:
            print(f"Unsupported format: {format}", file=sys.stderr)
            return
        
        if content:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
            print(f"Generated skills file at: {path}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate skills file")
    parser.add_argument("--workspace", type=Path, default=Path.cwd(), help="Workspace root directory")
    parser.add_argument("--path", type=Path, help="Path to write skills file")
    parser.add_argument("--format", type=str, default="command-markdown", help="Format of the skills file")
    args = parser.parse_args()
    
    skills = Skills(args.workspace)
    skills.install(path=args.path, format=args.format)
