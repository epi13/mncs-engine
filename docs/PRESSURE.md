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

## Verification baseline

Unless an entry says otherwise, diagnostics below were verified with
`mncs 0.1.0`, MNCS `0.10`, Source Profile 0.4, via
`mncs source-study` (frontend) and `mncs experiment run` (backends) with
`MNCS_LIBRARY_PATH=<mncs-language>/library:<mncs-engine>/language/mncs`.
Passing reproducers in `language/mncs/pressure/*.mncs` are pinned by
`tests/corpora/pressure-pins.json`, `pressure-shr-u64.json`,
`pressure-isqrt-max.json`, and `pressure-nested-seq.json`.
Known-failing reproducers live in `language/mncs/pressure/rejected/`
with per-file expected diagnostics in that directory's `README.md`.

## Open pressure

### ENG-PRESSURE-0001 — u64 `>>` lowers arithmetically on portable-WASM

- **Area**: backend (mncs-portable-wasm-mvp lowering).
- **Workload**: `engine.math.scalar.isqrt_u64` internals; any u64 halving.
- **Desired MNCS expression**: `(2^64 - 2) >> 1 == 2^63 - 1` on u64.
- **Observed limitation**: the WASM backend sign-extends: it returns
  `18446744073709551615` for `(2^64-2) >> 1` (expected `9223372036854775807`)
  and `13835058055282163712` for `2^63 >> 1` (expected `4611686018427387904`).
- **Minimal reproducer**: `language/mncs/pressure/shr_u64.mncs`
  (`probe_shr_max`, `probe_shr_highbit`), corpus `pressure-shr-u64.json`.
- **Targets affected**: mncs-portable-wasm-mvp. Reference, LLVM-IR, and C11
  return the mathematically correct values.
- **Correctness impact**: divergence (silent wrong values).
- **Cost impact**: engine-wide avoidance — all portable bit extraction uses
  division/modulo arithmetic instead of shifts (see 0009).
- **Owner repository**: `mncs-language` (WASM lowering).
- **Evidence**: `experiment run` over `pressure-shr-u64.json` on four
  backends; WASM `expectation_met=false` with the values above.
- **Status**: open.

### ENG-PRESSURE-0002 — no floating-point type

- **Area**: language semantics / stdlib.
- **Workload**: every engine module (`scalar`, `vec*`, `mat4`, `transform`,
  `quat`, rasterizer, simulation) — all fractional math.
- **Desired MNCS expression**: `fn fmul(a: f64, b: f64) -> f64 { return a * b; }`
- **Observed limitation**: no float type exists, so the engine carries
  Q16.16 fixed point in i64 with hand-rolled truncation contracts
  (`fx_mul`, `fx_div`, `fx_lerp`, trig tables). Rounding policy,
  overflow bounds, and transcendental coverage are engine reinventions.
- **Minimal reproducer**: `language/mncs/pressure/fixed_point.mncs`
  (`1.5 * 2.25 = 3.375` as `fx_mul(98304, 147456) == 221184`).
- **Targets affected**: all.
- **Correctness impact**: none (fixed point is deterministic), but semantic
  distance: engine numerics cannot name the operation they mean.
- **Cost impact**: table-driven trig, manual range analysis per
  multiplication (`|a|,|b| <= 46340` for exact `fx_mul`), unknown SIMD/FPU
  mapping.
- **Owner repository**: `mncs-language` (numeric tower decision).
- **Evidence**: `engine.math.scalar` header design notes; pins
  `pressure-pins#fmul`.
- **Status**: open.

### ENG-PRESSURE-0003 — leading-literal intent-operator typing (NOT REPRODUCED)

- **Area**: type system (elaboration of intent-suffixed operators).
- **Workload**: `engine.math.scalar.neg_wrap_i64`.
- **Desired MNCS expression**: `return 0 -% x;` for `x: i64`.
- **Observed limitation**: none on the current compiler. The historical
  report (left-operand type resolution, literals defaulting to i32) does
  not reproduce: bare `0 -% x`, `0 +% x`, `0 *% y`, and leading-literal
  intent ops in `select` arms all elaborate cleanly.
- **Minimal reproducer**: `language/mncs/pressure/lit_suffix.mncs`
  (now a regression pin, not a failing case).
- **Targets affected**: none observed.
- **Correctness impact**: none.
- **Cost impact**: one defensive binding retained in `neg_wrap_i64`.
- **Owner repository**: `mncs-language` (confirm the relaxation, then this
  entry closes and the defensive binding can go).
