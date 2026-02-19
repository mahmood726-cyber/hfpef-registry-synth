#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="${HFDEPS_DIR:-/tmp/hfpydeps}"
if [[ $# -eq 0 ]]; then
  echo "Usage: $0 <command> [args...]" >&2
  exit 1
fi

export PYTHONPATH="$TARGET_DIR/usr/lib/python3/dist-packages:${PYTHONPATH:-}"
export LD_LIBRARY_PATH="$TARGET_DIR/usr/lib/x86_64-linux-gnu/blas:$TARGET_DIR/usr/lib/x86_64-linux-gnu/lapack:$TARGET_DIR/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH:-}"

exec "$@"
