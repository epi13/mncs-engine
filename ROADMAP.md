# mncs-engine roadmap

This roadmap is a pressure sequence, not a feature checklist. Each stage should expose language/backend gaps before the next layer raises complexity.

## Stage 0 — foundation

- Establish MNCS-only implementation policy.
- Land engine charter and architecture RFCs.
- Land a small executable MNCS probe that exercises current stable semantics.
- Create a pressure ledger with owner repository and reproducer expectations.

## Stage 1 — compute canvas

- Pixel/color representation.
- Framebuffer/image storage.
- Clear, point, line, rectangle, circle, triangle.
- Deterministic image serialization or digest semantics.
- CPU/native and WASM execution.
- Define the first CUDA/PTX execution path without introducing target-specific engine semantics.

Exit condition: the same MNCS drawing program produces equivalent evidence on the supported reference and accelerated paths.

## Stage 2 — reference rasterizer

- Vertex representation and transforms.
- Primitive assembly.
- Clipping.
- Triangle setup and rasterization.
- Depth buffering.
- Perspective-correct interpolation.
- Basic texture sampling.

Exit condition: reference images are reproducible and backend comparisons are automated enough to detect regressions.

## Stage 3 — heterogeneous compute

- Express data-parallel work in target-neutral MNCS.
- Exercise buffers, synchronization, work partitioning, address/memory spaces, atomics where justified, and numeric modes.
- Compare CPU, WASM/SIMD where available, and CUDA/PTX implementations.

Exit condition: acceleration does not require applications to encode CUDA thread/block identities into ordinary engine logic.

## Stage 4 — basic 3D

- Vec/matrix/quaternion pressure.
- Cameras and projection.
- Meshes and indexed geometry.
- Depth, textures, lighting and instancing.
- Canonical MNCS cube conformance scene.

Exit condition: one source-level scene is rendered through multiple supported backends with declared tolerances and evidence.

## Stage 5 — simulation pressure

- Particle systems from tiny to multi-million element workloads.
- Boids/spatial neighborhoods.
- Collision broad/narrow phase experiments.
- Procedural fields/terrain.
- Candidate cloth/fluid/voxel/ray workloads.

Exit condition: the engine provides enough realistic parallel pressure to reveal compiler lowering and memory-layout weaknesses.

## Stage 6 — cross-generation CUDA pressure

- Run identical workload corpus on at least two CUDA generations.
- Capture compute capability and relevant backend/toolchain identity.
- Compare correctness first, then compile time, kernel time, memory/resource behavior, and generated-code diagnostics.
- Prevent target-specific tuning from silently changing semantic results.

## Stage 7 — Fabric distributed engine lab

- Express workload requirements as capabilities.
- Dispatch reference and accelerated runs to heterogeneous workers.
- Collect evidence through a stable schema.
- Add architecture diversity beyond CUDA: x86_64, ARM, Windows, alternate Linux environments, WASM, and future targets.

## Stage 8 — verifier and learned advisory loops

- Deterministic micro-verifiers for bounds, races, result equivalence, artifact integrity and regression detection where feasible.
- Micro-debuggers that classify failures and shrink reproducers.
- Advisory micro-models for optimization opportunities such as memory access, occupancy or lowering strategy.
- Never make model output the sole correctness authority.

## Long-term direction

The engine may become generally useful, but usefulness is downstream of its primary architectural role: forcing MNCS to express high-performance visual and simulation workloads cleanly across heterogeneous machines.