- **Evidence**: `source-study` over three scratch variants (return, let,
  select/call-arg positions), zero errors on each.
- **Status**: open (as a confirmation request, not a defect).

### ENG-PRESSURE-0004 — counted iteration capped at `up_to 32`

- **Area**: language semantics (Source Profile 0.4).
- **Workload**: `isqrt_u64` (64 digit/shrink steps), 64-step simulation
  runs, any loop over more than 32 iterations.
- **Desired MNCS expression**: `iterate i up_to 64 carrying h: i64 = 0 { … }`.
- **Observed limitation**: `MNE142` (bound must be 1..32); longer loops must
  be spelled as chained 32-step runs (`steps2/4/8/…`, `isqrt_shrink32` +
  `isqrt_digit32`). The 64-element sequence bound has the same root: FB8 is
  64 lanes because 64 is the cap.
- **Minimal reproducer**: `language/mncs/pressure/rejected/n0004.mncs`
  (`MNE142` + `MNE102` cascade); workaround pin
  `language/mncs/pressure/up_to32.mncs` (`probe_chained64 == 64`).
- **Targets affected**: all.
- **Correctness impact**: unsupported (hard elaboration error).
- **Cost impact**: quadratic source blowup for long fixed loops; chaining
  helpers everywhere.
- **Owner repository**: `mncs-language` (profile bound / counted-loop rule).
- **Evidence**: `source-study` diagnostic `MNE142` quoted in
  `pressure/rejected/README.md`.
- **Status**: open.

### ENG-PRESSURE-0005 — i64 `>>` fails body validation

- **Area**: type system (shift-count typing vs body checker).
- **Workload**: `engine.math.scalar.fx_narrow_trunc` (arithmetic shift
  right by 16 with truncation-toward-zero correction).
- **Desired MNCS expression**: `return x >> 1;` for `x: i64`.
- **Observed limitation**: `MNB017` (integer operand type does not match the
  operation type): shift-count literals elaborate as u64 while the body
  checker demands the count match the value type. Halving must be spelled
  as `/ 2` with manual correction (`fx_narrow_trunc`).
- **Minimal reproducer**: `language/mncs/pressure/rejected/n0005.mncs`
  (`MNB017`); workaround pin `language/mncs/pressure/shr_i64.mncs`.
- **Targets affected**: all (frontend rejection).
- **Correctness impact**: unsupported (hard elaboration error).
- **Cost impact**: division-based narrowing everywhere; the `/`-by-literal
  proof gap of 0008 applies to each site.
- **Owner repository**: `mncs-language` (shift-count literal typing).
- **Evidence**: `source-study` diagnostic `MNB017` quoted in
  `pressure/rejected/README.md`.
- **Status**: open.

### ENG-PRESSURE-0006 — u64 arguments with the high bit set lose it on LLVM-IR/C11 (REFINED)

- **Area**: backend (mncs-llvm-ir, mncs-c11 argument marshaling).
- **Workload**: `math-scalar#isqrt-max`: `isqrt_u64` called with the corpus
  argument `18446744073709551615` (u64).
- **Desired MNCS expression**: pass `2^64 - 1` as a u64 argument; receive
  `2^64 - 1`.
- **Observed limitation**: both backends return `3037000499`, which is
  `floor(sqrt(2^63 - 1))`, not `floor(sqrt(2^64 - 1)) = 4294967295`. The
  isqrt algorithm itself is exonerated: the same value as an in-body
  literal (`pressure.isqrt_max.probe_isqrt_max`) returns the correct
  `4294967295` on reference, LLVM-IR, and C11. The high bit is lost at the
  argument boundary (value arrives as `2^63 - 1`), and downstream code is
  then exactly correct for the wrong input.
- **Minimal reproducer**: corpus case `math-scalar#isqrt-max` (boundary) vs
  `language/mncs/pressure/isqrt_max.mncs` + corpus `pressure-isqrt-max.json`
  (in-body control).
- **Targets affected**: mncs-llvm-ir, mncs-c11. Reference and WASM pass the
  argument intact (WASM fails only the `>>` cases of 0001).
- **Correctness impact**: divergence (silent wrong values for high-bit u64
  inputs at call boundaries).
- **Cost impact**: engine avoids high-bit u64 traffic across call
  boundaries; all pixel/word values stay below 2^32 partly for this reason.
