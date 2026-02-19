#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="${1:-/tmp/hfpydeps}"

export PYTHONPATH="$TARGET_DIR/usr/lib/python3/dist-packages:${PYTHONPATH:-}"
export LD_LIBRARY_PATH="$TARGET_DIR/usr/lib/x86_64-linux-gnu/blas:$TARGET_DIR/usr/lib/x86_64-linux-gnu/lapack:$TARGET_DIR/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH:-}"

echo "PYTHONPATH=$PYTHONPATH"
echo "LD_LIBRARY_PATH=$LD_LIBRARY_PATH"
