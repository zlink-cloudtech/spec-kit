#!/usr/bin/env python3
"""
init_spec.py - Generate SPECIFICATION.md from template with directory isolation

This script generates a SPECIFICATION.md file from the template by substituting
placeholders with user-provided data. The Agent should gather all required
information through conversation with the user before invoking this script.

IMPORTANT: This script does NOT handle user interaction. The Agent must collect
all necessary information first, then call this script to generate the file.

Usage:
    # Auto-create isolated directory (RECOMMENDED - supports concurrent features)
    init_spec.py --from-json requirements.json --auto-dir
    
    # Quick mode with auto directory
    init_spec.py --name "OAuth2 Integration" \\
                 --overview "Add OAuth2 authentication support" \\
                 --requirements "Users can login via Google, GitHub, Microsoft" \\
                 --auto-dir
    
    # Use existing directory
    init_spec.py --from-json requirements.json --work-dir specs/001-oauth2
    
    # Traditional mode (output to specific file)
    init_spec.py --from-json requirements.json --output SPECIFICATION.md

JSON Schema:
    {
        "feature_name": "string (required)",
        "overview": "string (required)",
        "user_requirements": "string (required)",
        "business_value": ["string", ...] (optional),
        "target_users": ["string", ...] (optional),
        "constraints": ["string", ...] (optional),
        "acceptance_criteria": ["string", ...] (optional),
        "out_of_scope": ["string", ...] (optional),
        "questions": ["string", ...] (optional)
    }

Example JSON:
    {
        "feature_name": "OAuth2 Integration",
        "overview": "Add OAuth2 authentication to support third-party login providers",
        "user_requirements": "Users should be able to login using Google, GitHub, or Microsoft accounts",
        "business_value": [
            "Reduce friction in user onboarding",
            "Eliminate password management overhead"
        ],
        "target_users": [
            "End users who prefer social login",
            "Enterprise users with SSO requirements"
        ],
        "constraints": [
            "Must support PKCE flow for security",
            "Must work with existing session management"
        ],
        "acceptance_criteria": [
            "Users can login with Google OAuth2",
            "Users can login with GitHub OAuth2",
            "Existing local auth still works"
        ],
        "out_of_scope": [
            "SAML support",
            "Custom OAuth2 providers"
        ],
        "questions": []
    }
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# ============================================================================
# Constants
# ============================================================================

SCRIPT_DIR = Path(__file__).parent.resolve()
TEMPLATE_PATH = SCRIPT_DIR.parent / "assets/templates/SPECIFICATION.template.md"
DEFAULT_SPECS_BASE = "specs"

# ANSI Colors
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    BOLD = '\033[1m'
    NC = '\033[0m'

# ============================================================================
# Directory Management
# ============================================================================

def generate_slug(name: str, max_length: int = 30) -> str:
    """
    Generate URL-friendly slug from feature name.
    
    Logic matches vibe_workflow.py's create_spec_dir() for consistency.
    """
    slug = re.sub(r'[^a-z0-9 ]', '', name.lower())
    words = slug.split()[:3]  # Max 3 words
    slug = '-'.join(words)[:max_length].rstrip('-')
    return slug or "feature"


def create_work_dir(specs_base: str, feature_name: str) -> Path:
    """
    Create isolated work directory with sequential numbering.
    
    Format: specs/NNN-feature-slug/
    - Finds next available number (001, 002, 003...)
    - Generates slug from feature_name
    - Creates subdirectories (sessions/, checklists/, copilot-logs/)
    - Updates .latest symlink
    
    Handles race conditions: If multiple processes try to create directories
    simultaneously, the function retries with the next available number.
    
    Args:
        specs_base: Base directory for specs (e.g., "specs")
        feature_name: Feature name for slug generation
        
    Returns:
        Path to created work directory
    """
    base_dir = Path(specs_base)
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate slug from feature name (reusable)
    slug = generate_slug(feature_name)
    
    # Retry loop to handle race conditions
    max_attempts = 100  # Reasonable limit
    for attempt in range(max_attempts):
        # Find next available number (re-scan each attempt for race condition safety)
        next_num = 1
        for d in base_dir.glob("[0-9][0-9][0-9]-*"):
            if d.is_dir():
                try:
                    num = int(d.name[:3])
                    if num >= next_num:
                        next_num = num + 1
                except ValueError:
                    pass
        
        # Try to create directory with this number
        dir_name = f"{next_num:03d}-{slug}"
        work_dir = base_dir / dir_name
        
        # Use exist_ok=False to detect race conditions
        try:
            work_dir.mkdir(parents=True, exist_ok=False)
            # Success! Create subdirectories
            (work_dir / "sessions").mkdir(exist_ok=True)
            (work_dir / "checklists").mkdir(exist_ok=True)
            (work_dir / "copilot-logs").mkdir(exist_ok=True)
            
            # Update .latest symlink
            latest_link = base_dir / ".latest"
            if latest_link.exists() or latest_link.is_symlink():
                latest_link.unlink()
            latest_link.symlink_to(dir_name)
            
            return work_dir
        except FileExistsError:
            # Race condition: another process created this directory
            # Loop will retry with next number
            continue
    
    # Should never reach here unless we have 100+ failed attempts
    raise RuntimeError(f"Failed to create work directory after {max_attempts} attempts")


# ============================================================================
# Template Loading and Validation
# ============================================================================

def load_template() -> str:
    """Load the SPECIFICATION template."""
    if not TEMPLATE_PATH.exists():
        print(f"{Colors.RED}Error: Template not found at {TEMPLATE_PATH}{Colors.NC}", file=sys.stderr)
        sys.exit(1)
    return TEMPLATE_PATH.read_text()

# ============================================================================
# Input Modes
# ============================================================================

def load_from_json(json_path: Path) -> Dict[str, Any]:
    """Load requirements from JSON file."""
    if not json_path.exists():
        print(f"{Colors.RED}Error: JSON file not found: {json_path}{Colors.NC}", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError as e:
        print(f"{Colors.RED}Error: Invalid JSON in {json_path}: {e}{Colors.NC}", file=sys.stderr)
        sys.exit(1)

def load_from_args(args) -> Dict[str, Any]:
    """Load requirements from command-line arguments."""
    data = {
        "feature_name": args.name,
        "overview": args.overview,
        "user_requirements": args.requirements,
    }
    
    # Optional fields
    if args.business_value:
        data["business_value"] = args.business_value.split("|")
    if args.target_users:
        data["target_users"] = args.target_users.split("|")
    if args.constraints:
        data["constraints"] = args.constraints.split("|")
    if args.acceptance_criteria:
        data["acceptance_criteria"] = args.acceptance_criteria.split("|")
    if args.out_of_scope:
        data["out_of_scope"] = args.out_of_scope.split("|")
    if args.questions:
        data["questions"] = args.questions.split("|")
    
    return data

# ============================================================================
# Validation
# ============================================================================

def validate_data(data: Dict[str, Any]) -> bool:
    """Validate that required fields are present."""
    required_fields = ["feature_name", "overview", "user_requirements"]
    missing = [field for field in required_fields if field not in data or not data[field]]
    
    if missing:
        print(f"{Colors.RED}Error: Missing required fields: {', '.join(missing)}{Colors.NC}", file=sys.stderr)
        print(f"\n{Colors.YELLOW}Required fields:{Colors.NC}", file=sys.stderr)
        print("  - feature_name: Name of the feature", file=sys.stderr)
        print("  - overview: Brief description of the feature", file=sys.stderr)
        print("  - user_requirements: What the user wants", file=sys.stderr)
        return False
    
    return True

# ============================================================================
# Template Rendering
# ============================================================================

def format_list(items: Optional[List[str]], prefix: str = "-") -> str:
    """Format a list of items as markdown list."""
    if not items:
        return f"{prefix} [To be determined]"
    return "\n".join([f"{prefix} {item}" for item in items])

def format_numbered_list(items: Optional[List[str]]) -> str:
    """Format a list of items as numbered markdown list."""
    if not items:
        return "1. [To be determined]"
    return "\n".join([f"{i+1}. {item}" for i, item in enumerate(items)])

def render_spec(template: str, data: Dict[str, Any]) -> str:
    """Render template with user data."""
    # Required fields
    spec = template.replace("[FEATURE_NAME]", data["feature_name"])
    spec = spec.replace("[Brief description of the feature and its purpose]", data["overview"])
    spec = spec.replace("[Natural language description of what the user wants]", data["user_requirements"])
    
    # Optional fields with defaults
    business_value = format_list(data.get("business_value"))
    target_users = format_list(data.get("target_users"))
    constraints = format_list(data.get("constraints"))
    acceptance = format_numbered_list(data.get("acceptance_criteria"))
    out_of_scope = format_list(data.get("out_of_scope"))
    questions = format_list(data.get("questions"))
    
    # Replace optional sections
    spec = spec.replace("- [Why is this feature needed?]\n- [What problem does it solve?]", business_value)
    spec = spec.replace("- [Who will use this feature?]", target_users)
    spec = spec.replace("- [Any technical or business constraints]\n- [Timeline requirements]\n- [Dependencies on other systems]", constraints)
    spec = spec.replace("1. [Criterion 1: What must be true for this to be complete?]\n2. [Criterion 2]\n3. [Criterion 3]", acceptance)
    spec = spec.replace("- [What is explicitly NOT included]", out_of_scope)
    spec = spec.replace("- [Any questions that need answers before starting]", questions)
    
    return spec

# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate SPECIFICATION.md from template",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # From JSON file with auto directory creation (recommended)
  %(prog)s --from-json requirements.json --auto-dir
  
  # From command-line with auto directory
  %(prog)s --name "OAuth2" --overview "Add OAuth2 auth" --requirements "Support Google login" --auto-dir
  
  # Use existing directory
  %(prog)s --from-json requirements.json --work-dir specs/001-oauth2
  
  # Traditional mode (output to specific file)
  %(prog)s --from-json requirements.json --output SPECIFICATION.md
  
  # With multiple list items (use | as separator)
  %(prog)s --name "API" --overview "REST API" --requirements "CRUD endpoints" \\
           --acceptance-criteria "GET endpoint works|POST endpoint works|Auth required" --auto-dir
        """
    )
    
    # Input mode
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--from-json",
        type=Path,
        metavar="FILE",
        help="Load requirements from JSON file"
    )
    input_group.add_argument(
        "--name",
        help="Feature name (use with --overview and --requirements for quick mode)"
    )
    
    # Quick mode arguments
    parser.add_argument("--overview", help="Brief feature description")
    parser.add_argument("--requirements", help="User requirements description")
    parser.add_argument("--business-value", help="Business value (use | to separate multiple items)")
    parser.add_argument("--target-users", help="Target users (use | to separate multiple items)")
    parser.add_argument("--constraints", help="Constraints (use | to separate multiple items)")
    parser.add_argument("--acceptance-criteria", help="Acceptance criteria (use | to separate multiple items)")
    parser.add_argument("--out-of-scope", help="Out of scope items (use | to separate multiple items)")
    parser.add_argument("--questions", help="Questions/clarifications (use | to separate multiple items)")
    
    # Directory management (new)
    dir_group = parser.add_mutually_exclusive_group()
    dir_group.add_argument(
        "--auto-dir",
        action="store_true",
        help="Automatically create isolated work directory (specs/NNN-feature-name/)"
    )
    dir_group.add_argument(
        "--work-dir",
        type=Path,
        metavar="DIR",
        help="Use existing work directory (must exist)"
    )
    
    parser.add_argument(
        "--specs-base",
        default=DEFAULT_SPECS_BASE,
        help=f"Base directory for specs (default: {DEFAULT_SPECS_BASE})"
    )
    
    parser.add_argument(
        "--save-json",
        action="store_true",
        help="Save requirements.json to work directory (automatic with --auto-dir)"
    )
    
    # Output
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default="SPECIFICATION.md",
        help="Output file path (default: SPECIFICATION.md, ignored with --auto-dir or --work-dir)"
    )
    
    # Flags
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Overwrite output file if it exists"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print output to stdout instead of writing to file"
    )
    
    args = parser.parse_args()
    
    # Load data
    if args.from_json:
        data = load_from_json(args.from_json)
    else:
        # Quick mode requires name, overview, and requirements
        if not args.overview or not args.requirements:
            parser.error("Quick mode requires --name, --overview, and --requirements")
        data = load_from_args(args)
    
    # Validate
    if not validate_data(data):
        sys.exit(1)
    
    # Determine work directory and whether to save JSON
    work_dir: Path
    save_requirements: bool
    
    if args.auto_dir:
        # Auto-create isolated directory
        work_dir = create_work_dir(args.specs_base, data["feature_name"])
        print(f"{Colors.GREEN}✓ Created work directory: {work_dir}{Colors.NC}")
        save_requirements = True  # Always save JSON in auto-dir mode
    elif args.work_dir:
        # Use existing directory
        work_dir = args.work_dir
        if not work_dir.exists():
            print(f"{Colors.RED}Error: Work directory does not exist: {work_dir}{Colors.NC}", file=sys.stderr)
            sys.exit(1)
        save_requirements = args.save_json
    else:
        # Traditional mode: use --output path
        work_dir = args.output.parent if args.output.parent != Path('.') else Path('.')
        save_requirements = args.save_json
        
        # Warn if --output is ignored
        if args.auto_dir or args.work_dir:
            print(f"{Colors.YELLOW}Note: --output ignored when using --auto-dir or --work-dir{Colors.NC}")
    
    # Save requirements.json if requested
    if save_requirements:
        req_json_path = work_dir / "requirements.json"
        with open(req_json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"{Colors.GREEN}✓ Saved: {req_json_path}{Colors.NC}")
    
    # Load template and render
    template = load_template()
    spec_content = render_spec(template, data)
    
    # Output
    if args.dry_run:
        print(spec_content)
    else:
        # Determine output path
        if args.auto_dir or args.work_dir:
            spec_path = work_dir / "SPECIFICATION.md"
        else:
            spec_path = args.output
        
        # Check if file exists (unless in auto-dir mode where we expect a clean directory)
        if not args.auto_dir and spec_path.exists() and not args.force:
            print(f"{Colors.YELLOW}Warning: {spec_path} already exists. Use --force to overwrite.{Colors.NC}", file=sys.stderr)
            sys.exit(1)
        
        # Write file
        spec_path.write_text(spec_content, encoding='utf-8')
        print(f"{Colors.GREEN}✓ Generated: {spec_path}{Colors.NC}")
        
        # Show next step (updated based on mode)
        if args.auto_dir or args.work_dir:
            print(f"\n{Colors.CYAN}Next step:{Colors.NC}")
            print(f"  python3 scripts/vibe_workflow.py --auto --spec-dir {work_dir}")
        else:
            print(f"\n{Colors.CYAN}Next step:{Colors.NC}")
            print(f"  python3 scripts/vibe_workflow.py --auto --spec {spec_path}")

if __name__ == "__main__":
    main()
