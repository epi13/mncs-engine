# Bootstrap foundation

The first implementation slice is intentionally small. `language/mncs/engine/foundation/probe.mncs` exists to prove that `mncs-engine` begins with executable MNCS source before higher-level graphics abstractions are introduced.

The probe currently exercises:

- scalar control flow;
- integer arithmetic and clamping;
- fixed-size sequence input;
- deterministic iteration and accumulation;
- small engine-relevant semantics such as channel clamping and framebuffer linear indexing.

This is not intended to be an engine API. It is a bootstrap executable foothold. The next implementation step should be the compute-canvas slice, where real image storage, mutation, primitive drawing, deterministic artifact comparison, and backend pressure will expose the first substantive language gaps.

## Acceptance rule

Do not expand the foundation with speculative abstractions. New MNCS modules should arrive together with executable pressure or a concrete engine capability.
