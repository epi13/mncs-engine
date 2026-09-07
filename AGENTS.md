# AGENTS.md

## Mission

`mncs-engine` is the MNCS-native 2D/3D graphics, simulation, and heterogeneous compute pressure engine. Its first responsibility is to expose and document language, stdlib, compiler, runtime, and backend weaknesses through demanding executable workloads.

## Non-negotiable language boundary

Executable project logic in this repository must be MNCS Language.

That includes implementation, tests, benchmarks, examples, generators, pressure harnesses, and project-specific tooling. Do not introduce Rust, C, C++, Python, JavaScript, shell, or another host language to bypass a missing MNCS capability.

Documentation and declarative repository metadata may use their natural formats, but they must not become a hidden implementation layer.

If an unavoidable platform facility is missing, pressure the correct MNCS boundary:

- language semantics -> `mncs-language`;
- reusable primitive/runtime capability -> MNCS stdlib/runtime;
- target lowering/code generation -> MNCS backend/compiler boundary;
- distributed machine selection/execution -> `mncs-fabric`;
- conformance orchestration/evidence enforcement -> `mncs-actions`.

Record unresolved pressure in `docs/PRESSURE.md` instead of silently implementing around it here.

## Architectural constraints

- Keep engine semantics target-neutral wherever possible.
- Prefer capability requirements to vendor/device/model checks.
- Keep reference semantics distinct from optimization strategy.
- Every accelerated path must have a defined correctness oracle or comparison contract.
- Numerical tolerances must be explicit, scoped, and justified.
- Do not treat matching screenshots alone as sufficient proof when structural/numerical evidence is available.
- Keep CUDA/PTX target details in backend-facing contracts, not scattered throughout engine logic.
- Design data structures for deterministic comparison where practical.
- Avoid decorative `.mncs` files. MNCS source should execute or directly support an executable path.

## Language pressure discipline

When a workload cannot be expressed cleanly in MNCS:

1. reduce the problem to the smallest useful reproducer;
2. document the missing semantic or stdlib capability;
3. distinguish parser/type-system/runtime/backend gaps from engine design mistakes;
4. preserve the desired machine-native expression rather than redesigning around current compiler limitations;
5. upstream the pressure to the appropriate MNCS repository;
6. return and replace temporary constraints once the language grows.

## Conformance discipline

A backend is not considered supported because it compiles. Evidence should progressively cover:

- compilation success;
- execution success;
- semantic/numerical equivalence;
- visual/reference equivalence where relevant;
- architecture and device capability record;
- compiler/backend diagnostics;
- performance and resource observations when used for optimization claims.

## Initial definition of done

The bootstrap phase is complete when the repository has a clear MNCS-only boundary, accepted architecture/RFC baseline, a real executable MNCS foundation probe, and a pressure plan that leads directly into a 2D compute canvas and reference rasterizer without requiring a host-language engine implementation.
