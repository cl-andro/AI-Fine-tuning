#!/usr/bin/env bash
# ==============================================================
# push_kernel.sh - bundle notebook + src + config + sample data and
#                  push it to Kaggle as a GPU kernel, then (optionally) run it.
#   ./push_kernel.sh               push only
#   ./push_kernel.sh --run         push, then wait until it finishes
#   ./push_kernel.sh --stage-only  build .build/kernel and exit (no creds needed)
# ==============================================================
set -euo pipefail
cd "$(dirname "$0")/.."

RUN=0
STAGE_ONLY=0
for arg in "$@"; do
  case "$arg" in
    --run) RUN=1 ;;
    --stage-only) STAGE_ONLY=1 ;;
    *) echo "unknown option: $arg"; exit 1 ;;
  esac
done

set -a; source ./.env; set +a
if [[ $STAGE_ONLY -eq 0 && (-z "${KAGGLE_USERNAME:-}" || "${KAGGLE_KEY:-}" == your_kaggle_key*) ]]; then
  echo "[error] fill KAGGLE_USERNAME / KAGGLE_KEY in .env first"; exit 1
fi
KAGGLE_USERNAME="${KAGGLE_USERNAME:-YOUR_KAGGLE_USERNAME}"
SLUG="${KAGGLE_KERNEL_SLUG:-0point5-qlora-finetune}"
KERNEL_ID="$KAGGLE_USERNAME/$SLUG"
STAGE=".build/kernel"

rm -rf "$STAGE"; mkdir -p "$STAGE"
cp notebook/kaggle_0point5_finetune.ipynb "$STAGE"/
cp config.yaml requirements.txt .env.example "$STAGE"/ 2>/dev/null || true
mkdir -p "$STAGE/src" "$STAGE/data/raw" "$STAGE/scripts"
cp src/*.py "$STAGE/src"/
cp data/raw/* "$STAGE/data/raw"/ 2>/dev/null || true
cp scripts/*.sh "$STAGE/scripts"/ 2>/dev/null || true
sed "s|YOUR_KAGGLE_USERNAME|$KAGGLE_USERNAME|g; s|SLUG_PLACEHOLDER|$SLUG|g" \
    notebook/kernel-metadata.json > "$STAGE/kernel-metadata.json"

echo "[stage] kernel bundle built at $STAGE:"
find "$STAGE" -type f | sort
if [[ $STAGE_ONLY -eq 1 ]]; then
  echo "[stage-only] skipping kaggle push (no credentials used)"
  exit 0
fi

echo "[push] pushing kernel $KERNEL_ID ..."
kaggle kernels push -p "$STAGE"
echo "[done] kernel pushed: https://www.kaggle.com/code/$KERNEL_ID"

if [[ $RUN -eq 1 ]]; then
  echo "[run] starting kernel (GPU required in kernel settings) ..."
  kaggle kernels run "$KERNEL_ID" -w
fi
echo "tip: after it finishes, fetch artifacts with ./scripts/pull_results.sh"