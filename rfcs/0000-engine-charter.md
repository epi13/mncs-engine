# RFC 0000 — Engine Charter and Boundaries

Status: Draft

## Summary

`mncs-engine` is a machine-native 2D/3D graphics, simulation, and heterogeneous compute engine whose primary architectural purpose is to pressure MNCS Language and its execution backends with realistic high-performance workloads.

## Motivation

Synthetic compiler tests are necessary but insufficient. Graphics and simulation combine dense data, numerical semantics, memory layout, parallelism, deterministic comparison, platform interaction and accelerator execution in ways that expose weaknesses quickly. The engine provides a sustained workload corpus where language design and backend correctness can be tested against visible and measurable behavior.

## Decision

The repository will contain MNCS Language as its only executable implementation language. Missing capabilities are treated as pressure on the appropriate MNCS family boundary rather than justification for a permanent host-language escape hatch.

The engine is organized around reusable semantic layers: foundation, math, image, compute, raster, geometry, scene, simulation, render, platform capability contracts and evidence.

## Non-goals

The bootstrap project is not attempting to:

- compete immediately with mature commercial game engines;
- build a vendor-specific CUDA engine API;
- hide missing MNCS functionality behind foreign-language bindings;
- optimize before a correctness oracle exists;
- make machine-learning components authoritative for correctness.

## Pressure-first development

Each substantial feature should answer two questions:

1. Can the workload be expressed naturally and safely in MNCS?
2. Do supported backends preserve its semantics at acceptable cost?

When the answer is no, the reduced failure becomes a language/backend pressure artifact.

## Initial success criteria

The first major milestone is a compute canvas and software rasterizer entirely in MNCS, executable through reference and accelerated paths. The later canonical milestone is a basic 3D scene (the MNCS cube) that runs from the same semantic source across multiple backends with explicit conformance evidence.

## Consequences

This policy will sometimes make engine progress slower than embedding mature foreign libraries. That friction is intentional: the repository exists specifically to expose the places where MNCS must grow.
