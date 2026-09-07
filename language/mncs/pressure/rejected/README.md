# Known-failing reproducers

Every `.mncs` file in this directory except `*lib.mncs` is rejected at
elaboration by design. They are the minimized negative cases behind the
`ENG-PRESSURE-*` ledger entries in `docs/PRESSURE.md`. Do not "fix" them
into compiling: a fix belongs in `mncs-language`, after which the file
should be re-verified and either promoted to a passing pin or deleted.

Verify one (expects exactly the listed codes, non-zero exit):

```sh
export MNCS_LIBRARY_PATH=<mncs-language>/library:<mncs-engine>/language/mncs
mncs source-study language/mncs/pressure/rejected/<file>.mncs
```

| file | pressure | expected diagnostics |
| ---- | -------- | -------------------- |
| `n0004.mncs` | 0004 | `MNE142` (bound must be 1..32) + `MNE102` cascade |
| `n0005.mncs` | 0005 | `MNB017` (shift operand type) |
| `n0007.mncs` + `n0007lib.mncs` | 0007 | `MNB063` + `MNB066` (cross-module record payload) |
| `n0007b.mncs` | 0007 | `MNE171` + `MNE172`/`MNE177` cascades (bare-sequence payload) |
| `n0010.mncs` | 0010 | `MNB101` (u64 traversal domain) |
| `n0011a.mncs` + `n0011lib.mncs` | 0011 | `MNE117` + `MNE133` (nested-seq argument) |
| `n0011b.mncs` + `n0011lib.mncs` | 0011 | `MNE135` + `MNE115` (nested-seq result) |
| `n0018.mncs` | 0018 | `MNE105` (over-long sequence type) + `MNE186` cascade |
| `n0019.mncs` | 0019 | `MNP123` + `MNP127`/`MNP128`/`MNP007` (generic record header) |
| `n0020.mncs` | 0020 | `MNP157` + `MNP061` desync (repeat literal) |
| `n0021.mncs` | 0021 | `MNE110` (rebinding in the same scope) |

The `*lib.mncs` callees elaborate cleanly on their own; the failure is at
the cross-module boundary in the caller.
