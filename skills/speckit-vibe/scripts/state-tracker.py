#!/usr/bin/env python3
"""
state-tracker.py - Track workflow state for resume capability

Usage:
    state-tracker.py status [--spec-dir DIR]     Show current workflow state
    state-tracker.py checkpoint STAGE            Mark stage as completed
    state-tracker.py reset                       Reset workflow state
    state-tracker.py resume                      Get next stage to execute
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# State directory
STATE_DIR = Path(".speckit-vc")
STATE_FILE = STATE_DIR / "state.json"

# Workflow stages in order
WORKFLOW_STAGES = [
    "specify",
    "clarify", 
    "plan",
    "tasks",
    "checklist",
    "analyze",
    "implement"
]


def ensure_state_dir() -> None:
    """Ensure state directory exists."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    (STATE_DIR / "sessions").mkdir(exist_ok=True)
    (STATE_DIR / "learnings").mkdir(exist_ok=True)
    (STATE_DIR / "tasks").mkdir(exist_ok=True)


def load_state() -> Dict[str, Any]:
    """Load workflow state from file."""
    if not STATE_FILE.exists():
        return create_initial_state()
    
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("Warning: Corrupted state file, creating new state", file=sys.stderr)
        return create_initial_state()


def save_state(state: Dict[str, Any]) -> None:
    """Save workflow state to file."""
    ensure_state_dir()
    state['updated_at'] = datetime.now().isoformat()
    
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def create_initial_state() -> Dict[str, Any]:
    """Create initial workflow state."""
    return {
        'workflow_id': datetime.now().strftime('%Y%m%d_%H%M%S'),
        'started_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'current_stage': None,
        'completed_stages': [],
        'failed_stage': None,
        'failed_at': None,
        'spec_dir': None,
        'requirement': None,
        'task_status': {}
    }


def get_next_stage(completed: List[str]) -> Optional[str]:
    """Get the next stage to execute based on completed stages."""
    for stage in WORKFLOW_STAGES:
        if stage not in completed:
            return stage
    return None


def cmd_status(args) -> None:
    """Show current workflow state."""
    state = load_state()
    
    if args.json:
        print(json.dumps(state, indent=2))
        return
    
    print("Workflow State")
    print("=" * 50)
    print(f"Workflow ID:      {state.get('workflow_id', 'N/A')}")
    print(f"Started:          {state.get('started_at', 'N/A')}")
    print(f"Last Updated:     {state.get('updated_at', 'N/A')}")
    print(f"Spec Directory:   {state.get('spec_dir', 'Not set')}")
    print()
    
    # Stage progress
    print("Stage Progress:")
    print("-" * 50)
    
    completed = state.get('completed_stages', [])
    current = state.get('current_stage')
    failed = state.get('failed_stage')
    
    for stage in WORKFLOW_STAGES:
        if stage in completed:
            status = "✓ Completed"
            color = "\033[92m"  # Green
        elif stage == current:
            status = "⟳ In Progress"
            color = "\033[93m"  # Yellow
        elif stage == failed:
            status = "✗ Failed"
            color = "\033[91m"  # Red
        else:
            status = "○ Pending"
            color = "\033[90m"  # Gray
        
        reset = "\033[0m"
        print(f"  {color}{stage:12} {status}{reset}")
    
    print()
    
    # Next action
    if failed:
        print(f"⚠ Workflow failed at stage: {failed}")
        print(f"  Failed at: {state.get('failed_at', 'Unknown')}")
        print("  Run with --stage to retry from a specific stage")
    elif current:
        print(f"Currently executing: {current}")
    else:
        next_stage = get_next_stage(completed)
        if next_stage:
            print(f"Next stage: {next_stage}")
        else:
            print("✓ All stages completed!")
    
    # Task status summary
    task_status = state.get('task_status', {})
    if task_status:
        print()
        print("Task Execution Summary:")
        print("-" * 50)
        
        completed_tasks = sum(1 for t in task_status.values() if t.get('status') == 'completed')
        failed_tasks = sum(1 for t in task_status.values() if t.get('status') == 'failed')
        pending_tasks = sum(1 for t in task_status.values() if t.get('status') == 'pending')
        
        print(f"  Completed: {completed_tasks}")
        print(f"  Failed:    {failed_tasks}")
        print(f"  Pending:   {pending_tasks}")


def cmd_checkpoint(args) -> None:
    """Mark a stage as completed."""
    state = load_state()
    stage = args.stage
    
    if stage not in WORKFLOW_STAGES:
        print(f"Error: Unknown stage: {stage}", file=sys.stderr)
        print(f"Valid stages: {', '.join(WORKFLOW_STAGES)}")
        sys.exit(1)
    
    if stage not in state.get('completed_stages', []):
        if 'completed_stages' not in state:
            state['completed_stages'] = []
        state['completed_stages'].append(stage)
    
    # Clear current stage if it matches
    if state.get('current_stage') == stage:
        state['current_stage'] = None
    
    # Clear failed status if marking that stage complete
    if state.get('failed_stage') == stage:
        state['failed_stage'] = None
        state['failed_at'] = None
    
    save_state(state)
    print(f"✓ Stage '{stage}' marked as completed")


