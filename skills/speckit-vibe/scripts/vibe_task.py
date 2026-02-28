#!/usr/bin/env python3
"""
vibe_task.py - Execute individual tasks with vibe coding

This script executes tasks from tasks.md using pluggable agent adapters.
It supports single task execution and phase-based parallel execution.

Usage:
    vibe_task.py --task T001 --spec-dir spec-vibes/001-feature
    vibe_task.py --phase 2 --parallel 4 --spec-dir spec-vibes/001-feature

Examples:
    # Single task execution
    vibe_task.py --task T005 --spec-dir spec-vibes/001-feature
    
    # Execute phase with parallelism
    vibe_task.py --phase 3 --parallel 4 --spec-dir spec-vibes/001-feature
    
    # Dry run to see what would execute
    vibe_task.py --task T001 --spec-dir spec-vibes/001-feature --dry-run
"""

import argparse
import concurrent.futures
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add parent directory to path for imports
SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

from adapters import (
    AgentAdapter,
    AgentConfig,
    ExecutionContext,
    ExecutionMode,
    ExecutionResult,
    ToolPermissions,
    get_adapter,
    get_default_adapter,
)

# ============================================================================
# Constants
# ============================================================================

CONFIG_FILE = ".speckit-vc.json"
STATE_DIR = ".speckit-vc"

# ANSI Colors
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'


# ============================================================================
# Logging
# ============================================================================

LOG_LEVEL = "INFO"

def set_log_level(level: str) -> None:
    global LOG_LEVEL
    LOG_LEVEL = level.upper()

def log_debug(msg: str) -> None:
    if LOG_LEVEL == "DEBUG":
        print(f"{Colors.BLUE}[DEBUG]{Colors.NC} {msg}", file=sys.stderr)

def log_info(msg: str) -> None:
    if LOG_LEVEL in ("DEBUG", "INFO"):
        print(f"{Colors.GREEN}[INFO]{Colors.NC} {msg}", file=sys.stderr)

def log_warn(msg: str) -> None:
    if LOG_LEVEL in ("DEBUG", "INFO", "WARN"):
        print(f"{Colors.YELLOW}[WARN]{Colors.NC} {msg}", file=sys.stderr)

def log_error(msg: str) -> None:
    print(f"{Colors.RED}[ERROR]{Colors.NC} {msg}", file=sys.stderr)


# ============================================================================
# Configuration
# ============================================================================

@dataclass
class TaskConfig:
    """Task executor configuration."""
    agent: str = "copilot"
    model: str = "claude-sonnet-4.5"
    allow_tools: bool = True
    excluded_tools: List[str] = field(default_factory=lambda: ["skill(speckit-vibe)"])
    log_level: str = "INFO"
    max_parallel: int = 3
    timeout_minutes: int = 30
    retry_count: int = 2
    agent_config: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    @classmethod
    def load(cls, config_file: str = CONFIG_FILE) -> "TaskConfig":
        """Load configuration from file."""
        config_path = Path(config_file)
        
        if not config_path.exists():
            return cls()
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return cls(
                agent=data.get("agent", "copilot"),
                model=data.get("model", "claude-sonnet-4.5"),
                allow_tools=data.get("allow_tools", True),
                excluded_tools=data.get("excluded_tools", ["skill(speckit-vibe)"]),
                log_level=data.get("log_level", "INFO"),
                max_parallel=data.get("max_parallel", 3),
                timeout_minutes=data.get("timeout_minutes", 30),
                retry_count=data.get("retry_count", 2),
                agent_config=data.get("agent_config", {}),
            )
        except json.JSONDecodeError as e:
            log_error(f"Invalid JSON in {config_file}: {e}")
            sys.exit(1)
    
    def get_agent_config(self) -> Dict[str, Any]:
        """Get configuration for the currently selected agent."""
        return self.agent_config.get(self.agent, {})


# ============================================================================
# Task Parsing
# ============================================================================

