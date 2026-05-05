#!/usr/bin/env bash
set -euo pipefail

# Sync or upgrade the project for uv, pixi, and optionally local rustronomy.
#
# Usage:
#   ./dev-sync.sh                # sync/install existing lockfiles
#   ./dev-sync.sh upgrade        # upgrade, lock, and sync everything
#   ./dev-sync.sh rust           # sync + build/install local rustronomy
#   ./dev-sync.sh upgrade rust   # upgrade everything + build/install rustronomy
#
# Run from the PyPLUTO project root.

if [[ ! -f "pyproject.toml" ]]; then
  echo "Error: run script from the project root (pyproject.toml not found)." >&2
  exit 1
fi

mode="sync"
with_rustronomy=false

for arg in "$@"; do
  case "$arg" in
    upgrade)
      mode="upgrade"
      ;;
    rust|rustronomy)
      with_rustronomy=true
      ;;
    *)
      echo "Usage: $0 [upgrade] [rust]" >&2
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

ensure_venv_pip() {
  local py=".venv/bin/python"

  if [[ ! -x "$py" ]]; then
    echo ">>> .venv Python not found; running uv sync first"
    uv sync --all-extras --all-groups
  fi

  if ! "$py" -m pip --version >/dev/null 2>&1; then
    echo ">>> pip missing in .venv; installing pip"
    "$py" -m ensurepip --upgrade
    "$py" -m pip install --upgrade pip
  fi
}

run_rustronomy_sync() {
  if [[ "$with_rustronomy" != true ]]; then
    return 0
  fi

  if [[ ! -f "../rustronomy/Cargo.toml" ]]; then
    echo ">>> rustronomy not found at ../rustronomy; skipping"
    return 0
  fi

  if ! have_cmd uv; then
    echo ">>> uv not found; cannot install rustronomy into PyPLUTO venv"
    return 1
  fi

  ensure_venv_pip

  echo ">>> uv: building/installing rustronomy release build"
  uv sync --all-extras --all-groups --reinstall-package rustronomy

  if have_cmd pixi; then
    echo ">>> pixi: building/installing rustronomy release build"
    pixi run -e local-dev rustronomy-release || true
  fi

  echo ">>> checking rustronomy import"
  uv run python -c "import rustronomy; print('rustronomy OK')"
}

echo ">>> Mode: $mode"
echo ">>> Rustronomy: $with_rustronomy"

run_uv_sync
run_pixi_sync
run_rustronomy_sync

echo ">>> Done"