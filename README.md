# mncs-engine

Machine-native 2D/3D graphics, simulation, and heterogeneous compute engine for MNCS, designed to pressure language semantics and backend correctness across CPU, WASM, CUDA/PTX, and future targets.

`mncs-engine` begins as a language and backend pressure system, not as a conventional game engine. The goal is to make demanding spatial, numerical, rendering, simulation, and massively parallel workloads first-class MNCS programs and use their behavior as evidence about the language, standard library, compiler, runtimes, and backends.

## Principles

- **MNCS all the way down.** Executable implementation, tests, benchmarks, tools, and examples in this repository are MNCS Language. Platform-specific host implementations do not belong here.
- **Pressure before convenience.** When the engine exposes a language or stdlib gap, record and pressure the gap rather than hiding it behind Rust, C, C++, Python, JavaScript, shell, or vendor glue.
- **One semantic program, many machines.** Workloads should be expressible once and evaluated across CPU, WASM, CUDA/PTX, and later backends without embedding target identity into ordinary engine logic.
- **Evidence-backed conformance.** Backend claims require executable evidence: output equivalence, tolerances, visual/reference artifacts, diagnostics, and performance measurements where relevant.
- **Capabilities over device names.** Engine programs describe required and preferred capabilities; Fabric and backend selection resolve those requirements onto available workers.
- **Correctness before acceleration.** A deterministic or well-specified reference path is the oracle from which accelerated implementations are judged.

## Initial architecture

The intended MNCS module tree is:

```text
language/mncs/engine/
  foundation/    semantic primitives and invariant probes
  math/          vectors, matrices, transforms, numeric policy
  image/         pixels, images, color and framebuffer representation
  raster/        software rasterization and reference rendering
  scene/         cameras, meshes and scene representation
  simulation/    particles, boids and procedural fields
  render/        2D primitives (draw2d) independent of a vendor API
language/mncs/pressure/
                 minimized reproducers per ENG-PRESSURE-* ID, the pins
                 regression net, and documented known-failing cases
examples/        standalone MNCS programs (fountain, flock)
benches/         deterministic cost workloads with step budgets
tests/corpora/   baked expectations run by scripts/conformance.py
docs/            architecture, pressure ledger, benchmarks, guidance
```

Only `engine/`, `pressure/`, `examples/`, and `benches/` hold executable
MNCS. Not yet started: `compute/` (target-neutral parallelism),
`platform/` (window/input/surface contracts), `evidence/` (observation
schema). The repository should not accumulate decorative placeholder modules.

## First pressure ladder

1. **Foundation probes** — numeric and deterministic semantics that compile everywhere.
2. **Compute canvas** — framebuffer creation plus pixel/line/triangle primitives.
3. **Reference rasterizer** — a software pipeline implemented in MNCS.
4. **CUDA/PTX acceleration** — accelerate the same semantic workloads without changing their meaning.
5. **Basic 3D** — transforms, clipping, depth, interpolation, textures, lighting, camera and meshes.
6. **Simulation pressure** — particles, boids, collision, procedural fields and other data-parallel workloads.
7. **Cross-generation CUDA conformance** — run identical workloads on multiple CUDA generations and compare correctness, diagnostics and cost.
8. **Distributed pressure** — use Fabric workers to collect backend and architecture evidence across the MNCS machine fleet.

A long-term canonical test is **the MNCS cube**: the same MNCS source renders a reference scene across supported backends, with evidence showing semantic equivalence within explicitly declared tolerances.

## Repository map

- `language/mncs/` — all executable project implementation.
- `examples/` — executable MNCS examples and pressure programs.
- `rfcs/` — design decisions and proposed engine contracts.
- `docs/` — architecture, pressure ledger, evidence model and project guidance.
- `AGENTS.md` — constraints for human and agent contributors.
- `ROADMAP.md` — staged pressure and implementation sequence.

## RFCs

The bootstrap RFC set defines the project before large implementation begins:

- **RFC 0000 — Engine Charter and Boundaries**
- **RFC 0001 — Execution, Capability and Memory-Space Abstraction**
- **RFC 0002 — Backend Conformance and Reference Rendering**
- **RFC 0003 — Fabric Multi-Worker Pressure and CUDA Generation Testing**
- **RFC 0004 — Verifier Evidence and Micro-Model Feedback Loops**

See [`rfcs/README.md`](rfcs/README.md).

## Relationship to the MNCS family

`mncs-engine` is a consumer and pressure source for `mncs-language` and its stdlib/backends. It should integrate with Fabric for heterogeneous execution and with MNCS Actions for evidence-backed conformance once those boundaries are wired. Micro-verifiers and learned advisory components may consume engine evidence, but correctness must not depend on an opaque model prediction.

## Current status

Pressure campaign 01 (this run): 25 corpora, all passing on
`mncs-research-bytecode`, covering math (scalar/vec2/vec3/vec4/mat4/
transform/quat/geometry), image (color/framebuffer), render/draw2d,
rasterizer, scene (mesh/camera/cube scene), simulation
(particles/boids/fields), two rendered examples, one cost benchmark,
and the pressure regression pins. The 5-backend matrix (25 corpora ×
reference/WASM/LLVM-IR/C11/Cranelift = 125 cells) stands at 121 PASS +
4 classified known divergences (`tests/known-divergences.json`:
`math-scalar#isqrt-max` on LLVM-IR/C11 under ENG-PRESSURE-0006,
`pressure-shr-u64` on WASM under ENG-PRESSURE-0001), zero unclassified
failures. Run it with `scripts/conformance.py --matrix`. The pressure ledger (`docs/PRESSURE.md`)
holds ENG-PRESSURE-0001..0015 with minimized reproducers; two entries
were refined by evidence this run (0006 is u64 argument high-bit loss,
not isqrt; 0011 is elaboration rejection, not corruption) and one did
not reproduce (0003). Deliberately unproven: PTX/GPU execution, Fabric
distribution, verifier loops, window/input boundaries.

## License

Apache-2.0, consistent with the MNCS project family.
