# System Map

**Purpose**: Centralized index of all authoritative documentation for the project. Enables AI agents to quickly locate relevant context without scanning the entire codebase.

**Template Version**: 2.0.0
**Version**: 1.0.0 | **Created**: 2026-03-03 | **Last Updated**: 2026-03-13
**Maintained By**: Spec Kit Maintainers
**Review Frequency**: After each major feature completion

---

## Project Identity

**Project**: Spec Kit
**Description**: An open source toolkit for Spec-Driven Development (SDD). Provides
templates, scripts, AI agent integrations, and a CLI tool (Specify) that guide development
teams through a structured, specification-first approach to building software.

### Core Principles

1. **Specification First** — Every feature begins with a written spec before any implementation.
2. **Executable Specifications** — Specs must be precise and unambiguous enough to drive code generation.
3. **Lifecycle Integrity** — The 6-phase SDD lifecycle must be followed; CONVERGENCE_BOUNDARY required in all tasks.
4. **Test-First Imperative** — TDD mandatory; Red-Green-Refactor cycle strictly enforced.
5. **Multi-Agent Portability** — Toolkit works across all supported AI agents; agent-specific code isolated.

### Technology Stack

<!-- List the primary languages, frameworks, and tools used in this project. -->

| Category | Technology | Purpose |
|----------|-----------|------|
| Language | Python 3.11+ | Specify CLI source code |
| CLI Framework | Typer + Rich | CLI interface and formatting |
| Language | TypeScript / Node.js | MCP server |
| Scripts | Bash / PowerShell | Feature creation and context update scripts |
| Packaging | Hatchling + uv | Python package build and distribution |
| Container | Docker / Helm | Release server and MCP deployment |
| Testing | pytest + unittest.mock | Python unit and integration tests |
| Linting | ruff | Python code quality |

### Project Components

<!-- List the major components/modules of this project. -->

| Component | Location | Technology | Purpose |
|-----------|----------|------------|---------|
| Specify CLI | `src/specify_cli/` | Python / Typer | Bootstrap projects for SDD; `init`, `check`, `version` commands |
| Bash Scripts | `scripts/bash/` | Bash | Feature creation, context update, skill generation |
| PowerShell Scripts | `scripts/powershell/` | PowerShell | Cross-platform equivalents of all bash scripts |
| Templates | `templates/` | Markdown / YAML | Command, instruction, and document templates |
| Skills | `skills/` | Markdown | AI agent skill personas (architect, developer, tech-lead, etc.) |
| Release Server | `release-server/` | Python / FastAPI / Docker | Package hosting and release management |
| MCP Server | `mcp/` | TypeScript / Helm | Model Context Protocol server deployment |
| Documentation | `docs/` | Markdown / DocFX | User-facing docs, quickstart, ADRs, upgrade guide |
| Specifications | `specs/` | Markdown | Feature specification directories (`###-name/`) |

---

## Essential Artifacts

<!--
Status values: ✅ Active | ⚠️ Missing | 🗑️ Deprecated
Fill tables based on your project type. Not all categories apply to every project.

Common artifacts by project type:
- Web Backend: System Architecture, Database Schema, API Design, Deployment Config
- CLI Tool: Command Structure, Plugin Architecture, Distribution Config
- Frontend App: Component Hierarchy, State Management, Routing Map
- Library/SDK: Public API Reference, Compatibility Matrix, Usage Examples
- Microservices: Service Topology, Contract Catalog, Inter-service Auth
- Data Pipeline: Data Flow Diagram, Schema Registry, Processing SLAs

Add rows that are relevant; remove or leave empty categories that don't apply.
-->

### 🏛️ Architecture & Design

