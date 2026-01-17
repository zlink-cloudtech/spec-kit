---
name: spec-kit Development Guidelines
description: Protocol for discovering and using specialized skills.
applyTo: "**"
---

Auto-generated from all feature plans. Last updated: 2026-01-04

## Active Technologies
- Python 3.12+ + FastAPI, Uvicorn (server), Jinja2 (HTML templates), python-multipart (uploads). (003-release-server)
- Local Filesystem (`/data`) (003-release-server)
- Local filesystem (`/data` volume) (003-release-server)
- Python 3.11+, Bash 4+, PowerShell Core + `typer` (existing CLI) (007-refine-skills-integration)
- Python 3.11+ (Skill Scripts), Bash 4+ (Underlying Scripts) + `uv`, `pytest`, `uvicorn`, `act` (or `gh act`) (008-release-server-skill)
- Filesystem (`.github/skills/release-server-developer/`) (008-release-server-skill)
- Python 3.11 + `typer`, `rich`, `pathlib` (002-skills-integration)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.11: Follow standard conventions

## Recent Changes
- 012-add-sha256-checksum: Added Python 3.12+ + FastAPI, Uvicorn, python-multipart, aiofiles, hashlib (std lib)
- 012-add-sha256-checksum: Added [if applicable, e.g., PostgreSQL, CoreData, files or N/A]
- 011-add-sha256-checksum: Added Python 3.12+ (release-server) + FastAPI, Uvicorn, python-multipart, aiofiles.


<!-- MANUAL ADDITIONS START -->
## Feature: Release Server Development Guidelines

### 1. Init Development Environment

Only needed once or when dependencies change.

Initialize the development environment by running:

```bash
cd release-server && uv sync --all-extras
```

if uv is not installed:

```bash
pip install uv
```

### 2. Active Environment

Activate the development environment before starting work:

```bash
# workdir: release-server
source .venv/bin/activate
```

or execute directly with uv:

```bash
uv run <command>
uv pip install <package>
uv pytest
```

### 3. Testing After Development Changes

Run tests to ensure everything works as expected:

```bash
# workdir: release-server
pytest
```

<!-- MANUAL ADDITIONS END -->
