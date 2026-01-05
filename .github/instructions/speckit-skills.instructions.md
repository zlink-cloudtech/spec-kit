---
name: Spec Kit Skills Protocol
description: Protocol for discovering and using specialized skills.
applyTo: "**"
---
# Agent Skills Configuration

You have access to a library of specialized skills defined in this workspace. These skills provide specific workflows, instructions, and strategies for complex tasks.

## Core Directive

**You MUST prioritize using these skills over your general knowledge whenever they are relevant to the user's request.** Skills represent the "gold standard" for how tasks should be performed in this project.

## Skill Usage Protocol

1.  **Discovery**: When you receive a task, first check the `<available_skills>` list below.
2.  **Activation**: If a skill's `<description>` matches the task or seems relevant, you **MUST** read the skill definition file at the provided `<location>`.
3.  **Execution**: Follow the instructions in the skill file. Prioritize the skill's specific strategies over your general knowledge.

## Available Skills

<available_skills>
  <skill>
    <name>mcp-builder</name>
    <description>Guide for creating high-quality MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools. Use when building MCP servers to integrate external APIs or services, whether in Python (FastMCP) or Node/TypeScript (MCP SDK).</description>
    <location>${workspaceFolder}/skills/mcp-builder/SKILL.md</location>
  </skill>
  <skill>
    <name>skill-creator</name>
    <description>Guide for creating effective skills. This skill should be used when users want to create a new skill (or update an existing skill) that extends Claude's capabilities with specialized knowledge, workflows, or tool integrations.</description>
    <location>${workspaceFolder}/skills/skill-creator/SKILL.md</location>
  </skill>
</available_skills>