| Artifact | Location | Status | Last Updated | Description |
|----------|----------|--------|--------------|-------------|
| Agent Integration Guide | `AGENTS.md` | ✅ Active | 2026-03-28 | Full project architecture, agent onboarding, and skill creation guide |
| SDD Methodology | `spec-driven.md` | ✅ Active | 2026-03-13 | Comprehensive Spec-Driven Development philosophy and workflow |
| MCP Helm Chart | `mcp/chart/` | ✅ Active | 2026-03-03 | Helm chart for MCP server deployment |
| Release Server Chart | `release-server/chart/` | ✅ Active | 2026-03-03 | Helm chart for release server deployment |
| Doc-Update Command Template | `templates/commands/doc-update.md` | ✅ Active | 2026-03-13 | Standalone `/speckit.doc-update` command template; auto-distributed to all agents via `generate_commands()` in release script |
| speckit-doc-updater Skill | `skills/speckit-doc-updater/SKILL.md` | ✅ Active | 2026-03-13 | Agent persona for lifecycle-independent documentation management; supports 6 operations (update, add, delete, deprecate, rename/move, merge, reposition) with hard-stop rule on missing system-map |
| speckit-doc-updater Adapter | `skills/speckit-doc-updater/speckit-adapter.yaml` | ✅ Active | 2026-03-13 | Phase hook registration for `doc-update` phase at priority 100; invocable via `bash scripts/bash/resolve-skills.sh doc-update .` |

### 📐 Configuration & Infrastructure

| Artifact | Location | Status | Last Updated | Description |
|----------|----------|--------|--------------|-------------|
| Python Package Config | `pyproject.toml` | ✅ Active | 2026-03-03 | Package metadata, dependencies, and build config for Specify CLI |
| SpecKit Config Template | `templates/speckit-config-template.yaml` | ✅ Active | 2026-03-03 | Project-level `.speckit.yaml` configuration template |
| Devcontainer Config | `.devcontainer/` | ✅ Active | 2026-03-03 | Development container setup with AI agent extensions |
| Release Packages Script | `.github/workflows/scripts/create-release-packages.sh` | ✅ Active | 2026-03-03 | Generates per-agent ZIP release packages |

### 🧪 Quality & Testing

| Artifact | Location | Status | Last Updated | Description |
|----------|----------|--------|--------------|-------------|
| CLI Tests | `tests/` | ✅ Active | 2026-03-13 | pytest suite for Specify CLI and skill resolver; includes `tests/test_init.py`, `tests/test_resolve_skills.py`, `tests/test_setup_uml_dir.py` (UML directory script tests), `tests/test_skill_diagram_strategy.py` (speckit-architect SKILL.md and adapter diagram rule tests), and `tests/test_doc_update_command.py` (doc-update command template, skill adapter, and CLI banner tests) |
| Release Server Tests | `release-server/tests/` | ✅ Active | 2026-03-03 | API, auth, contract, and storage tests for release server |
| MCP Server Tests | `mcp/tests/` | ✅ Active | 2026-03-03 | Prompt and integration tests for MCP server |

### 🧭 Project Memory

<!--
  These entries anchor the Gap Analysis in /speckit.plan.
  Always keep status up to date so agents do not incorrectly create bootstrap tasks
  for files that already exist on disk.
-->

| Artifact | Location | Status | Last Updated | Description |
|----------|----------|--------|--------------|-------------|
| System Map | `.specify/memory/system-map.md` | ✅ Active | 2026-03-03 | Living index of all project components and documentation |
| Project Constitution | `.specify/memory/constitution.md` | ✅ Active | 2026-03-03 | Governing principles and architectural constraints |

### 📚 Decisions & Standards

| Artifact | Location | Status | Last Updated | Description |
|----------|----------|--------|--------------|-------------|
| ADR Index | `docs/adr/README.md` | ✅ Active | 2026-03-03 | Index of all architectural decision records |
| ADR-0001 | `docs/adr/0001-dual-mode-deployment-pattern.md` | ✅ Active | 2026-03-03 | Dual-mode deployment pattern |
| ADR-0002 | `docs/adr/0002-oci-chart-publishing-ghcr.md` | ✅ Active | 2026-03-03 | OCI chart publishing to GHCR |
| ADR-0003 | `docs/adr/0003-gateway-api-httproute-support.md` | ✅ Active | 2026-03-03 | Gateway API HTTPRoute support |
| ADR-0004 | `docs/adr/0004-version-synchronization-strategy.md` | ✅ Active | 2026-03-03 | Version synchronization strategy |
| ADR-0005 | `docs/adr/0005-mermaid-only-diagram-standard.md` | ✅ Active | 2026-03-07 | Mermaid-only diagram standard (PlantUML PROHIBITED); five UML trigger rules for plan phase |
| ADR-0006 | `docs/adr/0006-standalone-doc-management-agent.md` | ✅ Active | 2026-03-13 | Decision to create a lifecycle-independent `/speckit.doc-update` command and `speckit-doc-updater` skill rather than extending `speckit-librarian` |

