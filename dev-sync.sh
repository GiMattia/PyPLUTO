#!/usr/bin/env bash
set -euo pipefail

# Sync or upgrade the project for uv and pixi.
#
# Usage:
#   ./dev-sync.sh                # sync/install existing lockfiles
#   ./dev-sync.sh upgrade        # upgrade, lock, and sync everything
#
# Run from the PyPLUTO project root.

if [[ ! -f "pyproject.toml" ]]; then
  echo "Error: run script from the project root (pyproject.toml not found)." >&2
  exit 1
fi

mode="sync"

for arg in "$@"; do
  case "$arg" in
    upgrade)
      mode="upgrade"
      ;;
    *)
      echo "Usage: $0 [upgrade]" >&2
      exit 2
      ;;
  esac
done

have_cmd() {
  command -v "$1" >/dev/null 2>&1
}

run_uv_sync() {
  if ! have_cmd uv; then
    echo ">>> uv not found; skipping uv"
    return 0
  fi

  if [[ "$mode" == "upgrade" ]]; then
    echo ">>> uv: upgrading, locking, and syncing all extras and groups"
    uv sync --all-extras --all-groups --upgrade
  else
    echo ">>> uv: syncing all extras and groups"
    uv sync --all-extras --all-groups
  fi
}

run_pixi_sync() {
  if ! have_cmd pixi; then
    echo ">>> pixi not found; skipping pixi"
    return 0
  fi

  if [[ "$mode" == "upgrade" ]]; then
    echo ">>> pixi: updating lockfile"
    pixi update
  fi

  echo ">>> pixi: installing full environment"
  pixi install -e full

  if pixi project environment list >/dev/null 2>&1; then
    echo ">>> pixi: installing local-dev environment"
    pixi install -e local-dev || true
  fi
}

echo ">>> Mode: $mode"

run_uv_sync
run_pixi_sync

echo ">>> Done"
