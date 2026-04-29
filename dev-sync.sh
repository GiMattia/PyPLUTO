#!/usr/bin/env bash
set -euo pipefail

# Sync or upgrade the project for both uv and pixi.
#
# Usage:
#   ./update_all.sh           # sync/install existing lockfiles
#   ./update_all.sh upgrade   # upgrade, lock, and sync everything
#
# Run from the project root.

if [[ ! -f "pyproject.toml" ]]; then
  echo "Error: run script from the project root (pyproject.toml not found)." >&2
  exit 1
fi

mode="sync"
if [[ $# -gt 0 ]]; then
  case "$1" in
    upgrade)
      mode="upgrade"
      ;;
    *)
      echo "Usage: $0 [upgrade]" >&2
      exit 2
      ;;
  esac
fi

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
    echo ">>> pixi: installing full environment"
    pixi install -e full
  else
    echo ">>> pixi: installing full environment"
    pixi install -e full
  fi
}

echo ">>> Mode: $mode"
run_uv_sync
run_pixi_sync

echo ">>> Done"
