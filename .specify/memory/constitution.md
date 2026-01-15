<!--
Sync Impact Report: Constitution Update (v1.0.0)

Version Change: N/A -> v1.0.0 (Initial Ratification)

Modified Principles:
- N/A -> I. Specification-First (Defined)
- N/A -> II. Executable Specifications (Defined)
- N/A -> III. Continuous Refinement (Defined)
- N/A -> IV. Research-Driven Context (Defined)
- N/A -> V. Bidirectional Feedback (Defined)

Added Sections:
- Core Principles (Defined 5 principles based on spec-driven.md)
- Development Workflow (Defined SDD lifecycle)

Templates Requiring Updates:
- .specify/templates/plan-template.md ⚠ (Path check needed, file might identify as templates/plan-template.md)
- .specify/templates/spec-template.md ⚠ (Path check needed)
- .specify/templates/tasks-template.md ⚠ (Path check needed)
- .specify/templates/commands/*.md ⚠ (Path check needed)

Follow-up TODOs:
- Verify template locations and update references if necessary.
-->
# Spec Kit Constitution

## Core Principles

### I. Specification-First
The specification is the primary artifact and source of truth. Code is a derived expression of the specification. All development begins with defining intent in a comprehensive Project Requirements Document (PRD). Implementation details flow downstream from the specification. Maintaining software means evolving specifications, not just patching code.

### II. Executable Specifications
Specifications must be precise, complete, and unambiguous enough to generate working systems. They serve as the input for implementation planning and code generation. The gap between intent and implementation is minimized by treating specifications as executable directives rather than passive documentation.

### III. Continuous Refinement
Consistency and quality are validated continuously, not at a single gate. Automated analysis checks specifications for ambiguity, contradictions, and gaps throughout the lifecycle. Refinement is an ongoing process of aligning the specification with evolving requirements and insights.

### IV. Research-Driven Context
Technical decisions are informed by active research. Before implementation planning, critical context—library compatibility, organizational constraints, performance benchmarks—is gathered and applied. This ensures specifications are grounded in technical reality.

### V. Bidirectional Feedback
Production reality informs specification evolution. Metrics, incidents, and operational learnings are not just fixes but inputs for refining the foundational specifications. The development loop is circular: Specification → Implementation → Operation → Specification.

## Development Workflow

### SDD Lifecycle

1.  **Specify**: Transform vague ideas into structured Feature Specifications (`spec.md`) with user stories and acceptance criteria.
2.  **Plan**: Generate comprehensive Implementation Plans (`plan.md`) that map requirements to technical architecture and decisions.
3.  **Task**: Derive executable Task Lists (`tasks.md`) from the implementation plan and design documents.
4.  **Implement**: Generate code and tests based on the precise instructions in the spec, plan, and tasks.
5.  **Refine**: Continuously update the specification based on implementation discoveries and operational feedback.

## Governance

This Constitution serves as the supreme law for the project. All architectural decisions, development practices, and code changes must align with these principles.

*   **Primacy**: In case of conflict between code and specification, the specification rules. The remediation is to update the specification, then regenerate the code.
*   **Amendments**: Changes to this Constitution require a formal proposal and ratification process. Breaking changes to principles trigger a MAJOR version bump.
*   **Compliance**: Automated tools and human review must verify that all artifacts (specs, plans, code) adhere to these principles.

**Version**: 1.0.0 | **Ratified**: 2026-01-05 | **Last Amended**: 2026-01-09
