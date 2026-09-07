# RFC 0001 — Execution, Capability and Memory-Space Abstraction

Status: Draft

## Summary

Engine source should express what a workload requires and what semantic parallel work it performs without hard-coding a particular GPU generation, CUDA launch shape, or host/device API into ordinary engine logic.

## Motivation

Graphics and simulation pressure heterogeneous execution immediately. A naive design would reproduce CUDA concepts directly in engine source and later add separate CPU/WASM implementations. That would make the engine a collection of target-specific ports rather than a test of MNCS portability.

## Proposed model

MNCS engine workloads should be able to declare:

- required capabilities;
- preferred capabilities;
- semantic parallel work shape;
- data access and synchronization requirements;
- numeric guarantees/tolerances;
- memory lifetime and visibility requirements.

The compiler/runtime/backend then maps those semantics onto CPU threads/SIMD, WASM, CUDA/PTX, or future execution systems.

## Capability orientation

Prefer concepts such as:

- parallel compute available;
- required scalar/vector numeric types;
- atomic/synchronization capability;
- local/shared fast memory where semantics require it;
- image/surface presentation capability;

rather than ordinary source checking device model names.

Target identity still belongs in evidence and backend selection because it matters for reproducibility and optimization, but it should not define the meaning of the workload.

## Memory spaces

The engine will pressure MNCS to distinguish memory semantics where hardware makes the distinction real. The durable language abstraction may or may not use CUDA vocabulary (`host`, `device`, `shared`, `local`). The requirement is that source can express ownership, accessibility, sharing, synchronization and lifetime without unsafe implicit assumptions.

## Parallel execution

The preferred source model describes semantic iteration or work rather than CUDA thread/block indices. Backend-specific launch configuration is an optimization/lowering concern unless the program explicitly requires a machine topology property.

## Fallbacks

Capability fallback must preserve meaning. A slower reference path is acceptable; silently changing algorithms or numerical contracts because a capability is unavailable is not.

## Language pressure

If current MNCS cannot express one of these contracts, the engine should keep the desired model documented and upstream a minimal reproducer rather than freezing CUDA-specific syntax into the engine as a workaround.

## Open questions

- Which memory properties must be language-level versus stdlib/runtime-level?
- How should asynchronous execution and transfer dependencies be represented?
- Which numeric modes are semantic promises versus optimization permissions?
- How should capability negotiation compose with Fabric worker selection?
