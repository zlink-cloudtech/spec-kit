# 5. Mermaid-Only Diagram Standard

**Date**: 2026-03-07  
**Status**: Accepted

## Context

The `speckit-architect` skill previously stated a vague preference: "Prefer Mermaid.js for architecture diagrams." This left PlantUML as an implicit fallback. In practice, mixing two diagram tools within the same plan phase produces inconsistent artifacts — different syntax, different rendering requirements, and increased agent token cost from multi-format instructions.

Five diagram types are relevant to the plan phase: sequence diagrams (cross-component call flows), ER diagrams (persistent entity relationships), state machine diagrams (entity lifecycle transitions), flowcharts (complex business logic branching), and class diagrams (OO domain models). Each has a clear trigger condition and obligation level.

A single mandatory standard eliminates ambiguity for agents generating diagrams and for engineers reviewing them. Mermaid.js is natively supported by GitHub, GitLab, and most AI coding assistants; PlantUML requires a separate renderer and server.

Additionally, each diagram type now has a precise trigger rule and output target, making diagram generation deterministic and automatically verifiable via `uv run pytest`. A dedicated script — `scripts/bash/setup-uml-dir.sh` (and its PowerShell equivalent `scripts/powershell/setup-uml-dir.ps1`) — initialises the `specs/###/uml/` directory idempotently and returns its absolute path, enabling adapter rules to reference a stable output directory.

## Decision

**Mermaid.js is the sole permitted diagram tool for all SpecKit-generated plan artifacts. PlantUML is PROHIBITED.**

The `speckit-architect` skill's `Tools & Standards` section has been updated accordingly, and a new `## Diagram Strategy` section has been added listing five diagram types with trigger conditions and obligation levels (MUST / SHOULD):

| Diagram Type | Trigger Condition | Obligation | Output Target |
|---|---|---|---|
| `sequenceDiagram` | Two or more named components exchange calls | MUST | `uml/sequence.md` |
| `erDiagram` | `data-model.md` defines persistent entities with relationships | MUST | embedded in `data-model.md` |
| `stateDiagram-v2` | `data-model.md` has entity with enumerated state field and transitions | MUST | embedded in `data-model.md` (after `erDiagram`) |
| `flowchart` | 3 or more conditional decision paths in user flows | SHOULD | `uml/flow.md` |
| `classDiagram` | OO inheritance or composition relationships between domain classes | SHOULD | `uml/class-diagram.md` |

The `skills/speckit-architect/speckit-adapter.yaml` plan hook encodes one rule per diagram type. Rules reference `scripts/bash/setup-uml-dir.sh` (bash) or `scripts/powershell/setup-uml-dir.ps1` (PowerShell) — agent selects based on execution environment — to initialise the `uml/` directory before writing any `uml/*.md` file.

## Consequences

**Positive**:
- Diagram generation is deterministic and machine-verifiable: presence of `uml/sequence.md`, `uml/flow.md`, `uml/class-diagram.md`, and inline blocks in `data-model.md` can be asserted in pytest.
- Eliminates rendering environment dependency on PlantUML servers.
- Reduces agent instruction ambiguity: one tool, five explicit trigger rules.
- `setup-uml-dir.sh` / `setup-uml-dir.ps1` are idempotent, enabling safe re-runs.

**Negative / Trade-offs**:
- Existing plan artifacts containing PlantUML syntax must be manually migrated if they are to be used as reference material.
- Mermaid has limited layout control compared to PlantUML for very large diagrams; this is acceptable for plan-phase artifacts which should remain concise.
- Engineers who prefer PlantUML cannot use it in SpecKit-managed plan outputs.
