#!/usr/bin/env python3
"""
learning-collector.py - Collect and categorize learnings from sessions

Usage:
    learning-collector.py --session-log FILE   Parse session log for learnings
    learning-collector.py --update-agents      Update AGENTS.md with learnings
    learning-collector.py --list               List pending learnings
    learning-collector.py --category CAT       Filter by category
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Directories
STATE_DIR = Path(".speckit-vc")
LEARNINGS_DIR = STATE_DIR / "learnings"
PENDING_FILE = LEARNINGS_DIR / "pending.json"
APPLIED_FILE = LEARNINGS_DIR / "applied.json"

# Learning categories
CATEGORIES = {
    "code-patterns": "Code patterns and best practices",
    "tool-usage": "Tool and command usage tips",
    "workflow-issues": "Workflow and process issues",
    "model-limitations": "AI model limitations and workarounds",
    "project-specific": "Project-specific knowledge"
}

# Patterns to detect issues in logs
ISSUE_PATTERNS = [
    # Error patterns
    (r"Error:?\s+(.+)", "error"),
    (r"ERROR\s+(.+)", "error"),
    (r"Failed:?\s+(.+)", "error"),
    (r"Exception:?\s+(.+)", "error"),
    
    # Warning patterns
    (r"Warning:?\s+(.+)", "warning"),
    (r"WARN\s+(.+)", "warning"),
    
    # Retry patterns (indicates issues)
    (r"Retry(?:ing)?:?\s+(.+)", "retry"),
    (r"Attempting again:?\s+(.+)", "retry"),
    
    # Missing/not found patterns
    (r"not found:?\s+(.+)", "missing"),
    (r"Missing:?\s+(.+)", "missing"),
    (r"Cannot find:?\s+(.+)", "missing"),
    
    # Timeout patterns
    (r"Timeout:?\s+(.+)", "timeout"),
    (r"Timed out:?\s+(.+)", "timeout"),
    
    # Permission patterns
    (r"Permission denied:?\s+(.+)", "permission"),
    (r"Access denied:?\s+(.+)", "permission"),
    
    # Hallucination indicators
    (r"does not exist", "hallucination"),
    (r"no such (?:file|directory|command)", "hallucination"),
    (r"undefined (?:variable|function|method)", "hallucination"),
]

# Category detection patterns
CATEGORY_PATTERNS = {
    "code-patterns": [
        r"syntax error",
        r"type error",
        r"null pointer",
        r"undefined reference",
        r"import error",
        r"module not found",
    ],
    "tool-usage": [
        r"git",
        r"npm|yarn|pnpm",
        r"docker",
        r"kubectl",
        r"command not found",
        r"invalid (?:option|argument)",
    ],
    "workflow-issues": [
        r"speckit\.",
        r"stage",
        r"workflow",
        r"dependency",
        r"order",
    ],
    "model-limitations": [
        r"hallucin",
        r"does not exist",
        r"incorrect assumption",
        r"fabricated",
    ],
}


def ensure_dirs() -> None:
    """Ensure required directories exist."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    LEARNINGS_DIR.mkdir(exist_ok=True)


def load_learnings(filepath: Path) -> List[Dict[str, Any]]:
    """Load learnings from JSON file."""
    if not filepath.exists():
        return []
    
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def save_learnings(learnings: List[Dict[str, Any]], filepath: Path) -> None:
    """Save learnings to JSON file."""
    ensure_dirs()
    with open(filepath, 'w') as f:
        json.dump(learnings, f, indent=2)


def detect_category(text: str) -> str:
    """Detect the category of a learning based on content."""
    text_lower = text.lower()
    
    for category, patterns in CATEGORY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return category
    
    return "project-specific"


