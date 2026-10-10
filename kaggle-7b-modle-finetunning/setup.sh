#!/usr/bin/env bash
# ==============================================================
# setup.sh - one-shot local environment setup
#   ./setup.sh              create .venv + install deps + wire Kaggle creds
#   ./setup.sh --system     use current python instead of creating .venv
#   ./setup.sh --verify     additionally verify kaggle auth (hits the API)
# ==============================================================
set -euo pipefail
cd "$(dirname "$0")"

USE_VENV=1
VERIFY=0
for arg in "$@"; do
  case "$arg" in
    --system) USE_VENV=0 ;;
    --verify) VERIFY=1 ;;
    *) echo "unknown option: $arg"; exit 1 ;;
  esac
done

echo "== Kaggle 7B fine-tune setup =="

# --- 1. Secrets file -------------------------------------------------
if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "[setup] created .env from .env.example - EDIT IT with your real keys"
fi
chmod 600 .env .env.example 2>/dev/null || true

# --- 2. Python environment ------------------------------------------
if [[ $USE_VENV -eq 1 ]]; then
  if [[ ! -d .venv ]]; then
    python3 -m venv .venv
    echo "[setup] created virtualenv .venv"
  fi
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi
PY="$(command -v python || command -v python3)"
echo "[setup] interpreter: $PY"
if [[ $USE_VENV -eq 1 ]]; then
  "$PY" -m pip install --upgrade pip
fi
echo "[setup] installing requirements ..."
"$PY" -m pip install -r requirements.txt

# --- 3. Kaggle credentials from .env -> ~/.kaggle/kaggle.json ---------
K_USER="$(grep -E '^KAGGLE_USERNAME=' .env | cut -d= -f2- | tr -d '"'"'"' ')"
K_KEY="$(grep -E '^KAGGLE_KEY=' .env | cut -d= -f2- | tr -d '"'"'"' ')"
if [[ -n "$K_USER" && -n "$K_KEY" && "$K_KEY" != your_kaggle_key* && "$K_KEY" != your_kaggle_key ]]; then
  mkdir -p ~/.kaggle
  printf '{"username":"%s","key":"%s"}\n' "$K_USER" "$K_KEY" > ~/.kaggle/kaggle.json
  chmod 600 ~/.kaggle/kaggle.json
  # make the modern kaggle CLI pick up the legacy credentials file too
  export KAGGLE_USERNAME="$K_USER"
  export KAGGLE_KEY="$K_KEY"
  echo "[setup] wrote ~/.kaggle/kaggle.json (chmod 600)"
else
  echo "[setup] KAGGLE_USERNAME/KAGGLE_KEY still placeholders in .env - skipping kaggle.json"
  echo "        Get them from: https://www.kaggle.com/settings -> API -> Create New Token"
fi

# --- 4. Sanity checks -------------------------------------------------
"$PY" - <<'PY'
import importlib, sys
missing = []
for mod in ("yaml", "dotenv", "kaggle"):
    try:
        importlib.import_module(mod)
    except ImportError:
        missing.append(mod)
heavy = []
for mod in ("torch", "transformers", "peft", "trl", "datasets", "accelerate", "bitsandbytes"):
    try:
        importlib.import_module(mod)
    except ImportError:
        heavy.append(mod)
print("[setup] light deps missing :", missing or "none")
print("[setup] GPU deps missing   :", heavy or "none", "(needed only for training/inference)")
if missing:
    sys.exit(1)
PY

if [[ $VERIFY -eq 1 ]]; then
  echo "[setup] verifying kaggle auth ..."
  kaggle whoami || true
fi

echo ""
echo "== Setup complete =="
echo "  next: python src/prepare_data.py --input data/raw --output data/processed"
echo "        python src/train.py --dry-run        # validate"
echo "        ./run_local.sh                       # full run (needs GPU)"
