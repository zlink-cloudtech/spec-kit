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
- 003-release-server: Added Python 3.12+ + FastAPI, Uvicorn (server), Jinja2 (HTML templates), python-multipart (uploads).


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