def extract_learnings_from_log(log_content: str) -> List[Dict[str, Any]]:
    """Extract potential learnings from session log content."""
    learnings = []
    seen = set()  # Avoid duplicates
    
    lines = log_content.split('\n')
    
    for i, line in enumerate(lines):
        for pattern, issue_type in ISSUE_PATTERNS:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                issue_text = match.group(1) if match.lastindex else match.group(0)
                issue_text = issue_text.strip()
                
                # Skip if too short or already seen
                if len(issue_text) < 10 or issue_text in seen:
                    continue
                
                seen.add(issue_text)
                
                # Get context (surrounding lines)
                context_start = max(0, i - 2)
                context_end = min(len(lines), i + 3)
                context = '\n'.join(lines[context_start:context_end])
                
                # Detect category
                category = detect_category(issue_text + ' ' + context)
                
                learning = {
                    'id': f"L{len(learnings)+1:03d}",
                    'timestamp': datetime.now().isoformat(),
                    'type': issue_type,
                    'category': category,
                    'summary': issue_text[:200],
                    'context': context[:500],
                    'status': 'pending',
                    'suggested_action': generate_suggested_action(issue_type, category, issue_text)
                }
                
                learnings.append(learning)
    
    return learnings


def generate_suggested_action(issue_type: str, category: str, text: str) -> str:
    """Generate a suggested action for a learning."""
    actions = {
        "error": "Add error handling guidance or check for this pattern",
        "warning": "Consider adding a note about this warning scenario",
        "retry": "Document the retry scenario and preferred approach",
        "missing": "Verify dependencies and add prerequisite checks",
        "timeout": "Document timeout handling and consider timeout adjustments",
        "permission": "Add permission requirements documentation",
        "hallucination": "Add clarification to prevent AI hallucination in this area",
    }
    
    base_action = actions.get(issue_type, "Review and document this issue")
    
    category_prefix = {
        "code-patterns": "Update coding guidelines: ",
        "tool-usage": "Update tool tips: ",
        "workflow-issues": "Update workflow documentation: ",
        "model-limitations": "Add to known limitations: ",
        "project-specific": "Add project-specific note: ",
    }
    
    return category_prefix.get(category, "") + base_action


def format_learning_for_agents_md(learning: Dict[str, Any]) -> str:
    """Format a learning entry for AGENTS.md."""
    category = learning.get('category', 'general')
    summary = learning.get('summary', '')
    action = learning.get('suggested_action', '')
    
    return f"- **{category}**: {summary}\n  - Action: {action}"


def update_agents_md(learnings: List[Dict[str, Any]], agents_path: str, dry_run: bool = False) -> None:
    """Update AGENTS.md with learnings."""
    agents_file = Path(agents_path)
    
    if not agents_file.exists():
        print(f"Warning: AGENTS.md not found at {agents_path}", file=sys.stderr)
        if dry_run:
            print("\n[DRY-RUN] Would create AGENTS.md with learnings section")
        return
    
    # Read current content
    with open(agents_file, 'r') as f:
        content = f.read()
    
    # Check if learnings section exists
    learnings_header = "## AI Learnings"
    
    if learnings_header not in content:
        # Add new section at the end
        new_section = f"\n\n{learnings_header}\n\nAutomatically collected learnings from vibe coding sessions:\n\n"
        content += new_section
    
    # Format learnings by category
    by_category: Dict[str, List[str]] = {}
    for learning in learnings:
        cat = learning.get('category', 'general')
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(format_learning_for_agents_md(learning))
    
    # Build additions
    additions = []
    for category, items in sorted(by_category.items()):
        additions.append(f"\n### {CATEGORIES.get(category, category)}\n")
        additions.extend(items)
    
    if dry_run:
        print("\n[DRY-RUN] Would add the following to AGENTS.md:")
        print("-" * 50)
        print('\n'.join(additions))
        print("-" * 50)
        return
    
    # Find position to insert (after learnings header)
    insert_pos = content.find(learnings_header)
    if insert_pos != -1:
        # Find end of header line
        insert_pos = content.find('\n', insert_pos)
        # Skip any existing description line
        next_newline = content.find('\n\n', insert_pos)
        if next_newline != -1:
            insert_pos = next_newline
        
        # Insert learnings
        new_content = content[:insert_pos] + '\n'.join(additions) + content[insert_pos:]
    else:
        new_content = content + '\n'.join(additions)
    
    with open(agents_file, 'w') as f:
        f.write(new_content)
    
    print(f"Updated {agents_path} with {len(learnings)} learnings")


