# Architecture

## Purpose

`mncs-engine` is an execution pressure system organized around visual, spatial, numerical, and heterogeneous compute workloads. It should remain useful as an engine, but architecture decisions are judged first by whether they let MNCS express those workloads cleanly and portably.

## Semantic layers

### Foundation

Small deterministic semantics used to prove the current compiler/runtime path before higher-level engine code depends on it.

### Math

Scalar policy, vectors, matrices, transforms, quaternions, interpolation and geometry-oriented numeric operations. Math should avoid target-specific spellings unless the language itself defines them as portable semantics.

### Image

Pixels, color representation, images, framebuffers and deterministic artifact/digest behavior.

### Compute

Target-neutral parallel work description, buffers, dispatch, synchronization and capability requirements. CUDA-specific execution details are backend concerns.

### Raster

The correctness-oriented software rendering path. This provides an understandable oracle for later accelerated rendering.

### Geometry / Scene

Meshes, primitives, transforms, cameras and scene representation. Data organization should remain amenable to CPU and GPU execution and should pressure MNCS memory-layout facilities rather than hiding them.

### Simulation

Particles and other data-parallel systems that provide sustained heterogeneous-compute pressure independently of rendering.

### Render

Coordinates rendering work while preserving the distinction between scene semantics, reference rendering and optimized execution.

### Platform boundary

Surfaces, display presentation and input are capabilities needed by interactive examples, not permission to place a conventional host-language platform layer inside this repository. Missing platform primitives should be supplied through reusable MNCS runtime/stdlib boundaries.

### Evidence

Every serious pressure run should be representable as observations: source/workload identity, compiler/backend identity, machine capabilities, outputs, comparison result, tolerances, diagnostics and performance/resource measurements where meaningful.

## Backend model

Backends are implementations of MNCS semantics, not separate engine APIs. Ordinary engine code should not fork into `cpu_engine`, `cuda_engine`, and `wasm_engine` implementations.

Where semantics genuinely differ—for example, availability of a capability—the difference must be explicit in the program contract and evidence rather than inferred from a vendor string.

## Reference vs optimized paths

The reference path is intentionally allowed to be slower. Its job is to make behavior legible and reproducible. Optimized paths may restructure work aggressively, but their acceptance is governed by the conformance contract in RFC 0002.

## Repository boundary

This repository owns engine semantics and engine pressure workloads. It does not own:

- general-purpose compiler semantics;
- CUDA/PTX code generation;
- generic windowing/runtime primitives that belong in reusable MNCS facilities;
- distributed scheduling policy owned by Fabric;
- repository-family conformance orchestration owned by MNCS Actions.

The engine should expose inadequacies in those boundaries with reduced reproducers and evidence.
