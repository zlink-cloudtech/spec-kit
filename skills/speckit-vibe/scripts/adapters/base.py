"""
Base classes for agent adapters.

This module defines the abstract interface that all agent adapters must implement,
along with common data structures used across the adapter layer.

All classes use Python standard library only (dataclasses, abc, subprocess, etc.)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
import shlex
import shutil
import subprocess
import time


class ExecutionMode(Enum):
    """Mode of agent execution."""
    STAGE = "stage"           # Workflow stage execution (specify, clarify, plan, etc.)
    TASK = "task"             # Individual task execution
    # Note: INTERACTIVE mode has been deprecated. Requirements gathering should
    # be done by the Agent directly in conversation with the user.


@dataclass
class AgentConfig:
    """
    Configuration for agent execution.
    
    Attributes:
        model: AI model to use (agent-specific format)
        timeout_minutes: Maximum execution time
        retry_count: Number of retries on failure
        log_level: Logging verbosity (DEBUG, INFO, WARN, ERROR)
        extra: Agent-specific additional configuration
    """
    model: str
    timeout_minutes: int = 30
    retry_count: int = 2
    log_level: str = "INFO"
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolPermissions:
    """
    Tool/capability permissions for agent execution.
    
    Attributes:
        allow_all: Whether to allow all tools (agent may ignore specific lists)
        allowed_tools: Explicit list of allowed tools
        excluded_tools: Tools to exclude (e.g., self to avoid recursion)
        allowed_paths: File paths the agent can access
        allowed_urls: URLs the agent can fetch
    """
    allow_all: bool = True
    allowed_tools: List[str] = field(default_factory=list)
    excluded_tools: List[str] = field(default_factory=list)
    allowed_paths: List[str] = field(default_factory=list)
    allowed_urls: List[str] = field(default_factory=list)


@dataclass
class ExecutionContext:
    """
    Context for a single agent execution.
    
    Attributes:
        mode: Execution mode (stage or task)
        spec_dir: Path to the specification directory
        stage: Workflow stage name (for STAGE mode)
        task_id: Task identifier (for TASK mode)
        task_info: Task description/details (for TASK mode)
        prompt: Custom prompt (optional, for specialized execution)
        session_log_path: Path to save session transcript
        debug_log_dir: Directory for debug logs
        no_ask_user: Whether to suppress user prompts (always True for autonomous)
        autonomous_suffix: Additional instructions for autonomous mode
    """
    mode: ExecutionMode
    spec_dir: str
    stage: Optional[str] = None
    task_id: Optional[str] = None
    task_info: Optional[str] = None
    prompt: Optional[str] = None
    session_log_path: Optional[str] = None
    debug_log_dir: Optional[str] = None
    no_ask_user: bool = True  # Always True for autonomous workflow
    autonomous_suffix: str = ""


@dataclass
class ExecutionResult:
    """
    Result of agent execution.
    
    Attributes:
        exit_code: Process exit code (0 = success)
        stdout: Standard output content
        stderr: Standard error content
        command: Command that was executed (for debugging)
        duration_seconds: Execution time
        log_files: Mapping of log type to file path
    """
    exit_code: int
    stdout: str
    stderr: str
    command: str
    duration_seconds: float
    log_files: Dict[str, str] = field(default_factory=dict)
    
    @property
    def success(self) -> bool:
        """Check if execution was successful."""
        return self.exit_code == 0


class AgentAdapter(ABC):
    """
    Abstract base class for AI agent CLI adapters.
    
    Each adapter translates agent-agnostic execution requests
    into agent-specific CLI commands. Subclasses must implement
    all abstract methods to support a new agent.
    
    Example:
        class MyAgentAdapter(AgentAdapter):
            @property
            def name(self) -> str:
                return "my-agent"
            
            @property  
            def executable(self) -> str:
                return "my-agent-cli"
            
            # ... implement other abstract methods
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Unique identifier for this agent.
        
        This is used in configuration files and CLI arguments
        to select the adapter.
        
        Returns:
            Agent name (e.g., "copilot", "claude-code")
        """
        pass
    
    @property
    @abstractmethod
    def executable(self) -> str:
        """
        CLI executable name or path.
        
        Returns:
            Executable name that can be found in PATH,
            or absolute path to the executable.
        """
        pass
    
    @property
    def description(self) -> str:
        """
        Human-readable description of this agent.
        
        Returns:
            Description string (default: agent name)
        """
        return f"{self.name} agent adapter"
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if agent CLI is installed and accessible.
        
        Returns:
            True if the agent can be used, False otherwise.
        """
        pass
    
    @abstractmethod
    def get_default_model(self) -> str:
        """
        Return default model for this agent.
        
        Returns:
            Model identifier string (agent-specific format)
        """
        pass
    
    @abstractmethod
    def get_default_excluded_tools(self) -> List[str]:
        """
        Return default excluded tools.
        
        Typically includes self-exclusion to avoid recursion.
        
        Returns:
            List of tool identifiers to exclude by default.
        """
        pass
    
    @abstractmethod
    def build_command(
        self,
        context: ExecutionContext,
        config: AgentConfig,
        permissions: ToolPermissions
    ) -> List[str]:
        """
        Build command as list of arguments.
        
        Uses list format for subprocess safety (avoids shell injection).
        
        Args:
            context: Execution context with mode, stage/task info, etc.
            config: Agent configuration (model, timeout, etc.)
            permissions: Tool permissions
            
        Returns:
            Command as list of strings for subprocess.
        """
        pass
    
    @abstractmethod
    def build_autonomous_suffix(self, stage: str) -> str:
        """
        Build prompt suffix for autonomous execution.
        
        This suffix instructs the agent to operate without
        user interaction, making reasonable assumptions.
        
        Args:
            stage: Workflow stage name
            
        Returns:
            Prompt suffix string
        """
        pass
    
    def get_install_instructions(self) -> str:
        """
        Return installation instructions for this agent.
        
        Shown to users when the agent is not available.
        
        Returns:
            Installation instructions string
        """
        return f"Please install {self.name} CLI and ensure it's in your PATH."
    
    def validate_config(self, config: AgentConfig) -> List[str]:
        """
        Validate agent configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        if not config.model:
            errors.append("Model must be specified")
        if config.timeout_minutes < 1:
            errors.append("Timeout must be at least 1 minute")
        if config.retry_count < 0:
            errors.append("Retry count cannot be negative")
        return errors
    
    def execute(
        self,
        context: ExecutionContext,
        config: AgentConfig,
        permissions: ToolPermissions,
        log_file: Optional[str] = None,
        dry_run: bool = False
    ) -> ExecutionResult:
        """
        Execute the agent with given context.
        
        Default implementation using subprocess. Can be overridden
        for agent-specific behavior (e.g., API calls instead of CLI).
        
        For interactive mode (no_ask_user=False), the process runs with
        direct terminal access so users can interact with the agent.
        
        Args:
            context: Execution context
            config: Agent configuration
            permissions: Tool permissions
            log_file: Optional path to write execution log
            dry_run: If True, show command without executing
            
        Returns:
            ExecutionResult with output and status
        """
        cmd = self.build_command(context, config, permissions)
        cmd_str = shlex.join(cmd)
        
        if dry_run:
            return ExecutionResult(
                exit_code=0,
                stdout=f"[DRY-RUN] Would execute:\n{cmd_str}",
                stderr="",
                command=cmd_str,
                duration_seconds=0.0
            )
        
        start_time = time.time()
        
        # Ensure log directory exists
        if log_file:
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Check if this is an interactive session
        # Note: INTERACTIVE mode was deprecated, so only check no_ask_user flag
        is_interactive = not context.no_ask_user
        
        try:
            if is_interactive:
                # Interactive mode: let terminal handle I/O directly
                # User can see output and provide input
                import sys
                process = subprocess.run(
                    cmd,
                    stdin=sys.stdin,
                    stdout=sys.stdout,
                    stderr=sys.stderr,
                    timeout=config.timeout_minutes * 60
                )
                exit_code = process.returncode
                stdout = "[Interactive session - output displayed in terminal]"
                stderr = ""
            else:
                # Non-interactive mode: capture output for logging
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=config.timeout_minutes * 60
                )
                exit_code = process.returncode
                stdout = process.stdout
                stderr = process.stderr
            
        except subprocess.TimeoutExpired:
            exit_code = 124  # Standard timeout exit code
            stdout = ""
            stderr = f"Execution timed out after {config.timeout_minutes} minutes"
            
        except FileNotFoundError:
            exit_code = 127  # Command not found
            stdout = ""
            stderr = f"Agent executable not found: {self.executable}\n{self.get_install_instructions()}"
            
        except Exception as e:
            exit_code = 1
            stdout = ""
            stderr = f"Execution error: {str(e)}"
        
        duration = time.time() - start_time
        
        # Write to log file if specified
        log_files = {}
        if log_file:
            try:
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.write(f"=== Execution Log ===\n")
                    f.write(f"Agent: {self.name}\n")
                    f.write(f"Command: {cmd_str}\n")
                    f.write(f"Exit Code: {exit_code}\n")
                    f.write(f"Duration: {duration:.2f}s\n")
                    f.write(f"Mode: {'interactive' if is_interactive else 'autonomous'}\n")
                    f.write(f"\n=== STDOUT ===\n{stdout}\n")
                    f.write(f"\n=== STDERR ===\n{stderr}\n")
                log_files["main"] = log_file
            except IOError:
                pass  # Ignore log write failures
        
        return ExecutionResult(
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            command=cmd_str,
            duration_seconds=duration,
            log_files=log_files
        )
    
    def __repr__(self) -> str:
        available = "available" if self.is_available() else "not available"
        return f"<{self.__class__.__name__}({self.name}, {available})>"