def cmd_parse_log(args) -> None:
    """Parse session log(s) for learnings."""
    log_path = Path(args.session_log)
    
    if log_path.is_dir():
        # Parse all logs in directory
        log_files = list(log_path.glob("*.log"))
        if not log_files:
            print(f"No log files found in {log_path}")
            return
    else:
        log_files = [log_path]
    
    all_learnings = []
    
    for log_file in log_files:
        if not log_file.exists():
            print(f"Warning: Log file not found: {log_file}", file=sys.stderr)
            continue
        
        print(f"Parsing: {log_file}")
        
        with open(log_file, 'r') as f:
            content = f.read()
        
        learnings = extract_learnings_from_log(content)
        
        # Add source info
        for learning in learnings:
            learning['source'] = str(log_file)
        
        all_learnings.extend(learnings)
    
    if not all_learnings:
        print("No learnings extracted from logs")
        return
    
    # Load existing pending learnings
    pending = load_learnings(PENDING_FILE)
    
    # Add new learnings (avoid duplicates by summary)
    existing_summaries = {l.get('summary') for l in pending}
    new_learnings = [l for l in all_learnings if l.get('summary') not in existing_summaries]
    
    if new_learnings:
        pending.extend(new_learnings)
        save_learnings(pending, PENDING_FILE)
        print(f"\nExtracted {len(new_learnings)} new learnings")
        print(f"Total pending: {len(pending)}")
    else:
        print("No new learnings found (all duplicates)")


def cmd_list(args) -> None:
    """List learnings."""
    pending = load_learnings(PENDING_FILE)
    applied = load_learnings(APPLIED_FILE)
    
    if args.all:
        learnings = pending + applied
    elif args.applied:
        learnings = applied
    else:
        learnings = pending
    
    # Filter by category if specified
    if args.category:
        learnings = [l for l in learnings if l.get('category') == args.category]
    
    if not learnings:
        print("No learnings found")
        return
    
    if args.json:
        print(json.dumps(learnings, indent=2))
        return
    
    # Group by category
    by_category: Dict[str, List[Dict[str, Any]]] = {}
    for learning in learnings:
        cat = learning.get('category', 'general')
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(learning)
    
    for category, items in sorted(by_category.items()):
        print(f"\n{CATEGORIES.get(category, category)}")
        print("=" * 50)
        
        for item in items:
            status = "✓" if item.get('status') == 'applied' else "○"
            print(f"\n{status} [{item.get('id', 'N/A')}] {item.get('type', 'unknown')}")
            print(f"  Summary: {item.get('summary', 'N/A')[:80]}")
            print(f"  Action:  {item.get('suggested_action', 'N/A')[:80]}")


def cmd_update_agents(args) -> None:
    """Update AGENTS.md with pending learnings."""
    pending = load_learnings(PENDING_FILE)
    
    if not pending:
        print("No pending learnings to apply")
        return
    
    # Filter by category if specified
    if args.category:
        to_apply = [l for l in pending if l.get('category') == args.category]
        remaining = [l for l in pending if l.get('category') != args.category]
    else:
        to_apply = pending
        remaining = []
    
    if not to_apply:
        print(f"No learnings in category: {args.category}")
        return
    
    # Get AGENTS.md path from config or default
    agents_path = args.agents_path or "AGENTS.md"
    
    update_agents_md(to_apply, agents_path, args.dry_run)
    
    if not args.dry_run:
        # Move to applied
        applied = load_learnings(APPLIED_FILE)
        for learning in to_apply:
            learning['status'] = 'applied'
            learning['applied_at'] = datetime.now().isoformat()
        applied.extend(to_apply)
        save_learnings(applied, APPLIED_FILE)
        
        # Update pending
        save_learnings(remaining, PENDING_FILE)
        
        print(f"Applied {len(to_apply)} learnings")


def cmd_clear(args) -> None:
    """Clear learnings."""
    if args.applied:
        if not args.force:
            response = input("Clear applied learnings? [y/N] ")
            if response.lower() != 'y':
                print("Cancelled")
                return
        save_learnings([], APPLIED_FILE)
        print("Cleared applied learnings")
    
    if args.pending or not args.applied:
        if not args.force:
            response = input("Clear pending learnings? [y/N] ")
            if response.lower() != 'y':
                print("Cancelled")
                return
        save_learnings([], PENDING_FILE)
        print("Cleared pending learnings")


