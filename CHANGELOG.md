# Changelog

All notable changes to this project from commit 9111699cd27879e3e6301651a03e502ecb6dd65d to the current version are documented here.

> [!NOTE]
> The original `CHANGELOG.md` has been renamed to `CHANGELOG.md.origin`.
> The original `README.md` has been renamed to `README.md.origin`.

## Changes since 9111699cd27879e3e6301651a03e502ecb6dd65d

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
