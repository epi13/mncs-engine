# Language and backend pressure ledger

This file records engine requirements that cannot yet be expressed cleanly, correctly, portably, or efficiently in MNCS.

Pressure entries should be reduced and actionable rather than vague wishes.

## Entry format

Each pressure item should record:

- **Area** — parser, type system, stdlib, runtime, optimizer, backend, Fabric, Actions, etc.
- **Workload** — the engine program that exposed the limitation.
- **Desired MNCS expression** — what the machine-native source should look like conceptually.
- **Observed limitation** — what currently prevents or degrades it.
- **Minimal reproducer** — smallest useful `.mncs` case.
- **Targets affected** — CPU/WASM/CUDA/PTX/etc.
- **Correctness impact** — none, ambiguity, divergence, crash, unsupported.
- **Cost impact** — compile time, runtime, memory, code size, transfer cost, or unknown.
- **Owner repository** — where the durable fix belongs.
- **Evidence** — logs/artifacts/measurements that demonstrate the issue.
- **Status** — open, upstreamed, fixed-awaiting-consumption, closed.

## Bootstrap expectations

The first implementation phases are expected to pressure at least these areas:

1. fixed-size numeric aggregates and vectorizable math;
2. explicit data layout and ABI stability;
3. images/buffers and safe indexed mutation;
4. deterministic numeric behavior and declared tolerances;
5. target-neutral parallel iteration/dispatch;
6. host/device/shared/local memory semantics or an equivalent machine-native abstraction;
7. synchronization and atomics;
8. GPU-friendly control flow and address-space lowering;
9. SIMD/SIMT lowering without source duplication;
10. capability discovery and requirement expression;
11. reusable surface/window/input runtime boundaries;
12. backend evidence and machine identity capture.

## Rule

A pressure item is not solved by adding host-language glue to this repository. If the missing facility is broadly reusable, solve it at the MNCS language/stdlib/runtime/backend boundary and then consume it here.

## Open pressure

None recorded yet. Bootstrap foundation is deliberately starting with semantics already known to be expressible. The compute-canvas slice should create the first real pressure entries.