- **Owner repository**: `mncs-language` (LLVM-IR/C11 lowering or the
  experiment argument encoding for those backends).
- **Evidence**: `result.json` artifacts: llvm-ir and c11 both return
  `3037000499` for `math-scalar#isqrt-max` while the in-body probe returns
  `4294967295` on the same backends. Classified in
  `tests/known-divergences.json`.
- **Status**: open (refined this run from "isqrt diverges" to "u64 argument
  high-bit loss"; the isqrt implementation is not at fault).

### ENG-PRESSURE-0007 — enum payload type restrictions

- **Area**: type system (variant payload types).
- **Workload**: `engine.math.transform.Proj` (validated frustum matrix),
  `engine.math.vec4.Homogenized` (perspective divide), camera screen verts.
- **Desired MNCS expression**: `enum E { Ok { m: [i64; 16] }, Bad }` and
  cross-module `enum E { Ok { r: other.Rec }, Bad }`.
- **Observed limitation**: bare-sequence payloads are rejected (`MNE171`,
  with `MNE172`/`MNE177` cascades); cross-module record payloads are
  rejected (`MNB063` on construction, `MNB066` on projection). Workarounds:
  same-module record wrappers (`ProjMat`) and scalar-split payloads
  (`Ok { x, y, z }` + rebuild).
- **Minimal reproducer**:
  `language/mncs/pressure/rejected/n0007b.mncs` (bare sequence),
  `language/mncs/pressure/rejected/n0007.mncs` +
  `n0007lib.mncs` (cross-module record); passing workarounds in
  `language/mncs/pressure/enum_payload.mncs` (pins `wrapped`, `split`).
- **Targets affected**: all (frontend rejection).
- **Correctness impact**: unsupported (hard elaboration errors).
- **Cost impact**: wrapper records and lane-splitting at every fallible
  boundary that wants to return validated aggregates.
- **Owner repository**: `mncs-language` (payload type universe).
- **Evidence**: `source-study` diagnostics quoted in
  `pressure/rejected/README.md`.
- **Status**: open.

### ENG-PRESSURE-0008 — checked-division obligations never discharge statically

- **Area**: compiler (obligation/proof surface) + optimizer.
- **Workload**: `engine.image.color.channel_lerp` (`/ 255`), every
  `unpack_*` (`/ 256`, `/ 65536`), `fx_div` call sites.
- **Desired MNCS expression**: `/ 255` on values the author can prove
  safe, with the divisor-nonzero fact discharged once at compile time.
- **Observed limitation**: division by a nonzero literal is runtime-total
  (a checked failure would trap on zero), but the proof surface exposes
  only opaque `integer-overflow` obligation hashes — no divisor fact, no
  way for engine code to discharge it, no static-totality story. The
  runtime check is therefore permanent at every site.
- **Minimal reproducer**: `language/mncs/pressure/div_oblig.mncs`
  (`255 / 255` still reports 2 `unresolved_obligations`, both
  `obligation:body:integer-overflow:*` with no divisor information).
- **Targets affected**: all.
- **Correctness impact**: none (runtime checks hold).
- **Cost impact**: unremovable runtime checks on hot pixel paths; optimizer
  cannot elide provably-safe divisions.
- **Owner repository**: `mncs-language` (obligation kinds + literal-divisor
  facts).
- **Evidence**: `source-study` `unresolved_obligations` for `div_oblig.mncs`.
- **Status**: open.

### ENG-PRESSURE-0009 — no integer `|`/`&`

- **Area**: language semantics (operator surface; byte-only bitwise ops).
- **Workload**: `engine.image.color` pack/unpack, `engine.simulation.fields`
  hash reduction.
- **Desired MNCS expression**: `(px >> 8) & 255`.
- **Observed limitation**: integer bitwise ops do not exist; channel
  extraction must use `(px / 256) % 256` and packing uses multiply/add.
  Combined with 0001 (no u64 `>>`) and 0005 (no i64 `>>`), no shift-based
  bit manipulation is expressible at all.
- **Minimal reproducer**: `language/mncs/pressure/bitops.mncs`
  (`probe_unpack_b(0xFF0000FF) == 0`).
- **Targets affected**: all.
- **Correctness impact**: none (arithmetic equivalents are exact).
- **Cost impact**: div/mod chains where single backend instructions would
  do; inherits the 0008 proof gap per site.
- **Owner repository**: `mncs-language` (integer operator surface).
- **Evidence**: `color.mncs` pack/unpack bodies; pin `pressure-pins#unpackb`.
- **Status**: open.

### ENG-PRESSURE-0010 — `[u64; N]` cannot be an iteration domain (MNB101)

- **Area**: type system (traversal domains).
- **Workload**: `engine.scene.scene.tri_keys` (triangle key traversal),
  every index-keys array in the engine.
- **Desired MNCS expression**: `let keys: [u64; 12] = […]; iterate k over keys …`.
- **Observed limitation**: `MNB101` (sequence traversal domain must name a
  resolvable element type). All traversal domains must be `[i64; N]` with
  `as u64` casts at use sites.
- **Minimal reproducer**: `language/mncs/pressure/rejected/n0010.mncs`
  (`MNB101`); workaround pin `language/mncs/pressure/seq_domain.mncs`
  (`probe_sum == 66`).
- **Targets affected**: all (frontend rejection).
- **Correctness impact**: unsupported (hard elaboration error).
- **Cost impact**: pervasive `as u64` casts; u64-native indexing
  unexpressible.
- **Owner repository**: `mncs-language` (domain element-type resolution).
- **Evidence**: `source-study` diagnostic `MNB101` quoted in
  `pressure/rejected/README.md`.
- **Status**: open.

### ENG-PRESSURE-0011 — bare nested sequences rejected across module boundaries (REFINED)

- **Area**: type system (cross-module signature types).
- **Workload**: `engine.image.framebuffer.FB16` (`[[i64; 16]; 16]` rows).
- **Desired MNCS expression**: pass `[[i64; 2]; 2]` to (or return it from)
  a function in another module.
- **Observed limitation**: same-module nested sequences elaborate and run
  (pin `pressure-nested-seq#nested == 10`), but any cross-module boundary
  rejects them: arguments fail with `MNE117` + `MNE133`, results with
  `MNE135` + `MNE115`. Stronger than previously recorded: merely
  *importing* a module with such signatures poisons the importer's
  elaboration, so `pressure.pins` cannot even delegate to the nested-seq
  reproducer. The portable carrier is a record wrapper (`FB16 { rows }`),
  which crosses every backend exactly. Earlier notes said "corrupt"; that
  does not reproduce on the current compiler — the failure is a hard
  elaboration error, which is strictly better (loud, not silent).
- **Minimal reproducer**: `language/mncs/pressure/nested_seq.mncs`
  (same-module baseline, pinned); `language/mncs/pressure/rejected/n0011a.mncs`
  (argument) and `n0011b.mncs` (result) with shared `n0011lib.mncs`.
- **Targets affected**: all (frontend rejection).
- **Correctness impact**: unsupported at the boundary; same-module use is fine.
- **Cost impact**: record-wrapping ceremony on every multi-dimensional
  buffer type; no bare grid/tensor signatures anywhere.
- **Owner repository**: `mncs-language` (cross-module type projection for
  nested sequences).
- **Evidence**: `source-study` diagnostics quoted in
  `pressure/rejected/README.md`; import-poisoning shown by the
  `pressure.pins` exclusion comment.
- **Status**: open (refined this run from "corrupt" to "rejected + import
  poisoning").

### ENG-PRESSURE-0012 — no frustum clipping (engine limitation, documented)

- **Area**: engine (reference rasterizer completeness).
- **Workload**: `engine.raster.rasterizer.rasterize_flat` on triangles
  straddling the eye plane.
- **Desired MNCS expression**: a clipped-triangle primitive assembly stage
  (Sutherland–Hodgman or guard-band clipping in clip space).
- **Observed limitation**: only a `w <= 0` guard exists: any triangle with
  a vertex on/behind the eye plane is dropped whole. A straddling triangle
  vanishes instead of clipping. Depth clear `131072` (2.0) and NDC-z tests
  are otherwise exact.
- **Minimal reproducer**: `language/mncs/pressure/clip_guard.mncs`
  (w-zero triangle leaves the clear frame: pin `wzero` equals the
  rasterizer `cull`/`wzero` goldens, cross-module agreement).
- **Targets affected**: all (semantic gap, identical everywhere).
- **Correctness impact**: none (defined behavior), but missing capability:
  close geometry pops out of existence.
- **Cost impact**: unknown (clipping adds per-triangle bounded work; the
  32-iteration cap of 0004 constrains the clipping loop design).
- **Owner repository**: `mncs-engine` (implement once the language can
  express the bounded clip loop cleanly).
- **Evidence**: `raster-rasterizer` cull/wzero goldens; pin
  `pressure-pins#wzero`.
- **Status**: open (engine-side; blocked on nothing, just unbuilt).

### ENG-PRESSURE-0013 — no unbounded sequences (fixed pools only)

- **Area**: language semantics (sequence/table types).
- **Workload**: `engine.simulation.particles.Pool` (16 lanes),
  `engine.scene.scene` (1–2 cube compositions).
- **Desired MNCS expression**: a growable particle list, a scene graph with
  a runtime object count.
- **Observed limitation**: all sequences are fixed-size; there is no
  unbounded list, so pools cannot grow/shrink and scenes are fixed small
  compositions. Emitters recycle lanes; scenes enumerate objects
  statically.
- **Minimal reproducer**: `language/mncs/pressure/fixed_pool.mncs`
  (8-lane ping-pong idiom, pin `pingpong == 2872347482756`).
- **Targets affected**: all.
- **Correctness impact**: unsupported (no dynamic-size type to name).
- **Cost impact**: over-provisioned fixed pools; combinatorial static
  compositions; O(n²) algorithms cannot graduate to indexed structures
  (see 0015).
- **Owner repository**: `mncs-language` (sequence/table type design).
- **Evidence**: `Pool`/`tri_keys` static shapes across engine modules.
- **Status**: open.

### ENG-PRESSURE-0014 — no RNG facility (stdlib gap)

- **Area**: stdlib (randomness/entropy).
- **Workload**: particle emitters, stochastic sampling, procedural
  variation (`engine.simulation.particles.spawn` is a pure function of the
  lane index for exactly this reason).
- **Desired MNCS expression**: a seeded, reproducible random stream
  (`random()` / `fork(seed)` with a stated determinism contract).
- **Observed limitation**: no RNG exists, so stochastic emitters must be
  driven by caller-supplied hash streams. The current stand-in is a
  counter-hashed multiply/add stream (portable by construction: no shifts,
  no bitwise ops, per 0001/0005/0009).
- **Minimal reproducer**: `language/mncs/pressure/hash_stream.mncs`
  (pin `stream4 == 247664`, verified against an independent model).
- **Targets affected**: all.
- **Correctness impact**: none (deterministic stand-in), but every
  stochastic workload hand-rolls its own stream with no shared contract.
- **Cost impact**: duplicated stream code; no capability-gated entropy
  story for targets that have it.
- **Owner repository**: MNCS stdlib (seeded deterministic RNG with a
  machine-native contract).
- **Evidence**: `spawn_*`/`scatter_*` pure-index initializers across
  simulation modules.
- **Status**: open.

### ENG-PRESSURE-0015 — no maps or spatial-index structures (stdlib gap)

- **Area**: language semantics / stdlib (associative structures).
- **Workload**: `engine.simulation.boids.neighbors` (O(n²) neighborhood
  fold over 16 lanes).
- **Desired MNCS expression**: a uniform-grid or hash-map neighbor query
  (`grid_query(cell) -> lanes`).
- **Observed limitation**: no map/dictionary/grid structure exists, so
  neighborhoods cost n² distance tests. The 16-lane pool keeps this
  affordable; a 1024-lane pool would be ~10⁶ tests per step with no
  structural way down.
- **Minimal reproducer**: `language/mncs/pressure/neighborhood.mncs`
  (4-lane fold, pin `nbcounts == 992`: lanes 0↔1 see each other, lane 3
  is lone).
- **Targets affected**: all.
- **Correctness impact**: none (the fold is exact).
- **Cost impact**: algorithmic — O(n²) is the only expressible
  neighborhood; this is the Stage 5 scaling wall.
- **Owner repository**: `mncs-language` + MNCS stdlib (map/grid structures
  with deterministic iteration).
- **Evidence**: `boids.mncs` neighborhood fold; flock16 step cost.
- **Status**: open.

## Deliberately out of scope this run

- CUDA/PTX execution paths (Stage 6): no GPU runs were attempted; PTX
  conformance is unproven on the available Quadro P620.
- Fabric-distributed evidence collection (Stage 7) and verifier/learned
  loops (Stage 8).
- Window/surface/input runtime boundaries (bootstrap expectation 11):
  no workload needed them yet.
- `mncs-actions` conformance orchestration: `scripts/conformance.py`
  remains the orchestrator; no claim is made that it satisfies the Actions
  evidence model.

