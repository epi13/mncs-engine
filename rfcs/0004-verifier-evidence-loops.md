# RFC 0004 — Verifier Evidence and Micro-Model Feedback Loops

Status: Draft

## Summary

Engine pressure runs should emit compact, structured evidence that deterministic micro-verifiers can inspect and that specialized micro-models may later use for diagnosis and optimization advice. Learned output is advisory unless independently verified.

## Motivation

The engine will generate a large stream of repeated, narrowly structured observations: compile outcomes, numerical comparisons, image differences, runtime failures, backend diagnostics and performance/resource measurements across machines. These are well suited to small specialized verifiers and learned components rather than requiring a single general model to reason over every run from scratch.

## Evidence unit

A useful evidence record should identify:

- workload/source identity;
- semantic contract/version;
- compiler and backend identity;
- target/worker capability facts;
- input identity;
- output/artifact identity;
- comparison policy and result;
- diagnostics;
- timing/resource observations where relevant;
- provenance linking the record to the run that produced it.

The exact schema should evolve with MNCS evidence/provenance facilities rather than inventing an incompatible private format.

## Micro-verifiers

Good early deterministic verifier candidates include:

- artifact/digest integrity;
- reference versus candidate dimension/layout checks;
- exact integer/buffer comparison;
- bounded floating-point comparison under declared tolerance;
- visual mismatch localization;
- regression against a previous accepted evidence baseline;
- static/runtime bounds evidence where exposed;
- race/synchronization checks when the backend can supply trustworthy evidence.

A verifier must have a narrow question and an explainable pass/fail/unknown result.

## Micro-debuggers

Specialized debuggers may classify recurring failure shapes and propose reduced reproductions: numerical drift, layout disagreement, unsupported capability, launch failure, synchronization/race suspicion, compiler regression, or target-specific codegen failure.

Their output should link back to raw evidence and be independently reproducible.

## Advisory micro-models

Potential learned components may predict or rank:

- memory coalescing/layout opportunities;
- likely occupancy/register pressure problems;
- shared/local memory candidates;
- profitable work-group/block shapes;
- SIMD/SIMT-friendly transformations;
- compiler lowering choices that historically perform well on a capability class;
- suspicious performance regressions requiring deterministic confirmation.

These components suggest hypotheses. They do not redefine program semantics.

## Trust boundary

Correctness cannot depend solely on an opaque model prediction. A learned component may trigger a candidate optimization, but acceptance requires deterministic compilation/execution/conformance evidence.

## Feedback loop

The intended loop is:

1. run a stable MNCS workload;
2. collect structured evidence;
3. verify correctness;
4. classify anomalies or optimization opportunities;
5. generate a candidate compiler/engine change or recommendation;
6. rerun the same corpus across relevant targets;
7. accept only when evidence improves without violating semantics.

## Long-term direction

As `mncs-memory`, `mncs-ingest`, `mncs-learn`, MNEL and related systems mature, engine evidence may become one domain feeding a broader machine-native learning loop. The engine should remain usable without those learned components and should preserve raw deterministic evidence for audit and replay.
