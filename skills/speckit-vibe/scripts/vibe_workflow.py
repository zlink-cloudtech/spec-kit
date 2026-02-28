#!/usr/bin/env python3
"""
vibe_workflow.py - Main workflow orchestrator for speckit vibe coding

This script orchestrates the speckit-vibe workflow stages using pluggable
agent adapters. It supports multiple execution modes:
- Autonomous: Full automated workflow without user interaction  
- Resume: Continue from last incomplete stage

IMPORTANT: Requirements gathering should be done by the Agent directly
in conversation with the user. This script handles ONLY the automated
execution of the workflow stages.

Usage:
    vibe_workflow.py [OPTIONS]

Examples:
    # Full autonomous workflow from spec (after Agent creates SPECIFICATION.md)
    vibe_workflow.py --auto --spec SPECIFICATION.md
    
    # Resume interrupted workflow
    vibe_workflow.py --resume --spec-dir spec-vibes/001-oauth2
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

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
    list_adapters,
)

# ============================================================================
# Constants
# ============================================================================

WORKFLOW_STAGES = ["specify", "clarify", "plan", "tasks", "checklist", "analyze", "implement"]
CONFIG_FILE = ".speckit-vc.json"
STATE_DIR = ".speckit-vc"
DEFAULT_SPECS_DIR = "specs"

# ANSI Colors
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color


# ============================================================================
# Configuration
# ============================================================================

@dataclass
class WorkflowConfig:
    """Workflow configuration loaded from .speckit-vc.json"""
    # Agent selection
    agent: str = "copilot"
    
    # Base agent configuration (all adapters handle these)
    model: str = "claude-sonnet-4.5"
    allow_tools: bool = True
    excluded_tools: List[str] = field(default_factory=lambda: ["skill(speckit-vibe)"])
    
    # Agent-agnostic workflow settings
    log_level: str = "INFO"
    max_parallel: int = 3
    auto_learning: bool = True
    agents_md_path: str = "AGENTS.md"
    timeout_minutes: int = 30
    retry_count: int = 2
    session_isolation: bool = True
    specs_dir: str = DEFAULT_SPECS_DIR
    
    # Agent-specific configurations (for truly agent-specific settings)
    agent_config: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    @classmethod
    def load(cls, config_file: str = CONFIG_FILE) -> "WorkflowConfig":
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
                auto_learning=data.get("auto_learning", True),
                agents_md_path=data.get("agents_md_path", "AGENTS.md"),
                timeout_minutes=data.get("timeout_minutes", 30),
                retry_count=data.get("retry_count", 2),
                session_isolation=data.get("session_isolation", True),
                specs_dir=data.get("specs_dir", DEFAULT_SPECS_DIR),
                agent_config=data.get("agent_config", {}),
            )
        except json.JSONDecodeError as e:
            log_error(f"Invalid JSON in {config_file}: {e}")
            sys.exit(1)
    
    def get_agent_config(self) -> Dict[str, Any]:
        """Get configuration for the currently selected agent."""
        return self.agent_config.get(self.agent, {})


# ============================================================================
# Logging
# ============================================================================

LOG_LEVEL = "INFO"

def set_log_level(level: str) -> None:
    """Set global log level."""
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

def log_stage(msg: str) -> None:
    print(f"{Colors.CYAN}[STAGE]{Colors.NC} {msg}", file=sys.stderr)


# ============================================================================
# State Management
# ============================================================================

@dataclass
class WorkflowState:
    """Workflow state persisted to state.json"""
    workflow_id: str
    started_at: str
    updated_at: Optional[str] = None
    current_stage: Optional[str] = None
    completed_stages: List[str] = field(default_factory=list)
    failed_stage: Optional[str] = None
    failed_at: Optional[str] = None
    spec_dir: Optional[str] = None
    requirement: Optional[str] = None
    
    @classmethod
    def load(cls, state_file: str = f"{STATE_DIR}/state.json") -> Optional["WorkflowState"]:
        """Load state from file."""
        state_path = Path(state_file)
        if not state_path.exists():
            return None
        
        try:
            with open(state_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls(**data)
        except (json.JSONDecodeError, TypeError):
            return None
    
    def save(self, state_file: str = f"{STATE_DIR}/state.json") -> None:
        """Save state to file."""
        state_path = Path(state_file)
        state_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.updated_at = datetime.now().isoformat()
        
        with open(state_path, 'w', encoding='utf-8') as f:
            json.dump(self.__dict__, f, indent=2)
    
    def mark_started(self, stage: str) -> None:
        """Mark a stage as started."""
        self.current_stage = stage
        self.save()
    
    def mark_completed(self, stage: str) -> None:
        """Mark a stage as completed."""
        if stage not in self.completed_stages:
            self.completed_stages.append(stage)
        self.current_stage = None
        self.save()
    
    def mark_failed(self, stage: str) -> None:
        """Mark a stage as failed."""
        self.current_stage = None
        self.failed_stage = stage
        self.failed_at = datetime.now().isoformat()
        self.save()
    
    def get_next_stage(self) -> Optional[str]:
        """Get the next stage to execute."""
        for stage in WORKFLOW_STAGES:
            if stage not in self.completed_stages:
                return stage
        return None


# ============================================================================
# Spec Directory Management
# ============================================================================

def create_spec_dir(specs_dir: str, requirement: str) -> str:
    """
    Create a new specs session directory.
    
    Format: specs/NNN-short-name/
    """
    base_dir = Path(specs_dir)
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Find next available number
    next_num = 1
    for d in base_dir.glob("[0-9][0-9][0-9]-*"):
        if d.is_dir():
            try:
                num = int(d.name[:3])
                if num >= next_num:
                    next_num = num + 1
            except ValueError:
                pass
    
    # Generate short name from requirement
    short_name = re.sub(r'[^a-z0-9 ]', '', requirement.lower())
    words = short_name.split()[:3]
    short_name = '-'.join(words)[:30].rstrip('-') or "feature"
    
    # Create directory
    dir_name = f"{next_num:03d}-{short_name}"
    spec_dir = base_dir / dir_name
    
    spec_dir.mkdir(parents=True, exist_ok=True)
    (spec_dir / "sessions").mkdir(exist_ok=True)
    (spec_dir / "checklists").mkdir(exist_ok=True)
    (spec_dir / "copilot-logs").mkdir(exist_ok=True)
    
    # Update latest symlink
    latest_link = base_dir / ".latest"
    if latest_link.exists() or latest_link.is_symlink():
        latest_link.unlink()
    latest_link.symlink_to(dir_name)
    
    log_info(f"Created vibe session directory: {spec_dir}")
    return str(spec_dir)


def show_workflow_status(state: WorkflowState) -> None:
    """Display current workflow status."""
    print(f"Spec Directory: {state.spec_dir or 'N/A'}")
    print(f"Workflow ID: {state.workflow_id}")
    print()
    print("Stage Status:")
    
    completed = set(state.completed_stages)
    
    for stage in WORKFLOW_STAGES:
        if stage in completed:
            status = "✅ completed"
        elif stage == state.failed_stage:
            status = "❌ failed"
        elif stage == state.current_stage:
            status = "🔄 in progress"
        else:
            status = "⏳ pending"
        print(f"  {stage}: {status}")
    
    next_stage = state.get_next_stage()
    if next_stage:
        print()
        print(f"Next stage to run: {next_stage}")
    else:
        print()
        print("All stages completed!")


# ============================================================================
# Workflow Executor
# ============================================================================

class WorkflowExecutor:
    """
    Orchestrates the speckit-vibe workflow using pluggable agent adapters.
    """
    
    def __init__(
        self,
        config: WorkflowConfig,
        adapter: AgentAdapter,
        spec_dir: Optional[str] = None,
        dry_run: bool = False,
    ):
        self.config = config
        self.adapter = adapter
        self.spec_dir = spec_dir
        self.dry_run = dry_run
        self.state: Optional[WorkflowState] = None
        
        # Build agent config from base configuration
        # Adapter can override with its default if base config is not set
        model = config.model or adapter.get_default_model()
        
        self.agent_config = AgentConfig(
            model=model,
            timeout_minutes=config.timeout_minutes,
            retry_count=config.retry_count,
            log_level=config.log_level,
        )
        
        # Build permissions from base configuration
        # Adapter provides defaults, config can override
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
    
    def init_state(self, requirement: Optional[str] = None) -> WorkflowState:
        """Initialize or load workflow state."""
        # Try to load existing state
        self.state = WorkflowState.load()
        
        if self.state is None:
            # Create new state
            self.state = WorkflowState(
                workflow_id=datetime.now().strftime("%Y%m%d_%H%M%S"),
                started_at=datetime.now().isoformat(),
                spec_dir=self.spec_dir,
                requirement=requirement,
            )
            Path(STATE_DIR).mkdir(parents=True, exist_ok=True)
            (Path(STATE_DIR) / "sessions").mkdir(exist_ok=True)
            (Path(STATE_DIR) / "learnings").mkdir(exist_ok=True)
            self.state.save()
        
        return self.state
    
    def execute_stage(
        self,
        stage: str,
        args: str = "",
        autonomous: bool = True,
    ) -> bool:
        """
        Execute a single workflow stage.
        
        Returns True on success, False on failure.
        """
        log_stage(f"=== Executing Stage: {stage} ===")
        
        if self.state is None:
            self.init_state()
        
        # Prepare log files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if self.spec_dir and Path(self.spec_dir).exists():
            sessions_dir = Path(self.spec_dir) / "sessions"
            debug_log_dir = Path(self.spec_dir) / "copilot-logs"
        else:
            sessions_dir = Path(STATE_DIR) / "sessions"
            debug_log_dir = None
        
        sessions_dir.mkdir(parents=True, exist_ok=True)
        log_file = sessions_dir / f"stage_{stage}_{timestamp}.log"
        session_md = sessions_dir / f"stage_{stage}_{timestamp}_session.md"
        
        # Build autonomous suffix
        autonomous_suffix = ""
        if autonomous:
            autonomous_suffix = self.adapter.build_autonomous_suffix(stage)
        
        # Create execution context
        context = ExecutionContext(
            mode=ExecutionMode.STAGE,
            spec_dir=self.spec_dir or "",
            stage=stage,
            session_log_path=str(session_md),
            debug_log_dir=str(debug_log_dir) if debug_log_dir else None,
            no_ask_user=autonomous,
            autonomous_suffix=autonomous_suffix,
        )
        
        # Dry run check
        if self.dry_run:
            cmd = self.adapter.build_command(context, self.agent_config, self.permissions)
            print(f"{Colors.YELLOW}[DRY-RUN]{Colors.NC} Would execute stage: {stage}")
            print(f"  Command: {' '.join(cmd)}")
            return True
        
        # Update state
        self.state.mark_started(stage)
        
        log_info(f"Stage {stage} started")
        log_info(f"  Console log: {log_file}")
        log_info(f"  Session markdown: {session_md}")
        if debug_log_dir:
            log_info(f"  Debug logs: {debug_log_dir}")
        
        # Execute
        result = self.adapter.execute(
            context=context,
            config=self.agent_config,
            permissions=self.permissions,
            log_file=str(log_file),
        )
        
        if result.success:
            self.state.mark_completed(stage)
            log_info(f"Stage {stage} completed successfully")
            return True
        else:
            self.state.mark_failed(stage)
            log_error(f"Stage {stage} failed with exit code {result.exit_code}")
            if result.stderr:
                log_error(f"  Error: {result.stderr[:200]}")
            return False
    
    def run_autonomous_workflow(
        self,
        start_stage: Optional[str] = None,
        spec_file: Optional[str] = None,
        requirement: Optional[str] = None,
    ) -> bool:
        """
        Run the full autonomous workflow.
        
        Returns True on success, False on failure.
        """
        log_stage("=== Starting Autonomous Workflow ===")
        
        # Initialize state
        self.init_state(requirement)
        
        # Find starting stage index
        start_index = 0
        if start_stage:
            try:
                start_index = WORKFLOW_STAGES.index(start_stage)
                log_info(f"Starting from stage: {start_stage} (index: {start_index})")
            except ValueError:
                log_error(f"Invalid stage: {start_stage}")
                return False
        
        # Execute stages
        for i in range(start_index, len(WORKFLOW_STAGES)):
            stage = WORKFLOW_STAGES[i]
            args = ""
            
            # Handle specify stage specially
            if stage == "specify":
                if spec_file:
                    args = spec_file
                elif requirement:
                    args = requirement
            
            # Handle implement stage - delegate to vibe_task.py
            if stage == "implement":
                log_stage("=== Implementation Phase (Parallel Tasks) ===")
                if not self._run_implementation():
                    return False
                continue
            
            # Execute stage
            if not self.execute_stage(stage, args):
                log_error(f"Workflow failed at stage: {stage}")
                return False
            
            # Update spec_dir after specify stage if needed
            if stage == "specify" and not self.spec_dir:
                self._detect_spec_dir()
        
        log_stage("=== Workflow Completed Successfully ===")
        return True
    
    def _run_implementation(self) -> bool:
        """Run the implementation phase using vibe_task.py."""
        if self.dry_run:
            print(f"{Colors.YELLOW}[DRY-RUN]{Colors.NC} Would execute implementation phase")
            return True
        
        if not self.spec_dir:
            log_error("Cannot determine spec directory for implementation")
            return False
        
        # Import and use vibe_task module
        try:
            from vibe_task import TaskExecutor
            
            executor = TaskExecutor(
                config=self.config,
                adapter=self.adapter,
                spec_dir=self.spec_dir,
                dry_run=self.dry_run,
            )
            
            # Execute phases sequentially
            phase = 1
            while phase <= 20:  # Safety limit
                tasks = executor.get_phase_tasks(phase)
                if not tasks:
                    break
                
                log_info(f"Executing Phase {phase} tasks...")
                if not executor.execute_phase(phase):
                    log_error(f"Phase {phase} failed")
                    return False
                
                phase += 1
            
            return True
            
        except ImportError:
            log_warn("vibe_task module not available, skipping implementation")
            return True
    
    def _detect_spec_dir(self) -> None:
        """Detect spec directory after specify stage."""
        # This would typically detect from git branch or other sources
        # For now, use the state's spec_dir if set
        if self.state and self.state.spec_dir:
            self.spec_dir = self.state.spec_dir


# ============================================================================
# CLI Interface
# ============================================================================

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Orchestrate the speckit vibe coding workflow (autonomous execution only)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Workflow Stages:
  specify    - Convert requirements to spec.md
  clarify    - Clarify and refine spec.md
  plan       - Generate technical plan.md
  tasks      - Create tasks.md with actionable items
  checklist  - Generate quality checklists
  analyze    - Analyze consistency across artifacts
  implement  - Execute tasks with parallel support

IMPORTANT: Requirements gathering should be done by the Agent in conversation.
This script handles ONLY the automated execution of workflow stages.

Examples:
  # Full autonomous workflow from spec (Agent creates SPECIFICATION.md first)
  %(prog)s --auto --spec SPECIFICATION.md
  
  # Resume interrupted workflow
  %(prog)s --resume --spec-dir spec-vibes/001-oauth2
  
  # Start from specific stage
  %(prog)s --stage implement --spec-dir spec-vibes/001-oauth2
"""
    )
    
    # Mode options
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--auto", action="store_true",
                           help="Run full autonomous workflow without interaction")
    mode_group.add_argument("--resume", action="store_true",
                           help="Resume from last incomplete stage")
    mode_group.add_argument("--reanalyze", action="store_true",
                           help="Re-run analyze and update artifacts")
    
    # Input options
    parser.add_argument("--spec", metavar="FILE",
                       help="Use existing SPECIFICATION.md file")
    parser.add_argument("--spec-dir", metavar="DIR",
                       help="Use existing spec directory")
    parser.add_argument("--stage", metavar="STAGE", choices=WORKFLOW_STAGES,
                       help="Start from specific stage")
    
    # Configuration options
    parser.add_argument("--config", metavar="FILE", default=CONFIG_FILE,
                       help=f"Config file path (default: {CONFIG_FILE})")
    parser.add_argument("--agent", metavar="NAME",
                       help="Override agent adapter (e.g., copilot)")
    parser.add_argument("--model", metavar="MODEL",
                       help="Override model from config")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARN", "ERROR"],
                       help="Set log level")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be executed without running")
    
    # Utility options
    parser.add_argument("--status", action="store_true",
                       help="Show workflow status and exit")
    parser.add_argument("--list-adapters", action="store_true",
                       help="List available agent adapters and exit")
    
    # Positional argument (kept for backward compatibility, but deprecated)
    parser.add_argument("requirement", nargs="?",
                       help="(Deprecated) Feature requirement - use Agent conversation instead")
    
    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_args()
    
    # Handle utility commands first
    if args.list_adapters:
        print("Available Agent Adapters:")
        print("-" * 40)
        for name, available in list_adapters().items():
            status = "✓ available" if available else "✗ not installed"
            print(f"  {name}: {status}")
        return 0
    
    # Load configuration
    config = WorkflowConfig.load(args.config)
    
    # Apply command line overrides
    if args.agent:
        config.agent = args.agent
    if args.log_level:
        config.log_level = args.log_level
    if args.model:
        agent_cfg = config.agent_config.setdefault(config.agent, {})
        agent_cfg["model"] = args.model
    
    # Set log level
    set_log_level(config.log_level)
    
    # Get adapter
    adapter = get_adapter(config.agent)
    if adapter is None:
        log_error(f"Unknown agent adapter: {config.agent}")
        log_error(f"Available adapters: {list(list_adapters().keys())}")
        return 1
    
    if not adapter.is_available():
        log_error(f"Agent '{config.agent}' is not available")
        log_error(adapter.get_install_instructions())
        return 1
    
    # Handle status command
    if args.status:
        state = WorkflowState.load()
        if state:
            show_workflow_status(state)
        else:
            log_info("No workflow state found")
        return 0
    
    # Determine spec directory
    spec_dir = args.spec_dir
    
    # Handle resume mode
    if args.resume:
        state = WorkflowState.load()
        if state is None:
            log_error("No workflow state found. Cannot resume.")
            return 1
        
        show_workflow_status(state)
        
        next_stage = state.get_next_stage()
        if next_stage is None:
            log_info("All stages completed!")
            return 0
        
        log_info(f"Resuming from stage: {next_stage}")
        spec_dir = spec_dir or state.spec_dir
        args.stage = next_stage
        args.auto = True
    
    # Create spec directory if needed
    if spec_dir is None and (args.requirement or args.spec):
        requirement = args.requirement or Path(args.spec).stem if args.spec else "feature"
        spec_dir = create_spec_dir(config.specs_dir, requirement)
        
        # Copy spec file if provided
        if args.spec and Path(args.spec).exists():
            import shutil
            dest = Path(spec_dir) / "SPECIFICATION.md"
            shutil.copy(args.spec, dest)
            log_info(f"Copied {args.spec} to {dest}")
    
    # Validate inputs
    if not any([args.auto, args.resume, args.reanalyze,
                spec_dir, args.spec, args.requirement]):
        log_error("Please provide a requirement, --spec file, or --spec-dir")
        return 1
    
    # Create executor
    executor = WorkflowExecutor(
        config=config,
        adapter=adapter,
        spec_dir=spec_dir,
        dry_run=args.dry_run,
    )
    
    log_info("Speckit Vibe Workflow Orchestrator")
    log_info(f"Agent: {adapter.name}")
    log_info(f"Model: {executor.agent_config.model}")
    log_info(f"Config: {args.config}")
    
    # Warn if using deprecated requirement argument
    if args.requirement:
        log_warn("Positional requirement argument is deprecated.")
        log_warn("Requirements gathering should be done by the Agent in conversation.")
        log_warn("The workflow will continue using the provided requirement for backward compatibility.")
    
    # Execute appropriate workflow
    success = False
    
    try:
        if args.reanalyze:
            if not spec_dir:
                log_error("--spec-dir is required for --reanalyze")
                return 1
            success = executor.execute_stage("analyze")
        
        elif args.auto or spec_dir or args.spec or args.requirement:
            # Run autonomous workflow
            success = executor.run_autonomous_workflow(
                start_stage=args.stage,
                spec_file=args.spec,
                requirement=args.requirement,
            )
        
        else:
            log_error("No action specified. Use --auto --spec <file> or --resume")
            log_error("Requirements gathering should be done by the Agent in conversation.")
            return 1
    
    except KeyboardInterrupt:
        log_warn("Workflow interrupted by user")
        return 130
    
    except Exception as e:
        log_error(f"Workflow failed: {e}")
        if config.log_level == "DEBUG":
            import traceback
            traceback.print_exc()
        return 1
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
