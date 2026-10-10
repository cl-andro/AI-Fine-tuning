#!/usr/bin/env bash
# ==============================================================
# setup.sh - install dependencies and prepare the environment
#   ./setup.sh           full setup (venv + deps + data check)
#   ./setup.sh --no-venv install deps into current environment
# ==============================================================
set -euo pipefail
cd "$(dirname "$0")/.."

USE_VENV=1
if [[ "${1:-}" == "--no-venv" ]]; then USE_VENV=0; fi

if [[ $USE_VENV -eq 1 ]]; then
  if [[ ! -d .venv ]]; then
    echo "[setup] creating virtual environment..."
    python3 -m venv .venv
  fi
  source .venv/bin/activate
  echo "[setup] using venv: $(which python)"
else
  echo "[setup] using system python: $(which python)"
fi

echo "[setup] upgrading pip..."
python -m pip install --upgrade pip -q

echo "[setup] installing requirements..."
pip install -r requirements.txt -q

echo "[setup] checking CUDA availability..."
python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"

if [[ -f .env ]]; then
  echo "[setup] .env found - loading..."
  set -a; source ./.env; set +a
else
  echo "[setup] .env not found - copying from .env.example"
  cp .env.example .env
  echo "[setup] edit .env with your credentials"
fi

echo ""
echo "[setup] done. Next steps:"
echo "  1. Place your training data in data/raw/ (or set TRAIN_DATASET_PATH in .env)"
echo "  2. Run: python src/train.py --dry-run"
echo "  3. Run: python src/train.py --config config.yaml"
echo "  4. Or push to Kaggle: ./scripts/push_kernel.sh"