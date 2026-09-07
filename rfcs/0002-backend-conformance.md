# RFC 0002 — Backend Conformance and Reference Rendering

Status: Draft

## Summary

Every accelerated engine path is judged against explicit reference semantics. Compilation alone is not backend support.

## Motivation

Graphics and numerical workloads can appear correct while hiding small semantic divergence, precision differences, undefined behavior, race conditions, layout mismatches, or backend-specific assumptions. The engine needs repeatable evidence that distinguishes acceptable numerical tolerance from actual semantic drift.

## Reference paths

Early engine stages should maintain a correctness-oriented reference path that is intentionally simple and inspectable. The software rasterizer is the primary rendering oracle. Similar reference implementations should exist for compute/simulation kernels where practical.

Reference does not mean infinitely precise. Its numeric contract must itself be explicit.

## Conformance levels

A workload/backend pair progresses through these levels:

1. **Compile** — source lowers successfully for the target.
2. **Execute** — the produced program/kernel completes successfully.
3. **Structural equivalence** — dimensions, counts, layouts and required metadata agree.
4. **Numerical equivalence** — numeric outputs satisfy declared exactness/tolerance rules.
5. **Visual equivalence** — rendered outputs satisfy the workload's image-comparison contract.
6. **Operational evidence** — compiler/backend/device identity and diagnostics are captured.
7. **Performance evidence** — timing/resource claims are backed by repeatable observations.

No later level implies an earlier omitted level.

## Golden artifacts

Golden images are useful but should not become opaque binary truth. A visual test should retain enough structured information to explain failure: dimensions, format, deterministic digest, comparison policy, mismatch counts/regions and relevant numeric statistics.

Goldens should be regenerated only when a semantic change is intentional and reviewed.

## Numerical policy

Exact comparison is preferred when semantics permit it. Floating-point workloads may declare absolute/relative/ULP-like tolerances or image-domain error measures once MNCS has the required primitives. Tolerances must be scoped to a workload or operation; there is no repository-wide 'close enough' threshold.

Fast-math or reduced-precision modes are separate contracts, not silent backend choices.

## The MNCS cube

A canonical basic 3D scene will serve as a cross-backend visual conformance workload. Its source-level scene, camera, transforms, geometry, material/texture inputs and comparison rules must be stable enough that CPU/WASM/CUDA and later backends can be compared meaningfully.

## Failure handling

On divergence, preserve both reference and candidate evidence. Where feasible, reduce the workload to a smaller `.mncs` reproducer suitable for `mncs-language` or the affected backend repository.

## Performance

Performance is measured only after correctness. A faster divergent backend is a failing backend for that semantic contract.
