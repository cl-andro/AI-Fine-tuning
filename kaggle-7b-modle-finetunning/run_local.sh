#!/usr/bin/env bash
# ==============================================================
# run_local.sh - full local pipeline: prepare data -> validate -> train
#   ./run_local.sh                  full training (needs an NVIDIA GPU)
#   ./run_local.sh --smoke          only 10 steps (quick wiring test)
#   ./run_local.sh --dry-run        config/data validation only (no GPU)
# Extra args are passed through to src/train.py (e.g. --model mistralai/...)
# ==============================================================
set -euo pipefail
cd "$(dirname "$0")"

SMOKE=0
DRY=0
PASSTHRU=()
for arg in "$@"; do
  case "$arg" in
    --smoke) SMOKE=1 ;;
    --dry-run) DRY=1 ;;
    *) PASSTHRU+=("$arg") ;;
  esac
done

# Prefer the project venv, but only if it is actually usable (setup.sh finished)
if [[ -d .venv ]] && .venv/bin/python -c 'import yaml' 2>/dev/null; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
  PY="$(command -v python)"
  echo "[run] using project venv"
else
  PY="$(command -v python3 || command -v python)"
  if [[ -d .venv ]]; then
    echo "[warn] venv incomplete (finish ./setup.sh first) - falling back to $PY"
  fi
fi
echo "[run] interpreter: $PY"

echo "[run] 1/2 preparing dataset ..."
"$PY" src/prepare_data.py --input data/raw --output data/processed

echo "[run] 2/2 training ..."
if [[ $DRY -eq 1 ]]; then
  "$PY" src/train.py --config config.yaml --dry-run ${PASSTHRU[@]+"${PASSTHRU[@]}"}
elif [[ $SMOKE -eq 1 ]]; then
  "$PY" src/train.py --config config.yaml --max-steps 10 ${PASSTHRU[@]+"${PASSTHRU[@]}"}
else
  "$PY" src/train.py --config config.yaml ${PASSTHRU[@]+"${PASSTHRU[@]}"}
fi
