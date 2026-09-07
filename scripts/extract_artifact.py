#!/usr/bin/env python3
"""Copy experiment-returned byte buffers verbatim to disk (transport only).

Usage:
    extract_artifact.py <result.json> <output> <case-id> [<case-id> ...]

Each named case must have returned a byte sequence (flat or nested). Values
are concatenated in the given case order. This script knows NOTHING about
pixels, colors, headers, or layout: byte order and meaning live entirely in
the MNCS probes named on the command line. If engine semantics ever leak in
here, that is a policy violation (see engine.render.ppm header comment).
"""
import json
import sys


def flat(value, out):
    if isinstance(value, dict):
        if "byte" in value:
            out.append(value["byte"]["value"])
        elif "sequence" in value:
            for item in value["sequence"]["values"]:
                flat(item, out)
        else:
            raise ValueError("non-byte leaf: %r" % (value,))
    else:
        raise ValueError("unexpected value: %r" % (value,))


def main():
    result_path, output_path, case_ids = sys.argv[1], sys.argv[2], sys.argv[3:]
    with open(result_path) as fh:
        result = json.load(fh)
    by_id = {c["case_id"]: c for c in result.get("cases", [])}
    raw = bytearray()
    for cid in case_ids:
        case = by_id[cid]
        assert case["status"] == "returned", cid
        assert case.get("expectation_met", True), cid
        for value in case["returned"]:
            flat(value, raw)
    with open(output_path, "wb") as fh:
        fh.write(bytes(raw))
    print("wrote %d bytes to %s" % (len(raw), output_path))


if __name__ == "__main__":
    main()