@dataclass
class Task:
    """Represents a task from tasks.md"""
    task_id: str
    description: str
    raw_line: str
    is_completed: bool = False
    is_parallel: bool = False
    user_story: Optional[str] = None
    phase: Optional[int] = None
    file_path: Optional[str] = None
    
    @classmethod
    def parse_line(cls, line: str, phase: Optional[int] = None) -> Optional["Task"]:
        """
        Parse a task line from tasks.md.
        
        Format: - [ ] T001 [P] [US1] Description with `file/path.ext`
        """
        # Match task pattern
        pattern = r'^- \[([ xX]?)\]\s+(T\d+)\s*(.*)$'
        match = re.match(pattern, line.strip())
        
        if not match:
            return None
        
        status, task_id, rest = match.groups()
        is_completed = status.lower() == 'x'
        
        # Check for parallel marker
        is_parallel = '[P]' in rest
        rest = rest.replace('[P]', '').strip()
        
        # Extract user story reference
        user_story = None
        us_match = re.search(r'\[US(\d+)\]', rest)
        if us_match:
            user_story = f"US{us_match.group(1)}"
            rest = rest.replace(us_match.group(0), '').strip()
        
        # Extract file path
        file_path = None
        path_match = re.search(r'`([^`]+)`', rest)
        if path_match:
            file_path = path_match.group(1)
        
        return cls(
            task_id=task_id,
            description=rest.strip(),
            raw_line=line,
            is_completed=is_completed,
            is_parallel=is_parallel,
            user_story=user_story,
            phase=phase,
            file_path=file_path,
        )


def parse_tasks_file(tasks_file: Path) -> Dict[str, Task]:
    """
    Parse tasks.md and return a dict of task_id -> Task.
    """
    tasks = {}
    current_phase = None
    
    with open(tasks_file, 'r', encoding='utf-8') as f:
        for line in f:
            # Check for phase header
            phase_match = re.match(r'^##\s*Phase\s*(\d+)', line)
            if phase_match:
                current_phase = int(phase_match.group(1))
                continue
            
            # Parse task line
            task = Task.parse_line(line, current_phase)
            if task:
                tasks[task.task_id] = task
    
    return tasks


def get_tasks_by_phase(tasks: Dict[str, Task], phase: int) -> List[Task]:
    """Get all tasks for a specific phase."""
    return [t for t in tasks.values() if t.phase == phase]


# ============================================================================
# Task Executor
# ============================================================================