def cmd_start(args) -> None:
    """Mark a stage as started (in progress)."""
    state = load_state()
    stage = args.stage
    
    if stage not in WORKFLOW_STAGES:
        print(f"Error: Unknown stage: {stage}", file=sys.stderr)
        print(f"Valid stages: {', '.join(WORKFLOW_STAGES)}")
        sys.exit(1)
    
    state['current_stage'] = stage
    
    # Clear failed status
    if state.get('failed_stage') == stage:
        state['failed_stage'] = None
        state['failed_at'] = None
    
    save_state(state)
    print(f"⟳ Stage '{stage}' marked as in-progress")


def cmd_fail(args) -> None:
    """Mark a stage as failed."""
    state = load_state()
    stage = args.stage
    
    if stage not in WORKFLOW_STAGES:
        print(f"Error: Unknown stage: {stage}", file=sys.stderr)
        print(f"Valid stages: {', '.join(WORKFLOW_STAGES)}")
        sys.exit(1)
    
    state['failed_stage'] = stage
    state['failed_at'] = datetime.now().isoformat()
    state['current_stage'] = None
    
    save_state(state)
    print(f"✗ Stage '{stage}' marked as failed")


def cmd_reset(args) -> None:
    """Reset workflow state."""
    if not args.force:
        response = input("Reset workflow state? This will clear all progress. [y/N] ")
        if response.lower() != 'y':
            print("Cancelled")
            return
    
    state = create_initial_state()
    save_state(state)
    print("Workflow state reset")


def cmd_resume(args) -> None:
    """Get the next stage to execute."""
    state = load_state()
    
    completed = state.get('completed_stages', [])
    failed = state.get('failed_stage')
    
    # If there's a failed stage, suggest retrying it
    if failed:
        print(failed)
        return
    
    next_stage = get_next_stage(completed)
    
    if next_stage:
        print(next_stage)
    else:
        print("COMPLETE")


def cmd_set_spec_dir(args) -> None:
    """Set the spec directory in state."""
    state = load_state()
    
    spec_dir = args.spec_dir
    
    # Validate directory exists
    if not Path(spec_dir).is_dir():
        print(f"Warning: Directory does not exist: {spec_dir}", file=sys.stderr)
    
    state['spec_dir'] = spec_dir
    save_state(state)
    print(f"Set spec directory: {spec_dir}")


def cmd_task(args) -> None:
    """Manage task status within the workflow."""
    state = load_state()
    
    if 'task_status' not in state:
        state['task_status'] = {}
    
    task_id = args.task_id
    action = args.action
    
    if action == 'start':
        state['task_status'][task_id] = {
            'status': 'in_progress',
            'started_at': datetime.now().isoformat()
        }
        print(f"⟳ Task {task_id} started")
    
    elif action == 'complete':
        if task_id in state['task_status']:
            state['task_status'][task_id]['status'] = 'completed'
            state['task_status'][task_id]['completed_at'] = datetime.now().isoformat()
        else:
            state['task_status'][task_id] = {
                'status': 'completed',
                'completed_at': datetime.now().isoformat()
            }
        print(f"✓ Task {task_id} completed")
    
    elif action == 'fail':
        if task_id in state['task_status']:
            state['task_status'][task_id]['status'] = 'failed'
            state['task_status'][task_id]['failed_at'] = datetime.now().isoformat()
        else:
            state['task_status'][task_id] = {
                'status': 'failed',
                'failed_at': datetime.now().isoformat()
            }
        print(f"✗ Task {task_id} failed")
    
    elif action == 'status':
        if task_id in state['task_status']:
            print(json.dumps(state['task_status'][task_id], indent=2))
        else:
            print("Not found")
            return
    
    save_state(state)


def main():
    parser = argparse.ArgumentParser(
        description="Track speckit-vibe workflow state",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # status command
    status_parser = subparsers.add_parser('status', help='Show current state')
    status_parser.add_argument('--spec-dir', help='Override spec directory')
    status_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    # checkpoint command
    checkpoint_parser = subparsers.add_parser('checkpoint', help='Mark stage completed')
    checkpoint_parser.add_argument('stage', help='Stage name')
    
    # start command
    start_parser = subparsers.add_parser('start', help='Mark stage as started')
    start_parser.add_argument('stage', help='Stage name')
    
    # fail command
    fail_parser = subparsers.add_parser('fail', help='Mark stage as failed')
    fail_parser.add_argument('stage', help='Stage name')
    
    # reset command
    reset_parser = subparsers.add_parser('reset', help='Reset workflow state')
    reset_parser.add_argument('--force', '-f', action='store_true', help='Skip confirmation')
    
    # resume command
    subparsers.add_parser('resume', help='Get next stage to execute')
    
    # set-spec-dir command
    spec_dir_parser = subparsers.add_parser('set-spec-dir', help='Set spec directory')
    spec_dir_parser.add_argument('spec_dir', help='Spec directory path')
    
    # task command
    task_parser = subparsers.add_parser('task', help='Manage task status')
    task_parser.add_argument('action', choices=['start', 'complete', 'fail', 'status'],
                            help='Action to perform')
    task_parser.add_argument('task_id', help='Task ID (e.g., T001)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Ensure state directory exists
    ensure_state_dir()
    
    # Dispatch to command handler
    commands = {
        'status': cmd_status,
        'checkpoint': cmd_checkpoint,
        'start': cmd_start,
        'fail': cmd_fail,
        'reset': cmd_reset,
        'resume': cmd_resume,
        'set-spec-dir': cmd_set_spec_dir,
        'task': cmd_task
    }
    
    commands[args.command](args)


if __name__ == '__main__':
    main()
