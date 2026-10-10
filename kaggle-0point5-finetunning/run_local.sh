#!/usr/bin/env bash
# ==============================================================
# run_local.sh - run training locally (requires GPU)
#   ./run_local.sh              full training
#   ./run_local.sh --dry-run    validate config + data only
#   ./run_local.sh --steps 100  quick smoke test (100 steps)
# ==============================================================
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ ! -d .venv ]]; then
  echo "[error] .venv not found - run ./setup.sh first"
  exit 1
fi
source .venv/bin/activate

if [[ -f .env ]]; then
  set -a; source ./.env; set +a
fi

EXTRA_ARGS=()
if [[ "${1:-}" == "--dry-run" ]]; then
  EXTRA_ARGS=(--dry-run)
elif [[ "${1:-}" == "--steps" && -n "${2:-}" ]]; then
  EXTRA_ARGS=(--max-steps "$2")
fi

python src/train.py --config config.yaml "${EXTRA_ARGS[@]}" "$@"