class TaskExecutor:
    """
    Executes individual tasks using pluggable agent adapters.
    """
    
    def __init__(
        self,
        config: TaskConfig,
        adapter: AgentAdapter,
        spec_dir: str,
        dry_run: bool = False,
    ):
        self.config = config
        self.adapter = adapter
        self.spec_dir = Path(spec_dir)
        self.dry_run = dry_run
        
        # Validate spec directory
        if not self.spec_dir.exists():
            raise ValueError(f"Spec directory does not exist: {spec_dir}")
        
        self.tasks_file = self.spec_dir / "tasks.md"
        if not self.tasks_file.exists():
            raise ValueError(f"tasks.md not found in {spec_dir}")
        
        # Build agent config from base configuration
        model = config.model or adapter.get_default_model()
        
        self.agent_config = AgentConfig(
            model=model,
            timeout_minutes=config.timeout_minutes,
            retry_count=config.retry_count,
            log_level=config.log_level,
        )
        
        # Build permissions from base configuration
        excluded_tools = config.excluded_tools
        if not excluded_tools:
            excluded_tools = adapter.get_default_excluded_tools()
        
        # Get agent-specific config for additional settings
        agent_cfg = config.get_agent_config()
        
        self.permissions = ToolPermissions(
            allow_all=config.allow_tools,
            excluded_tools=excluded_tools,
            allowed_paths=agent_cfg.get("allow_paths", []),
            allowed_urls=agent_cfg.get("allow_urls", []),
        )
        
        # Parse tasks
        self.tasks = parse_tasks_file(self.tasks_file)
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        return self.tasks.get(task_id)
    
    def get_phase_tasks(self, phase: int) -> List[Task]:
        """Get all tasks for a phase."""
        return get_tasks_by_phase(self.tasks, phase)
    
    def execute_task(self, task_id: str) -> bool:
        """
        Execute a single task.
        
        Returns True on success, False on failure.
        """
        task = self.get_task(task_id)
        if task is None:
            log_error(f"Task {task_id} not found in tasks.md")
            return False
        
        if task.is_completed:
            log_info(f"Task {task_id} is already completed, skipping")
            return True
        
        log_info(f"Processing task: {task_id}")
        
        # Prepare log files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sessions_dir = self.spec_dir / "sessions"
        sessions_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = sessions_dir / f"task_{task_id}_{timestamp}.log"
        session_md = sessions_dir / f"task_{task_id}_{timestamp}_session.md"
        
        debug_log_dir = self.spec_dir / "copilot-logs"
        debug_log_dir.mkdir(parents=True, exist_ok=True)
        
        # Build prompt
        prompt = self._build_task_prompt(task)
        
        # Create execution context
        context = ExecutionContext(
            mode=ExecutionMode.TASK,
            spec_dir=str(self.spec_dir),
            task_id=task_id,
            task_info=task.raw_line,
            prompt=prompt,
            session_log_path=str(session_md),
            debug_log_dir=str(debug_log_dir),
            no_ask_user=True,
        )
        
        # Dry run check
        if self.dry_run:
            cmd = self.adapter.build_command(context, self.agent_config, self.permissions)
            print(f"{Colors.YELLOW}[DRY-RUN]{Colors.NC} Would execute task {task_id}:")
            print(f"  Command: {' '.join(cmd)}")
            return True
        
        log_info(f"Executing task {task_id}")
        log_info(f"  Console log: {log_file}")
        log_info(f"  Session markdown: {session_md}")
        log_info(f"  Debug logs: {debug_log_dir}")
        
        # Execute
        result = self.adapter.execute(
            context=context,
            config=self.agent_config,
            permissions=self.permissions,
            log_file=str(log_file),
        )
        
        # Save task status
        self._save_task_status(task_id, result, log_file)
        
        if result.success:
            log_info(f"Task {task_id} completed successfully")
            return True
        else:
            log_error(f"Task {task_id} failed with exit code {result.exit_code}")
            return False
    
    def _build_task_prompt(self, task: Task) -> str:
        """Build the prompt for task execution."""
        prompt_parts = [
            f"Execute task {task.task_id} from {self.spec_dir}/tasks.md:",
            "",
            task.raw_line,
            "",
            f"Follow the implementation plan in {self.spec_dir}/plan.md",
            f"and ensure consistency with {self.spec_dir}/spec.md.",
            "",
            "Mark the task as completed [X] when done.",
        ]
        
        # Add autonomous suffix
        suffix = self.adapter.build_autonomous_suffix("implement")
        if suffix:
            prompt_parts.append("")
            prompt_parts.append(suffix)
        
        return "\n".join(prompt_parts)
    
    def _save_task_status(
        self,
        task_id: str,
        result: ExecutionResult,
        log_file: Path,
    ) -> None:
        """Save task execution status."""
        status_dir = Path(STATE_DIR) / "tasks"
        status_dir.mkdir(parents=True, exist_ok=True)
        
        status = {
            "task_id": task_id,
            "executed_at": datetime.now().isoformat(),
            "log_file": str(log_file),
            "model": self.agent_config.model,
            "spec_dir": str(self.spec_dir),
            "exit_code": result.exit_code,
            "duration_seconds": result.duration_seconds,
        }
        
        status_file = status_dir / f"{task_id}.json"
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status, f, indent=2)
    
    def execute_phase(self, phase: int) -> bool:
        """
        Execute all tasks in a phase.
        
        Respects parallel markers and max_parallel setting.
        Returns True if all tasks succeeded.
        """
        tasks = self.get_phase_tasks(phase)
        
        if not tasks:
            log_warn(f"No tasks found in Phase {phase}")
            return True
        
        log_info(f"Found {len(tasks)} tasks in Phase {phase}")
        
        # Separate parallel and sequential tasks
        parallel_tasks = [t for t in tasks if t.is_parallel and not t.is_completed]
        sequential_tasks = [t for t in tasks if not t.is_parallel and not t.is_completed]
        
        # Execute sequential tasks first
        for task in sequential_tasks:
            if not self.execute_task(task.task_id):
                return False
        
        # Execute parallel tasks with concurrency limit
        if parallel_tasks:
            log_info(f"Executing {len(parallel_tasks)} parallel tasks (max {self.config.max_parallel} concurrent)")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.max_parallel) as executor:
                futures = {
                    executor.submit(self.execute_task, task.task_id): task
                    for task in parallel_tasks
                }
                
                failed = False
                for future in concurrent.futures.as_completed(futures):
                    task = futures[future]
                    try:
                        success = future.result()
                        if not success:
                            log_error(f"Parallel task {task.task_id} failed")
                            failed = True
                    except Exception as e:
                        log_error(f"Parallel task {task.task_id} raised exception: {e}")
                        failed = True
                
                if failed:
                    return False
        
        return True


