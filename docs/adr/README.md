# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for the Spec Kit project.

## What is an ADR?

An ADR is a document that captures an important architectural decision made along with its context and consequences. We follow the [Michael Nygard format](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions).

## Numbering Convention

ADRs are numbered sequentially: `0001`, `0002`, `0003`, etc. The number is never reused even if an ADR is superseded or deprecated.

## ADR Index

| Number | Title | Status | Date |
|--------|-------|--------|------|
| [0001](0001-dual-mode-deployment-pattern.md) | Dual-Mode Deployment Pattern (Image vs NPM) | Accepted | 2026-02-26 |
| [0002](0002-oci-chart-publishing-ghcr.md) | OCI Chart Publishing to GHCR | Accepted | 2026-02-26 |
| [0003](0003-gateway-api-httproute-support.md) | Gateway API HTTPRoute Support with Mutual Exclusivity | Accepted | 2026-02-26 |
| [0004](0004-version-synchronization-strategy.md) | Single-Version Synchronization Strategy | Accepted | 2026-02-26 |

## Template

```markdown
# [NUMBER]. [TITLE]

**Date**: YYYY-MM-DD
**Status**: Proposed | Accepted | Deprecated | Superseded by [XXXX]

## Context

[Describe the forces at play, including technical, political, social, and project local.]

## Decision

[Describe the decision and its rationale.]

## Consequences

[Describe the resulting context, both positive and negative.]
```
