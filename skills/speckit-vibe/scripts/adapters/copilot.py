"""
GitHub Copilot CLI adapter for speckit-vibe.

This adapter implements the AgentAdapter interface for GitHub Copilot CLI,
translating agent-agnostic execution requests into Copilot-specific commands.

Copilot CLI Reference:
    copilot --model MODEL [OPTIONS] -p "PROMPT"
    
Key Flags:
    --model MODEL           AI model to use
    --allow-all             Allow all tools
    --excluded-tools TOOL   Exclude specific tool
    --no-ask-user           Disable user prompts
    --log-level LEVEL       Set log verbosity
    --log-dir PATH          Debug log directory
    --share PATH            Export session to markdown
    --allow-path PATH       Allow file access
    --allow-url URL         Allow URL access
    --stream off            Disable streaming output
    -p "PROMPT"             Initial prompt
"""

from typing import List
import shutil

from .base import (
    AgentAdapter,
    AgentConfig,
    ExecutionContext,
    ExecutionMode,
    ToolPermissions,
)


class CopilotAdapter(AgentAdapter):
    """
    GitHub Copilot CLI adapter.
    
    Translates speckit-vibe execution requests into Copilot CLI commands.
    Supports workflow stages, task execution, and interactive sessions.
    """
    
    @property
    def name(self) -> str:
        return "copilot"
    
    @property
    def executable(self) -> str:
        return "copilot"
    
    @property
    def description(self) -> str:
        return "GitHub Copilot CLI adapter for VS Code integration"
    
    def is_available(self) -> bool:
        """Check if copilot CLI is installed."""
        return shutil.which("copilot") is not None
    
    def get_default_model(self) -> str:
        """Default to Claude Sonnet 4.5 for best coding performance."""
        return "claude-sonnet-4.5"
    
    def get_default_excluded_tools(self) -> List[str]:
        """Exclude speckit-vibe skill to avoid recursion."""
        return ["skill(speckit-vibe)"]
    
    def get_install_instructions(self) -> str:
        return (
            "GitHub Copilot CLI is not installed or not in PATH.\n"
            "To install:\n"
            "  1. Ensure you have VS Code with GitHub Copilot extension\n"
            "  2. Install the CLI: npm install -g @anthropic-ai/copilot\n"
            "  3. Authenticate: copilot auth login\n"
            "\n"
            "For more information, see: https://docs.github.com/copilot/cli"
        )
    
    def build_autonomous_suffix(self, stage: str) -> str:
        """
        Build prompt suffix for autonomous (no-ask-user) execution.
        
        This suffix instructs Copilot to operate without user interaction,
        making reasonable assumptions and proceeding with the workflow.
        
        Args:
            stage: Workflow stage name (e.g., "clarify", "implement")
            
        Returns:
            Prompt suffix with autonomous mode instructions
        """
        # Base autonomous instructions
        suffix_parts = [
            "-- [AUTONOMOUS VIBE MODE] CRITICAL:",
            "1) DO NOT ask user questions - decide yourself.",
            "2) DO NOT skip steps or request confirmation.",
            "3) Make reasonable assumptions and document them.",
            "4) Complete ALL work without asking for approval.",
        ]
        
        # Stage-specific hints
        stage_hints = {
            "clarify": (
                "For CLARIFY: Identify ambiguities, resolve them yourself with "
                "documented assumptions, update spec.md with clarifications."
            ),
            "plan": (
                "For PLAN: Create comprehensive technical plan covering architecture, "
                "implementation approach, and risk mitigation."
            ),
            "tasks": (
                "For TASKS: Generate all tasks with proper dependencies, phases, "
                "and parallel execution markers [P] where safe."
            ),
            "checklist": (
                "For CHECKLIST: Generate all validation items without asking priorities. "
                "Include unit tests, integration tests, and edge cases."
            ),
            "analyze": (
                "For ANALYZE: Check consistency across all artifacts, identify gaps, "
                "and update documents to ensure alignment."
            ),
            "implement": (
                "For IMPLEMENT: Execute ALL tasks in dependency order. "
                "Respect [P] markers for parallel execution. "
                "Mark tasks complete [X] as you finish them."
            ),
        }
        
        if stage in stage_hints:
            suffix_parts.append(stage_hints[stage])
        
        return " ".join(suffix_parts)
    
    def build_command(
        self,
        context: ExecutionContext,
        config: AgentConfig,
        permissions: ToolPermissions
    ) -> List[str]:
        """
        Build Copilot CLI command.
        
        Args:
            context: Execution context (mode, stage, task, etc.)
            config: Agent configuration (model, timeout, etc.)
            permissions: Tool permissions
            
        Returns:
            Command as list of strings for subprocess
        """
        cmd = [self.executable]
        
        # Model selection
        cmd.extend(["--model", config.model])
        
        # Tool permissions
        if permissions.allow_all:
            cmd.append("--allow-all")
        
        # Excluded tools
        for tool in permissions.excluded_tools:
            cmd.extend(["--excluded-tools", tool])
        
        # Allowed paths
        for path in permissions.allowed_paths:
            cmd.extend(["--allow-path", path])
        
        # Allowed URLs
        for url in permissions.allowed_urls:
            cmd.extend(["--allow-url", url])
        
        # No-ask-user mode (required for autonomous operation)
        if context.no_ask_user:
            cmd.append("--no-ask-user")
        
        # Debug logging
        if context.debug_log_dir:
            cmd.extend(["--log-level", "debug"])
            cmd.extend(["--log-dir", context.debug_log_dir])
        
        # Session export to markdown
        if context.session_log_path:
            cmd.extend(["--share", context.session_log_path])
        
        # Disable streaming for vibe coding (better for logging)
        cmd.extend(["--stream", "off"])
        
        # Build prompt based on execution mode
        prompt = self._build_prompt(context)
        cmd.extend(["-p", prompt])
        
        return cmd
    
    def _build_prompt(self, context: ExecutionContext) -> str:
        """
        Build prompt based on execution context.
        
        Args:
            context: Execution context
            
        Returns:
            Prompt string for Copilot
        """
        if context.mode == ExecutionMode.STAGE:
            # Workflow stage execution using slash command
            prompt = f"/speckit.{context.stage}"
            if context.autonomous_suffix:
                prompt = f"{prompt} {context.autonomous_suffix}"
            return prompt
        
        elif context.mode == ExecutionMode.TASK:
            # Task execution with full context
            prompt_parts = [
                f"Execute task {context.task_id} from {context.spec_dir}/tasks.md:",
                "",
                context.task_info or "",
                "",
                f"Follow the implementation plan in {context.spec_dir}/plan.md",
                f"and ensure consistency with {context.spec_dir}/spec.md.",
                "",
                "Mark the task as completed [X] when done.",
            ]
            if context.autonomous_suffix:
                prompt_parts.append("")
                prompt_parts.append(context.autonomous_suffix)
            return "\n".join(prompt_parts)
        
        else:
            # Fallback: use custom prompt if provided
            return context.prompt or ""
    
    def validate_config(self, config: AgentConfig) -> List[str]:
        """
        Validate Copilot-specific configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            List of validation error messages
        """
        errors = super().validate_config(config)
        
        # Copilot-specific validations
        known_models = [
            "claude-sonnet-4.5",
            "claude-sonnet-4-20250514",
            "gpt-4o",
            "gpt-4-turbo",
            "gpt-4",
        ]
        
        # Warn if model is not in known list (but don't fail)
        if config.model and config.model not in known_models:
            # Not an error, just a note - models may be added
            pass
        
        return errors