# ============================================================================
# CLI Interface
# ============================================================================

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Execute individual tasks with vibe coding",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single task execution
  %(prog)s --task T005 --spec-dir spec-vibes/001-feature
  
  # Execute phase with parallelism
  %(prog)s --phase 3 --parallel 4 --spec-dir spec-vibes/001-feature
  
  # With custom model
  %(prog)s --task T001 --model claude-sonnet-4.5 --spec-dir spec-vibes/001-feature
  
  # Dry run to see what would execute
  %(prog)s --task T001 --spec-dir spec-vibes/001-feature --dry-run
"""
    )
    
    # Task selection
    task_group = parser.add_mutually_exclusive_group()
    task_group.add_argument("--task", metavar="ID",
                           help="Execute specific task (e.g., T001)")
    task_group.add_argument("--phase", type=int, metavar="N",
                           help="Execute all tasks in phase N")
    
    # Required options
    parser.add_argument("--spec-dir", required=True, metavar="DIR",
                       help="Spec directory path (in spec-vibes/)")
    
    # Configuration options
    parser.add_argument("--parallel", type=int, metavar="N",
                       help="Max concurrent tasks (default: from config or 3)")
    parser.add_argument("--config", metavar="FILE", default=CONFIG_FILE,
                       help=f"Config file path (default: {CONFIG_FILE})")
    parser.add_argument("--agent", metavar="NAME",
                       help="Override agent adapter")
    parser.add_argument("--model", metavar="MODEL",
                       help="Override model from config")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARN", "ERROR"],
                       help="Set log level")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show command without executing")
    
    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_args()
    
    # Validate inputs
    if not args.task and not args.phase:
        log_error("Either --task or --phase must be specified")
        return 1
    
    # Load configuration
    config = TaskConfig.load(args.config)
    
    # Apply command line overrides
    if args.agent:
        config.agent = args.agent
    if args.log_level:
        config.log_level = args.log_level
    if args.parallel:
        config.max_parallel = args.parallel
    if args.model:
        agent_cfg = config.agent_config.setdefault(config.agent, {})
        agent_cfg["model"] = args.model
    
    # Set log level
    set_log_level(config.log_level)
    
    # Get adapter
    adapter = get_adapter(config.agent)
    if adapter is None:
        log_error(f"Unknown agent adapter: {config.agent}")
        return 1
    
    if not adapter.is_available():
        log_error(f"Agent '{config.agent}' is not available")
        log_error(adapter.get_install_instructions())
        return 1
    
    # Create executor
    try:
        executor = TaskExecutor(
            config=config,
            adapter=adapter,
            spec_dir=args.spec_dir,
            dry_run=args.dry_run,
        )
    except ValueError as e:
        log_error(str(e))
        return 1
    
    log_info("Speckit Vibe Task Executor")
    log_info(f"Agent: {adapter.name}")
    log_info(f"Spec Directory: {args.spec_dir}")
    log_info(f"Model: {executor.agent_config.model}")
    log_info(f"Max Parallel: {config.max_parallel}")
    
    # Execute
    success = False
    
    try:
        if args.task:
            success = executor.execute_task(args.task)
        elif args.phase:
            success = executor.execute_phase(args.phase)
    
    except KeyboardInterrupt:
        log_warn("Execution interrupted by user")
        return 130
    
    except Exception as e:
        log_error(f"Execution failed: {e}")
        if config.log_level == "DEBUG":
            import traceback
            traceback.print_exc()
        return 1
    
    log_info("Task execution completed")
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
