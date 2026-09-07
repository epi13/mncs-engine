# RFC 0003 — Fabric Multi-Worker Pressure and CUDA Generation Testing

Status: Draft

## Summary

`mncs-engine` should use Fabric as a heterogeneous execution laboratory. Engine workloads declare capability needs; Fabric resolves them to workers; the resulting evidence is compared across machines, operating systems, architectures and accelerator generations.

## Motivation

A backend that works only on the compiler host is not meaningfully proven. The MNCS family already has multiple workers and is explicitly evolving toward distributed execution. The engine provides high-value workloads for proving that this machinery actually preserves semantics across real systems.

## Worker selection

Engine workloads should not normally name a worker directly. They should describe requirements such as:

- native CPU execution;
- WASM execution/runtime availability;
- CUDA-capable accelerator;
- minimum required numeric or memory capability;
- operating-system/platform requirement where the workload genuinely needs it.

Fabric resolves these requirements against current worker capability records.

Direct worker selection remains useful for diagnostics and reproducibility, but is not the semantic program model.

## Cross-generation CUDA campaign

As soon as two CUDA generations are available, run the same bounded workload corpus on both. Each observation should capture at least:

- engine/workload source identity;
- MNCS compiler/toolchain identity;
- backend and PTX/codegen identity;
- worker identity as a non-secret reproducibility label;
- GPU family/model and compute capability where exposed;
- driver/runtime/toolchain versions relevant to execution;
- output/conformance result;
- declared tolerance contract;
- compile time where measurable;
- kernel/runtime measurements where meaningful;
- resource/codegen diagnostics such as registers/shared memory/occupancy when available and trustworthy.

## Correctness first

The campaign first answers whether semantics survive both generations. Only then should it answer whether target-aware lowering improves performance.

An architecture-specific optimization may produce different machine code and scheduling while remaining conformant. It may not silently change numerical policy or workload meaning.

## Distributed corpus

Initial corpus candidates:

- foundation deterministic probes;
- framebuffer clears and primitive rasterization;
- image transformations;
- vector/matrix workloads;
- particle update kernels at increasing sizes;
- triangle raster workloads;
- the canonical MNCS cube;
- later procedural, collision and ray workloads.

## Evidence aggregation

Fabric should return machine execution observations in a form consumable by MNCS Actions and engine evidence logic. Engine-specific comparison policy remains in this repository; generic worker scheduling belongs in Fabric.

## Failure classification

Failures should distinguish at least:

- capability unavailable;
- toolchain unavailable;
- compile failure;
- launch/execution failure;
- timeout/resource exhaustion;
- semantic divergence;
- evidence capture failure.

'Unknown' should not be treated as success.

## Long-term value

The same mechanism should expand beyond CUDA generations to x86/ARM, Linux/Windows, WASM runtimes and future MNCS backends. The engine becomes a distributed backend conformance corpus rather than a single-machine demo.