---

## Integration Points

### External Services

<!-- List third-party services, APIs, or platforms the project depends on. Leave empty if none. -->

| Service | Type | Documentation | Purpose |
|---------|------|---------------|---------|

### Internal Dependencies

<!-- List internal modules or services that this project depends on or exposes. Leave empty if not applicable. -->

| Module | Location | Interface | Description |
|--------|----------|-----------|-------------|

---

## Knowledge Sources

### Documentation

<!-- List user-facing and developer-facing documentation. -->

| Topic | Location | Type | Description |
|-------|----------|------|-------------|
| Quickstart Guide | `docs/quickstart.md` | User-facing | Step-by-step guide for using Spec Kit |
| Installation Guide | `docs/installation.md` | User-facing | Installation instructions for all platforms |
| Skills Integration | `docs/skills-integration.md` | Developer-facing | How to create and integrate agent skills |
| Local Development | `docs/local-development.md` | Developer-facing | Development environment setup |
| Upgrade Guide | `docs/upgrade.md` | User-facing | Instructions for upgrading Specify CLI |
| Helm Deployment | `docs/helm-deployment.md` | Ops-facing | MCP and release server Helm deployment guide |
| README | `README.md` | User-facing | Project overview, quick start, and supported agents |
| Chinese README | `README-CN.md` | User-facing | Chinese language project overview |

### Technical Context

<!-- List domain-specific resources, guides, or references relevant to this project. -->

| Domain | Resource | Description |
|--------|----------|-------------|

---

## Using the System Map

### For Planning (`/speckit.plan`)

1. **Identify Touched Components**: Cross-reference feature requirements with the Architecture & Design section.
2. **Flag Gaps**: If a touched component has status "⚠️ Missing", add a Bootstrapping Task to Phase N.
3. **Extract Context**: Include relevant artifacts in the "Relevant System Context" section of `plan.md`.

### For Task Generation (`/speckit.tasks`)

1. **Bind Context to Tasks**: For tasks touching specific modules, append `(Ref: <location>)` to task descriptions.
2. **Verify Prerequisites**: Check the Configuration & Infrastructure section for setup requirements.

### For Implementation (`/speckit.implement`)

1. **Follow Standards**: Reference the Code Style Guide and Development Guidelines.
2. **Check Decisions**: Review related ADRs before making architectural changes.

---

## Maintenance Protocol

### When a Feature is Completed

1. **Update Status**: Change artifact status from "⚠️ Missing" to "✅ Active".
2. **Record Location**: Fill in the actual file path or URL.
3. **Update Timestamp**: Set "Last Updated" to the current date.
4. **Add Description**: Briefly describe what the artifact contains.

### When an Artifact is Deprecated

1. **Change Status**: Mark as "🗑️ Deprecated".
2. **Add Reason**: Note why it was deprecated and what replaced it.
3. **Archive**: Move to an `archive/` directory if still needed for reference.

---

## Bootstrap Checklist

Review the Essential Artifacts tables above. Any artifact with status "⚠️ Missing" that is critical to your project should be prioritized for creation. The `/speckit.converge` phase will use this map to identify and close documentation gaps.

---

**Instructions for Agents**:

- **DO** treat this map as the authoritative index of documentation.
- **DO** propose updates to this map when creating or discovering new artifacts.
- **DO** flag missing artifacts during planning phases.
- **DO NOT** assume artifacts exist if not listed here or marked as "⚠️ Missing".
- **DO NOT** create duplicate documentation without updating this index.
- **DO NOT** add new sections or restructure this document. Only fill tables and update status fields.
