#!/usr/bin/env bash
set -euo pipefail

# Local, no-sudo dependency bootstrap using apt package downloads + extraction.
# Useful when pip/system install is unavailable.

TARGET_DIR="${1:-/tmp/hfpydeps}"
WORK_DIR="${2:-$(pwd)}"

mkdir -p "$TARGET_DIR"
cd "$WORK_DIR"

already_bootstrapped() {
  [[ -d "$TARGET_DIR/usr/lib/python3/dist-packages/pandas" ]] &&
  [[ -d "$TARGET_DIR/usr/lib/python3/dist-packages/numpy" ]] &&
  [[ -d "$TARGET_DIR/usr/lib/python3/dist-packages/scipy" ]] &&
  [[ -d "$TARGET_DIR/usr/lib/python3/dist-packages/requests" ]] &&
  [[ -d "$TARGET_DIR/usr/lib/python3/dist-packages/pytest" ]] &&
  [[ -f "$TARGET_DIR/usr/lib/x86_64-linux-gnu/blas/libblas.so.3" || -f "$TARGET_DIR/usr/lib/x86_64-linux-gnu/libblas.so.3" ]] &&
  [[ -f "$TARGET_DIR/usr/lib/x86_64-linux-gnu/lapack/liblapack.so.3" || -f "$TARGET_DIR/usr/lib/x86_64-linux-gnu/liblapack.so.3" ]]
}

if already_bootstrapped; then
  echo "[bootstrap] Reusing existing local dependencies at $TARGET_DIR"
  echo "[bootstrap] Done. Export these before running the project:"
  echo "export PYTHONPATH=$TARGET_DIR/usr/lib/python3/dist-packages:\$PYTHONPATH"
  echo "export LD_LIBRARY_PATH=$TARGET_DIR/usr/lib/x86_64-linux-gnu/blas:$TARGET_DIR/usr/lib/x86_64-linux-gnu/lapack:$TARGET_DIR/usr/lib/x86_64-linux-gnu:\$LD_LIBRARY_PATH"
  exit 0
fi

PY_PKGS=(
  python3-certifi
  python3-chardet
  python3-dateutil
  python3-decorator
  python3-exceptiongroup
  python3-idna
  python3-importlib-metadata
  python3-iniconfig
  python3-numpy
  python3-packaging
  python3-pandas
  python3-pandas-lib
  python3-pkg-resources
  python3-pluggy
  python3-pytest
  python3-requests
  python3-scipy
  python3-six
  python3-tomli
  python3-tqdm
  python3-tz
  python3-urllib3
)

LIB_PKGS=(
  libblas3
  liblapack3
  libgfortran5
  liblbfgsb0
)

echo "[bootstrap] Downloading Python/runtime packages..."
apt-get download "${PY_PKGS[@]}" "${LIB_PKGS[@]}"

echo "[bootstrap] Extracting packages into $TARGET_DIR ..."
for deb in ./*.deb; do
  dpkg-deb -x "$deb" "$TARGET_DIR"
done

echo "[bootstrap] Done. Export these before running the project:"
echo "export PYTHONPATH=$TARGET_DIR/usr/lib/python3/dist-packages:\$PYTHONPATH"
echo "export LD_LIBRARY_PATH=$TARGET_DIR/usr/lib/x86_64-linux-gnu/blas:$TARGET_DIR/usr/lib/x86_64-linux-gnu/lapack:$TARGET_DIR/usr/lib/x86_64-linux-gnu:\$LD_LIBRARY_PATH"
