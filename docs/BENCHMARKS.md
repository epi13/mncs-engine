# Engine cost benchmarks (reference backend)

Workloads in `benches/` are fixed MNCS programs with baked digest goldens
(corpus `bench-pool.json`). The cost model is the runner-reported `steps`
field per case on `mncs-research-bytecode` — deterministic for a fixed
workload, so regressions in compiler lowering show up as step changes.
Wall-clock time is deliberately not recorded here: it is host-noisy and
belongs to backend evidence, not to the MNCS programs.

Reference costs (`mncs-research-bytecode`, this run):

| workload (`bench-pool` case) | golden | steps |
| ---------------------------- | ------ | ----- |
| `fountain256`: 256 gravity steps, 16 lanes | `-567740986135572480` | 596132 |
| `flock32`: 32 O(n²) flocking steps, 16 lanes | `2579857818895446407` | 816947 |
| `heightmap`: 16×16 two-octave fbm render | `6857554413083366400` | 194256 |

Notes:

- `heightmap` agrees exactly with the `simulation-fields#heightmap-checksum`
  golden: two independent corpus paths, one value.
- Per-lane step cost is roughly linear: `step64` ≈ 150k steps
  (`simulation-particles`), so `fountain256` ≈ 4× that plus digest.
- Cross-backend step comparison is unproven: each backend reports its own
  `steps`, and whether the unit is commensurable across lowering strategies
  is itself pressure for the evidence model (cf. `docs/PRESSURE.md`).
- Re-run: `python3 scripts/conformance.py --backend <b> bench-pool`, then
  read `steps` from the backend's `result.json` under the evidence dir.
