# Kaggle 7B Model Fine-tuning (QLoRA)

Fine-tune a **7B instruction model** on your **custom training set** — locally prepared,
trained on **Kaggle's free GPU** (T4/P100/L4), using **QLoRA** (4-bit base + LoRA adapters)
so a single 16 GB GPU is enough.

Default base model: `Qwen/Qwen2.5-7B-Instruct` (ungated). Swap it in `config.yaml` / `.env`
for Mistral-7B, Llama-3.1-8B (gated, needs `HF_TOKEN`), Phi-3.5, or any HF/local model.

## Folder layout

```
kaggle-7b-modle-finetunning/
├── README.md                  # you are here
├── requirements.txt           # python dependencies
├── config.yaml                # model + LoRA + training hyperparameters
├── .env / .env.example        # SECRETS (chmod 600, git-ignored)
├── setup.sh                   # one-shot local setup (venv + deps + kaggle creds)
├── run_local.sh               # prepare data -> validate -> train locally
├── data/
│   ├── raw/                   # 👉 DROP YOUR CUSTOM TRAINING SET HERE (jsonl/json/csv)
│   │   └── sample_data.jsonl  # sample set so the pipeline runs out-of-the-box
│   └── processed/             # generated train.jsonl / val.jsonl
├── src/
│   ├── prepare_data.py        # any format -> chat-format train/val JSONL (stdlib only)
│   ├── train.py               # QLoRA training (supports --dry-run, auto-resume)
│   └── inference.py           # chat with base model + adapter
├── scripts/
│   ├── push_dataset.sh        # upload data/raw as a Kaggle dataset
│   ├── push_kernel.sh         # push the notebook (+src/config/data) to Kaggle
│   └── pull_results.sh        # download trained adapter/metrics from Kaggle
└── notebook/
    ├── kaggle_7b_finetune.ipynb   # the Kaggle GPU notebook
    └── kernel-metadata.json       # kernel settings (GPU, private)
```

## Quick start

### 1. Configure secrets (once)

```bash
cd kaggle-7b-modle-finetunning
cp .env.example .env && nano .env   # then: chmod 600 .env
```

| Variable | Where to get it | Required? |
|---|---|---|
| `KAGGLE_USERNAME` / `KAGGLE_KEY` | Kaggle → Settings → API → *Create New Token* (downloads `kaggle.json`) | yes |
| `HF_TOKEN` | huggingface.co/settings/tokens (*write* role) | only for gated models / pushing |
| `HF_MODEL_REPO` | e.g. `your_name/qwen2.5-7b-qlora-finetuned` | only if `push_to_hub: true` |
| `WANDB_API_KEY` | wandb.ai (experiment tracking) | optional |

`setup.sh` converts `.env` into `~/.kaggle/kaggle.json` (chmod 600) automatically.

### 2. Setup + validate (no GPU needed)

```bash
./setup.sh                     # creates .venv, installs requirements, wires Kaggle creds
python src/prepare_data.py --input data/raw --output data/processed
python src/train.py --dry-run  # validates config + dataset without downloading the model
```

### 3. Add your custom training set

Put one or more `.jsonl` / `.json` / `.csv` files in `data/raw/` (replacing or next to
`sample_data.jsonl`). These formats are auto-detected per record:

```jsonc
// Alpaca
{"instruction": "...", "input": "...", "output": "..."}
// Prompt / response
{"prompt": "...", "response": "..."}          // also question/answer, query/completion
// ShareGPT
{"conversations": [{"from": "human", "value": "..."}, {"from": "gpt", "value": "..."}]}
// OpenAI chat
{"messages": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
```
CSV works with the same column names. Re-run `prepare_data.py` after changing data.

### 4. Train

```bash
./run_local.sh                 # full run - needs an NVIDIA GPU locally
./run_local.sh --smoke         # 10-step wiring test
./run_local.sh --dry-run       # config/data validation only
```

**No local GPU? Train on Kaggle (recommended):**

```bash
./scripts/push_dataset.sh "My Custom Training Set" my-custom-training-set   # upload data
./scripts/push_kernel.sh --run                                              # push + run GPU kernel
./scripts/pull_results.sh                                                   # fetch outputs/adapter
```
Both push scripts accept `--stage-only` to build the upload bundle under `.build/`
locally without credentials (handy to preview exactly what gets uploaded).
Or open `notebook/kaggle_7b_finetune.ipynb` on kaggle.com manually (attach your dataset
as *Add data*, enable GPU, Run all). After training, chat with the result:

```bash
python src/inference.py --interactive --adapter outputs/adapter
```

## Key settings (`config.yaml`)

| Setting | Default | Notes |
|---|---|---|
| `model_name` | `Qwen/Qwen2.5-7B-Instruct` | any HF id / local path |
| `use_4bit` | `true` | QLoRA — required for 16 GB GPUs |
| `lora_r` / `lora_alpha` | 16 / 32 | rank / scaling; raise for more capacity |
| `max_seq_length` | 1024 | lower (512) if VRAM is tight |
| `per_device_train_batch_size` × `gradient_accumulation_steps` | 2 × 4 | effective batch 8/GPU |
| `num_train_epochs` | 3 | or set `max_steps` for step-based runs |
| `merge_and_save` | `false` | `true` also writes standalone fp16 weights (~14 GB) |
| `push_to_hub` | `false` | pushes adapter to `HF_MODEL_REPO` |

Precedence: **CLI args > `.env` > `config.yaml`**. Auto-resume from `outputs/checkpoint-*`
is on — delete `outputs/` for a fresh start.

## Troubleshooting

- **CUDA out of memory** → lower `max_seq_length` (512) or batch size (1), keep `use_4bit: true`.
- **`no CUDA GPU detected`** → local run without GPU: use `--dry-run`, or train on Kaggle.
- **Gated model 401/403** → accept the license on HF and set a valid `HF_TOKEN`.
- **Kernel can't find project files** → push via `scripts/push_kernel.sh` (bundles `src/`, config, data).
- **Old checkpoint resumes unexpectedly** → `rm -rf outputs/`.

> ⚠️ `.env` contains real secrets: it is chmod 600 and git-ignored — never commit or share it.
