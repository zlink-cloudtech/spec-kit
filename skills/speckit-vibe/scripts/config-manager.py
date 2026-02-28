#!/usr/bin/env python3
"""
config-manager.py - Manage .speckit-vc.json configuration

Usage:
    config-manager.py init                 Create default config file
    config-manager.py show                 Display current config
    config-manager.py set KEY VALUE        Set config value
    config-manager.py get KEY              Get config value
    config-manager.py validate             Validate config file
    config-manager.py reset                Reset to defaults
    config-manager.py adapters             List available agent adapters
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import adapter registry for agent validation
try:
    from adapters import list_adapters, adapter_info
    ADAPTERS_AVAILABLE = True
except ImportError:
    ADAPTERS_AVAILABLE = False
    def list_adapters() -> Dict[str, bool]:
        return {"copilot": True}  # Fallback
    def adapter_info(name: str) -> Optional[Dict]:
        return None

# Valid agent types (extensible via adapters)
VALID_AGENTS = ["copilot"]  # Will be extended by registered adapters

# Default configuration - base settings with agent-specific overrides
DEFAULT_CONFIG: Dict[str, Any] = {
    # Agent selection
    "agent": "copilot",
    
    # Base agent configuration (all adapters should handle these)
    "model": "claude-sonnet-4.5",
    "allow_tools": True,
    "excluded_tools": ["skill(speckit-vibe)"],
    
    # Agent-agnostic workflow settings
    "log_level": "INFO",
    "max_parallel": 3,
    "auto_learning": True,
    "agents_md_path": "AGENTS.md",
    "timeout_minutes": 30,
    "retry_count": 2,
    "session_isolation": True,
    "specs_dir": "specs",
    
    # Agent-specific configurations (for truly agent-specific settings)
    "agent_config": {
        "copilot": {
            "allow_paths": [],
            "allow_urls": []
        }
        # Future agents can add their specific configs here:
        # "claude-code": { "editor_integration": true, ... }
        # "aider": { "git_auto_commit": false, ... }
    }
}

# Config file path
CONFIG_FILE = ".speckit-vc.json"

# Valid log levels
VALID_LOG_LEVELS = ["DEBUG", "INFO", "WARN", "ERROR"]

# Config schema for validation - top-level keys
CONFIG_SCHEMA = {
    "agent": {"type": str, "values": VALID_AGENTS},
    "model": {"type": str},
    "allow_tools": {"type": bool},
    "excluded_tools": {"type": list},
    "log_level": {"type": str, "values": VALID_LOG_LEVELS},
    "max_parallel": {"type": int, "min": 1, "max": 10},
    "auto_learning": {"type": bool},
    "agents_md_path": {"type": str},
    "timeout_minutes": {"type": int, "min": 1, "max": 120},
    "retry_count": {"type": int, "min": 0, "max": 5},
    "session_isolation": {"type": bool},
    "specs_dir": {"type": str},
    "agent_config": {"type": dict}
}

# Copilot-specific config schema (for agent_config.copilot)
COPILOT_CONFIG_SCHEMA = {
    "allow_paths": {"type": list},
    "allow_urls": {"type": list}
}


def load_config() -> Dict[str, Any]:
    """Load configuration from file."""
    config_path = Path(CONFIG_FILE)
    
    if not config_path.exists():
        return DEFAULT_CONFIG.copy()
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Merge with defaults for any missing keys
        merged = DEFAULT_CONFIG.copy()
        merged.update(config)
        return merged
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {CONFIG_FILE}: {e}", file=sys.stderr)
        sys.exit(1)


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"Configuration saved to {CONFIG_FILE}")


def validate_value(key: str, value: Any) -> tuple[bool, str]:
    """Validate a configuration value against the schema."""
    if key not in CONFIG_SCHEMA:
        return False, f"Unknown configuration key: {key}"
    
    schema = CONFIG_SCHEMA[key]
    expected_type = schema["type"]
    
    # Type check
    if expected_type == bool:
        if isinstance(value, str):
            if value.lower() in ('true', '1', 'yes'):
                value = True
            elif value.lower() in ('false', '0', 'no'):
                value = False
            else:
                return False, f"{key} must be a boolean (true/false)"
        elif not isinstance(value, bool):
            return False, f"{key} must be a boolean"
    elif expected_type == int:
        try:
            value = int(value)
        except (ValueError, TypeError):
            return False, f"{key} must be an integer"
        
        if "min" in schema and value < schema["min"]:
            return False, f"{key} must be >= {schema['min']}"
        if "max" in schema and value > schema["max"]:
            return False, f"{key} must be <= {schema['max']}"
    elif expected_type == list:
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                # Treat as single item list
                value = [value]
        if not isinstance(value, list):
            return False, f"{key} must be a list"
    elif expected_type == str:
        if not isinstance(value, str):
            value = str(value)
        
        if "values" in schema and value not in schema["values"]:
            return False, f"{key} must be one of: {', '.join(schema['values'])}"
    
    return True, ""


def convert_value(key: str, value: str) -> Any:
    """Convert string value to appropriate type based on schema."""
    if key not in CONFIG_SCHEMA:
        return value
    
    schema = CONFIG_SCHEMA[key]
    expected_type = schema["type"]
    
    if expected_type == bool:
        return value.lower() in ('true', '1', 'yes')
    elif expected_type == int:
        return int(value)
    elif expected_type == list:
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return [value]
    else:
        return value


def cmd_init(args) -> None:
    """Initialize default configuration file."""
    config_path = Path(CONFIG_FILE)
    
    if config_path.exists() and not args.force:
        print(f"Configuration file already exists: {CONFIG_FILE}")
        print("Use --force to overwrite")
        sys.exit(1)
    
    save_config(DEFAULT_CONFIG)
    print("Default configuration initialized")


def cmd_show(args) -> None:
    """Display current configuration."""
    config = load_config()
    
    if args.json:
        print(json.dumps(config, indent=2))
    else:
        print("Current Configuration:")
        print("-" * 40)
        
        # Show agent-agnostic settings first
        for key, value in sorted(config.items()):
            if key == "agent_config":
                continue  # Show this last
            if isinstance(value, list):
                if value:
                    print(f"  {key}:")
                    for item in value:
                        print(f"    - {item}")
                else:
                    print(f"  {key}: []")
            elif isinstance(value, dict):
                print(f"  {key}: {{...}}")
            else:
                print(f"  {key}: {value}")
        
        # Show agent-specific configs
        if "agent_config" in config:
            print("\n  agent_config:")
            current_agent = config.get("agent", "copilot")
            for agent_name, agent_cfg in config["agent_config"].items():
                marker = " (active)" if agent_name == current_agent else ""
                print(f"    {agent_name}{marker}:")
                for k, v in agent_cfg.items():
                    if isinstance(v, list):
                        if v:
                            print(f"      {k}:")
                            for item in v:
                                print(f"        - {item}")
                        else:
                            print(f"      {k}: []")
                    else:
                        print(f"      {k}: {v}")


def cmd_set(args) -> None:
    """Set a configuration value."""
    config = load_config()
    
    key = args.key
    value = args.value
    
    # Handle special case for lists - append mode
    if args.append and key in CONFIG_SCHEMA and CONFIG_SCHEMA[key]["type"] == list:
        if key not in config:
            config[key] = []
        if value not in config[key]:
            config[key].append(value)
        save_config(config)
        print(f"Appended '{value}' to {key}")
        return
    
    # Validate
    is_valid, error = validate_value(key, value)
    if not is_valid:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
    
    # Convert and set
    config[key] = convert_value(key, value)
    save_config(config)
    print(f"Set {key} = {config[key]}")


def cmd_get(args) -> None:
    """Get a configuration value."""
    config = load_config()
    
    key = args.key
    
    if key not in config:
        print(f"Error: Unknown key: {key}", file=sys.stderr)
        sys.exit(1)
    
    value = config[key]
    if isinstance(value, (list, dict)):
        print(json.dumps(value))
    else:
        print(value)


def cmd_validate(args) -> None:
    """Validate configuration file."""
    config_path = Path(CONFIG_FILE)
    
    if not config_path.exists():
        print(f"Configuration file not found: {CONFIG_FILE}")
        print("Run 'config-manager.py init' to create it")
        sys.exit(1)
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        sys.exit(1)
    
    errors = []
    warnings = []
    
    # Check each top-level value
    for key, value in config.items():
        if key not in CONFIG_SCHEMA:
            warnings.append(f"Unknown key: {key}")
            continue
        
        is_valid, error = validate_value(key, value)
        if not is_valid:
            errors.append(error)
    
    # Check for missing required keys
    for key in CONFIG_SCHEMA:
        if key not in config:
            warnings.append(f"Missing key (using default): {key}")
    
    # Validate agent selection
    agent = config.get("agent", "copilot")
    if ADAPTERS_AVAILABLE:
        available = list_adapters()
        if agent not in available:
            errors.append(f"Unknown agent: {agent}. Available: {list(available.keys())}")
        elif not available.get(agent, False):
            warnings.append(f"Agent '{agent}' is configured but not available (CLI not installed)")
    
    # Validate agent_config structure
    if "agent_config" in config:
        agent_cfg = config["agent_config"]
        if not isinstance(agent_cfg, dict):
            errors.append("agent_config must be a dictionary")
        else:
            # Check that active agent has config
            if agent not in agent_cfg:
                warnings.append(f"No configuration found for active agent: {agent}")
            
            # Validate copilot-specific config if present
            if "copilot" in agent_cfg:
                copilot_cfg = agent_cfg["copilot"]
                for key in COPILOT_CONFIG_SCHEMA:
                    if key not in copilot_cfg:
                        warnings.append(f"Missing copilot config key: {key}")
    
    # Report results
    if errors:
        print("❌ Validation FAILED")
        print("\nErrors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ Configuration is valid")
    
    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"  - {warning}")
    
    if errors:
        sys.exit(1)


def cmd_adapters(args) -> None:
    """List available agent adapters."""
    if not ADAPTERS_AVAILABLE:
        print("Adapter registry not available.")
        print("Only 'copilot' adapter is supported.")
        return
    
    available = list_adapters()
    
    print("Available Agent Adapters:")
    print("-" * 50)
    
    for name, is_available in available.items():
        status = "✓ available" if is_available else "✗ not installed"
        print(f"  {name}: {status}")
        
        # Show details if requested
        if args.verbose:
            info = adapter_info(name)
            if info:
                print(f"    Executable: {info.get('executable', 'unknown')}")
                print(f"    Default model: {info.get('default_model', 'unknown')}")
                if not is_available:
                    print(f"    Install: {info.get('install_instructions', 'See documentation')[:60]}...")
                print()


def cmd_reset(args) -> None:
    """Reset configuration to defaults."""
    if not args.force:
        response = input("Reset configuration to defaults? [y/N] ")
        if response.lower() != 'y':
            print("Cancelled")
            return
    
    save_config(DEFAULT_CONFIG)
    print("Configuration reset to defaults")


def cmd_remove(args) -> None:
    """Remove an item from a list configuration."""
    config = load_config()
    
    key = args.key
    value = args.value
    
    if key not in config:
        print(f"Error: Key not found: {key}", file=sys.stderr)
        sys.exit(1)
    
    if not isinstance(config[key], list):
        print(f"Error: {key} is not a list", file=sys.stderr)
        sys.exit(1)
    
    if value in config[key]:
        config[key].remove(value)
        save_config(config)
        print(f"Removed '{value}' from {key}")
    else:
        print(f"'{value}' not found in {key}")


def main():
    parser = argparse.ArgumentParser(
        description="Manage speckit-vibe configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # init command
    init_parser = subparsers.add_parser('init', help='Create default config file')
    init_parser.add_argument('--force', '-f', action='store_true',
                            help='Overwrite existing config')
    
    # show command
    show_parser = subparsers.add_parser('show', help='Display current config')
    show_parser.add_argument('--json', action='store_true',
                            help='Output as JSON')
    
    # set command
    set_parser = subparsers.add_parser('set', help='Set config value')
    set_parser.add_argument('key', help='Configuration key')
    set_parser.add_argument('value', help='Value to set')
    set_parser.add_argument('--append', '-a', action='store_true',
                           help='Append to list instead of replacing')
    
    # get command
    get_parser = subparsers.add_parser('get', help='Get config value')
    get_parser.add_argument('key', help='Configuration key')
    
    # validate command
    subparsers.add_parser('validate', help='Validate config file')
    
    # reset command
    reset_parser = subparsers.add_parser('reset', help='Reset to defaults')
    reset_parser.add_argument('--force', '-f', action='store_true',
                             help='Skip confirmation')
    
    # remove command
    remove_parser = subparsers.add_parser('remove', help='Remove item from list')
    remove_parser.add_argument('key', help='Configuration key (must be a list)')
    remove_parser.add_argument('value', help='Value to remove')
    
    # adapters command
    adapters_parser = subparsers.add_parser('adapters', help='List available agent adapters')
    adapters_parser.add_argument('--verbose', '-v', action='store_true',
                                help='Show detailed adapter info')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Dispatch to command handler
    commands = {
        'init': cmd_init,
        'show': cmd_show,
        'set': cmd_set,
        'get': cmd_get,
        'validate': cmd_validate,
        'reset': cmd_reset,
        'remove': cmd_remove,
        'adapters': cmd_adapters
    }
    
    commands[args.command](args)


if __name__ == '__main__':
    main()