def cmd_approve(args) -> None:
    """Approve a specific learning for application."""
    pending = load_learnings(PENDING_FILE)
    
    learning_id = args.learning_id
    
    found = None
    for i, learning in enumerate(pending):
        if learning.get('id') == learning_id:
            found = (i, learning)
            break
    
    if not found:
        print(f"Learning not found: {learning_id}")
        return
    
    idx, learning = found
    
    print(f"Learning: {learning.get('summary')}")
    print(f"Category: {learning.get('category')}")
    print(f"Action: {learning.get('suggested_action')}")
    
    if args.edit:
        # Allow editing
        new_action = input(f"New action (or Enter to keep): ").strip()
        if new_action:
            learning['suggested_action'] = new_action
        
        new_category = input(f"New category [{', '.join(CATEGORIES.keys())}] (or Enter to keep): ").strip()
        if new_category and new_category in CATEGORIES:
            learning['category'] = new_category
    
    learning['approved'] = True
    learning['approved_at'] = datetime.now().isoformat()
    pending[idx] = learning
    save_learnings(pending, PENDING_FILE)
    
    print(f"✓ Learning {learning_id} approved")


def main():
    parser = argparse.ArgumentParser(
        description="Collect and manage learnings from vibe coding sessions",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # parse command
    parse_parser = subparsers.add_parser('parse', help='Parse session logs')
    parse_parser.add_argument('--session-log', required=True,
                             help='Session log file or directory')
    
    # list command
    list_parser = subparsers.add_parser('list', help='List learnings')
    list_parser.add_argument('--category', '-c', choices=list(CATEGORIES.keys()),
                            help='Filter by category')
    list_parser.add_argument('--applied', action='store_true',
                            help='Show applied learnings')
    list_parser.add_argument('--all', action='store_true',
                            help='Show all learnings')
    list_parser.add_argument('--json', action='store_true',
                            help='Output as JSON')
    
    # update-agents command
    update_parser = subparsers.add_parser('update-agents', help='Update AGENTS.md')
    update_parser.add_argument('--category', '-c', choices=list(CATEGORIES.keys()),
                              help='Only apply learnings from category')
    update_parser.add_argument('--agents-path', default='AGENTS.md',
                              help='Path to AGENTS.md')
    update_parser.add_argument('--dry-run', action='store_true',
                              help='Show changes without applying')
    
    # clear command
    clear_parser = subparsers.add_parser('clear', help='Clear learnings')
    clear_parser.add_argument('--pending', action='store_true',
                             help='Clear pending learnings')
    clear_parser.add_argument('--applied', action='store_true',
                             help='Clear applied learnings')
    clear_parser.add_argument('--force', '-f', action='store_true',
                             help='Skip confirmation')
    
    # approve command
    approve_parser = subparsers.add_parser('approve', help='Approve a learning')
    approve_parser.add_argument('learning_id', help='Learning ID to approve')
    approve_parser.add_argument('--edit', '-e', action='store_true',
                               help='Edit before approving')
    
    # Legacy argument support
    parser.add_argument('--session-log', help='(Legacy) Parse session log')
    parser.add_argument('--update-agents', action='store_true',
                       help='(Legacy) Update AGENTS.md')
    parser.add_argument('--dry-run', action='store_true',
                       help='(Legacy) Dry run mode')
    parser.add_argument('--category', help='(Legacy) Filter by category')
    
    args = parser.parse_args()
    
    ensure_dirs()
    
    # Handle legacy arguments
    if args.session_log and not args.command:
        args.command = 'parse'
    elif args.update_agents and not args.command:
        args.command = 'update-agents'
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Dispatch to command handler
    commands = {
        'parse': cmd_parse_log,
        'list': cmd_list,
        'update-agents': cmd_update_agents,
        'clear': cmd_clear,
        'approve': cmd_approve
    }
    
    commands[args.command](args)


if __name__ == '__main__':
    main()
