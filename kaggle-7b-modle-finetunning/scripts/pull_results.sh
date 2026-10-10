#!/usr/bin/env bash
# ==============================================================
# pull_results.sh - download the trained adapter/metrics produced by the kernel
#   ./scripts/pull_results.sh            -> results/<kernel>/
# ==============================================================
set -euo pipefail
cd "$(dirname "$0")/.."

set -a; source ./.env; set +a
SLUG="${KAGGLE_KERNEL_SLUG:-7b-qlora-finetune}"
KERNEL_ID="$KAGGLE_USERNAME/$SLUG"
DEST="results/$SLUG"

mkdir -p "$DEST"
echo "[pull] downloading outputs of $KERNEL_ID -> $DEST"
kaggle kernels output "$KERNEL_ID" -p "$DEST" -w
echo "[done] artifacts in $DEST (adapter/, metrics json, samples)"
