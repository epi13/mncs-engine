# Contributing to mncs-engine

`mncs-engine` is deliberately strict about where executable logic lives: project implementation, tests, benchmarks, examples and project-specific tools are written in MNCS Language.

Before changing implementation, read `AGENTS.md`, `docs/ARCHITECTURE.md`, and the RFCs relevant to the area.

## Development rules

1. Start from the semantic behavior the engine needs, not from a target API you want to wrap.
2. Keep reference behavior simple enough to inspect and compare.
3. When MNCS cannot express the desired implementation cleanly, reduce and document the language pressure instead of adding a foreign-language workaround.
4. Add the pressure item to `docs/PRESSURE.md` and identify the MNCS-family repository where the durable fix belongs.
5. Backend-specific optimization must preserve the declared semantic/numerical contract.
6. Conformance and performance claims require evidence from actual execution.
7. Avoid placeholder or decorative `.mncs` code. New modules should exist because an executable path needs them.

## RFC discipline

Large semantic changes should update an existing RFC or add a new one before the project accumulates incompatible implementation assumptions. Draft RFCs are expected to move under real engine pressure.

## Cross-backend changes

Where a change affects backend behavior, test the reference path and every currently available relevant backend. Distinguish unsupported capability, toolchain absence, compile failure, execution failure and semantic divergence rather than collapsing them into one result.

## Optimization changes

Optimize only after correctness is established. Record the workload, target capabilities, compiler/backend identity and measurements needed to reproduce the claim. Prefer corpus-wide improvements over a target-specific special case unless the capability model justifies the specialization.
