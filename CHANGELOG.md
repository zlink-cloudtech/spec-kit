# Changelog

All notable changes to this project from commit 9111699cd27879e3e6301651a03e502ecb6dd65d to the current version are documented here.

> [!NOTE]
> The original `CHANGELOG.md` has been renamed to `CHANGELOG.md.origin`.
> The original `README.md` has been renamed to `README.md.origin`.

## [2.2.0] - 2026-02-28

### MCP

- **Helm chart for Kubernetes deployment**: Added full Helm chart (`mcp/chart/`) for deploying the MCP server to Kubernetes with dual-mode support
  - **Image mode** (default): Deploy from a pre-built container image
  - **NPM mode**: Install the NPM package at runtime via an init container
  - Flexible networking with Kubernetes Ingress and Gateway API HTTPRoute (mutually exclusive)
  - JSON schema validation (`values.schema.json`) for Helm values
  - Standard Kubernetes best practices: `app.kubernetes.io/*` labels, liveness/readiness probes, configurable resources
  - CI test values for multiple configurations (ingress, httproute, npm, npm-auth, image, conflict)
- **`publish-chart.sh` script**: New script (`mcp/scripts/publish-chart.sh`) to package and publish the Helm chart to GHCR as an OCI artifact
  - Supports `GITHUB_TOKEN`, `GITHUB_ACTOR` environment variables for GHCR authentication
  - Includes lint, package, and push steps with `DRY_RUN` support

### Documentation

- Updated MCP README (`mcp/README.md`) with Helm chart deployment section (quick install, NPM mode, verify deployment)
- Updated MCP 中文文档 (`mcp/README-CN.md`) with corresponding Helm chart 部署说明
- Added comprehensive chart documentation (`mcp/chart/README.md`) covering installation, configuration, networking, and troubleshooting

## [2.1.0] - 2026-02-26

### CLI

- **Post-install instructions updated for v2.0.0 lifecycle**: "Next Steps" panel now shows the complete 6-phase lifecycle including `/speckit.converge` (Phase N documentation convergence)
- **Enhancement commands panel updated**: Added `/speckit.taskstoissues` for GitHub issues integration; improved descriptions with lifecycle phase hints
- **Sub-step numbering fix**: Step numbers now dynamically follow the parent step number instead of being hardcoded as `2.x`

### Scripts

- **Branch naming convention**: New `type/###-name` format (e.g., `feat/001-user-auth`, `bug/002-login-crash`) replacing flat `###-name` format
  - 6 branch types: `feat`, `bug`, `hotfix`, `refactor`, `docs`, `chore` (default: `feat`)
  - Added `--type` parameter to `create-new-feature.sh` and `-Type` parameter to `create-new-feature.ps1`
  - Global sequential numbering across all types; specs directory stays flat (`specs/001-name/`)
  - Updated validation regex in `common.sh` / `common.ps1` to enforce new format
  - JSON output includes new `BRANCH_TYPE` field
- **`strip_branch_type()` / `Get-BranchWithoutType`**: New helper functions to strip type prefix for specs directory mapping

### Documentation

- Updated `SPECIFY_FEATURE` examples in README.md, README-CN.md, docs/upgrade.md, docs/skills-integration.md
- Updated `specify.md` template with `--type` parameter documentation and branch type auto-detection guidance

## [2.0.0] - 2026-02-13

### Architecture

- **Constitution v2.0.0**: 9 principles (added Skills-First, Test-First Imperative, Documentation Continuity, Context Awareness) and 6-phase lifecycle (Specify → Clarify → Plan → Task → Implement → Converge)
- **Adapter Pattern**: Skills use `speckit-adapter.yaml` sidecar for SpecKit-specific orchestration while keeping `SKILL.md` portable
- **Context Funnel**: Progressive context narrowing across lifecycle phases (System Map → Plan → Task → Implement)
- **Documentation State Matrix**: Tracks document update actions during plan phase

### Added

- **`/speckit.converge` command**: New lifecycle phase for documentation convergence — updates ADRs, System Map, and closes documentation gaps
- **`.speckit.yaml` configuration**: Optional project config file for customizing skill scan directories, memory paths, and version compatibility checks
- **System Map template** (`templates/system-map-template.md`): Documentation index for tracking all project artifacts
- **4 core skills**: `speckit-architect` (plan), `speckit-developer` (implement/tasks), `speckit-librarian` (converge), `speckit-tech-lead` (tasks)
- **`resolve-skills.py`**: Phase-based skill resolver with multi-directory scanning, `.speckit.yaml` support, and `instructions` field injection
- **`speckit-config-template.yaml`**: Configuration template for `.speckit.yaml`
- **`tests/test_resolve_skills.py`**: 15 test cases covering parser, config loading, skill resolution, and multi-dir scanning
- **Phase N Coverage Check**: `analyze` command Section G validates Documentation State Matrix and Gap Analysis task coverage

### Changed

- **TDD enforcement**: Tasks template and command changed from `OPTIONAL` to `REQUIRED` (per Constitution Article IV)
- **Phase separation**: Phase N-1 (Polish) separated from Phase N (Convergence) with `<!-- CONVERGENCE_BOUNDARY -->` marker
- **Implement command**: Hard stop at CONVERGENCE_BOUNDARY with Phase N-1 completion check and handoff to `/speckit.converge`
- **Plan command**: Added System Map integration, Documentation State Matrix, and Gap Analysis instructions
- **Tasks command**: Added Phase N-1/N generation rules, CONVERGENCE_BOUNDARY requirement, updated phase structure
- **Phase naming**: Unified `close` → `converge` across all files (adapter, docs, templates)
- **Skills integration docs**: Updated with `instructions` field, `.speckit.yaml` reference, converge phase

### Fixed

- Constitution header HTML comment updated from stale v1.0.0 to v2.0.0
- SKILL.md files purified — removed all SpecKit-specific path references (now in adapter `instructions`)
- Dependencies section in tasks template properly reflects Phase N-1/N separation

## Changes since 9111699cd27879e3e6301651a03e502ecb6dd65d

- feat: add --spec-dir parameter to speckit.specify for directory isolation and workflow orchestration
- 7257b6c fix: update release workflow to include version bump in pyproject.toml and handle git push conditionally
- b29322d chore(release-server): bump version to 0.0.6 [skip ci]
- 13ba0f7 fix: update method for retrieving latest release-server tag to ensure correct versioning
- f4fdc51 fix: update git push command to use HEAD reference for better compatibility
- 1227aa0 fixbug: blocking in commit version bump on local act env
- 184436a fixbug: Do not mark as repo-wide "latest" (avoids timeout errors with non-standard prefixes) for release-server publish
- 0a1d201 fix: checking path is a file in delete_package
- 6244778 feat: split publish workflow
- 02755f9 fix: workflow helm error
- fd876e3 fix: add response format enum and update package listing logic
- f17148e improve: fix problems for lint and other improved
- 4ef52f8 feat: add release-server
- 8434872 docs: amend constitution to v1.0.0 (ratify core principles + governance)
- bfde6b4 chore: update changelog for version 0.0.90
- 9de3a70 feat: add ESLint and Prettier ignore files
- 3d7b374 docs: add CN documents
- 2ac3cb2 feat: enhance translation prompt with Markdown anchor handling and output file naming
- 723eb9c env: speckit init
- 689f584 feat: add support for integrating skills
- 3e067a2 feat(mcp): initialize MCP server with Docker support and translation prompt
- daa7b89 feat: Add --template-url option for custom template repositories in specify command (update README.md)
- c109790 initialize spec for copilot and init constitution
- 878b35b feat: Add support for local or special remote template sources in download functions
