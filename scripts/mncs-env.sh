#!/bin/sh
# mncs-env.sh — source this to point MNCS tooling at the language stdlib and
# the mncs-engine module tree for `use` resolution.
#   . scripts/mncs-env.sh
ENGINE_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LANG_ROOT="${MNCS_LANGUAGE_ROOT:-/home/epi13/Documents/Projects/mncs-language}"
export MNCS_LIBRARY_PATH="$LANG_ROOT/library:$ENGINE_ROOT/language/mncs"
export MNCS_BIN="${MNCS_BIN:-$LANG_ROOT/target/debug/mncs}"
export MNCS_ENGINE_ROOT="$ENGINE_ROOT"
