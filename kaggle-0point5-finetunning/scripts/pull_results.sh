#!/usr/bin/env bash
# ==============================================================
# pull_results.sh - download the latest kernel output artifacts
#   ./pull_results.sh [KERNEL_SLUG]
# ==============================================================
set -euo pipefail
cd "$(dirname "$0")/.."

set -a; source ./.env; set +a
KAGGLE_USERNAME="${KAGGLE_USERNAME:-YOUR_KAGGLE_USERNAME}"
SLUG="${1:-${KAGGLE_KERNEL_SLUG:-0point5-qlora-finetune}}"
KERNEL_ID="$KAGGLE_USERNAME/$SLUG"

mkdir -p outputs
echo "[pull] downloading outputs from $KERNEL_ID ..."
kaggle kernels output "$KERNEL_ID" -p outputs/ || {
  echo "[error] pull failed - check kernel id and that the run finished"
  exit 1
}
echo "[done] artifacts in outputs/:"
find outputs/ -type f | head -30