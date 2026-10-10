#!/usr/bin/env bash
# ==============================================================
# push_dataset.sh - upload data/raw as a Kaggle dataset
#   ./push_dataset.sh "My Custom Training Set" my-custom-training-set
#   ./push_dataset.sh                  (uses default title/slug)
#   ./push_dataset.sh --stage-only     build .build/dataset only (no creds needed)
# First run creates the dataset, later runs push a new version.
# ==============================================================
set -euo pipefail
cd "$(dirname "$0")/.."

STAGE_ONLY=0
if [[ "${1:-}" == "--stage-only" ]]; then STAGE_ONLY=1; shift; fi

set -a; source ./.env; set +a
if [[ $STAGE_ONLY -eq 0 && (-z "${KAGGLE_USERNAME:-}" || "${KAGGLE_KEY:-}" == your_kaggle_key*) ]]; then
  echo "[error] fill KAGGLE_USERNAME / KAGGLE_KEY in .env first"; exit 1
fi
KAGGLE_USERNAME="${KAGGLE_USERNAME:-YOUR_KAGGLE_USERNAME}"

TITLE="${1:-SQL Training Set 0.5B Finetune}"
SLUG="${2:-sql-training-set-0point5-finetune}"
STAGE=".build/dataset"

rm -rf "$STAGE"; mkdir -p "$STAGE"
cp data/raw/* "$STAGE"/ 2>/dev/null || { echo "[error] nothing in data/raw/"; exit 1; }
cat > "$STAGE/dataset-metadata.json" <<EOF
{
  "title": "$TITLE",
  "id": "$KAGGLE_USERNAME/$SLUG",
  "licenses": [{"name": "CC0-1.0"}]
}
EOF
echo "[stage] dataset bundle built at $STAGE:"
find "$STAGE" -type f | sort
if [[ $STAGE_ONLY -eq 1 ]]; then
  echo "[stage-only] skipping kaggle upload (no credentials used)"
  exit 0
fi

echo "[push] uploading dataset $KAGGLE_USERNAME/$SLUG ..."
kaggle datasets create -p "$STAGE" || kaggle datasets create "$STAGE" || {
  echo "[error] dataset create failed"; exit 1; }
echo "[done] dataset published: https://www.kaggle.com/datasets/$KAGGLE_USERNAME/$SLUG"