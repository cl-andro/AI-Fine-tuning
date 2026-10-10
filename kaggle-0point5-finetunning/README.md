# Kaggle 0.5B QLoRA Fine-tune on SQL Training Set

Fine-tune **Qwen/Qwen2.5-0.5B-Instruct** on a custom SQL training set (2500 examples) using QLoRA (4-bit base weights + LoRA adapters). Designed to run on a single Kaggle T4/P100 16 GB GPU.

## Project Structure

```
kaggle-0point5-finetunning/
├── config.yaml              # Training configuration (model, LoRA, hyperparams)
├── requirements.txt         # Python dependencies
├── setup.sh                 # Local environment setup
├── run_local.sh             # Run training locally
├── .env.example             # Environment variable template
├── .gitignore
├── src/
│   ├── prepare_data.py      # Convert raw data to chat-format JSONL
│   ├── train.py             # QLoRA training script
│   └── inference.py         # Inference/chat script
├── notebook/
│   ├── kaggle_0point5_finetune.ipynb  # Kaggle notebook
│   └── kernel-metadata.json            # Kaggle kernel metadata
├── scripts/
│   ├── push_kernel.sh       # Push kernel to Kaggle
│   ├── push_dataset.sh      # Upload dataset to Kaggle
│   └── pull_results.sh      # Download kernel output artifacts
└── data/
    ├── raw/                 # Raw training data (place your JSON/JSONL here)
    └── processed/           # Prepared train/val JSONL (auto-generated)
```

## Quick Start

### Option 1: Run on Kaggle

1. **Upload your dataset** to Kaggle:
   ```bash
   ./scripts/push_dataset.sh "SQL Training Set" sql-training-set
   ```

2. **Push the kernel**:
   ```bash
   ./scripts/push_kernel.sh
   ```

3. **Run on Kaggle**: Open the kernel, attach your dataset, enable GPU, and run all cells.

### Option 2: Run Locally

1. **Setup environment**:
   ```bash
   ./setup.sh
   ```

2. **Place your data** in `data/raw/` (Alpaca format: `[{"instruction": "...", "output": "..."}]`)

3. **Validate config**:
   ```bash
   ./run_local.sh --dry-run
   ```

4. **Train**:
   ```bash
   ./run_local.sh
   ```

5. **Smoke test** (100 steps):
   ```bash
   ./run_local.sh --steps 100
   ```

## Configuration

Edit `config.yaml` to adjust:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `model_name` | `Qwen/Qwen2.5-0.5B-Instruct` | Base model |
| `lora_r` | 16 | LoRA rank |
| `lora_alpha` | 32 | LoRA alpha |
| `num_train_epochs` | 3 | Training epochs |
| `learning_rate` | 2e-4 | Learning rate |
| `per_device_train_batch_size` | 4 | Batch size per device |
| `max_seq_length` | 1024 | Max sequence length |
| `merge_and_save` | true | Merge LoRA into base weights after training |

## Data Format

The training data should be in **Alpaca format** (JSON or JSONL):

```json
[
  {
    "instruction": "Schema: employees(id, name, salary)\nGet all employees",
    "output": "SELECT * FROM employees;"
  }
]
```

Supported formats: Alpaca, ShareGPT, prompt/response pairs, and chat messages.

## Environment Variables

Create a `.env` file from `.env.example`:

```bash
KAGGLE_USERNAME=your_username
KAGGLE_KEY=your_key
HF_TOKEN=hf_xxx                    # optional, for pushing to HF
HF_MODEL_REPO=your_user/model-name # optional
WANDB_API_KEY=                     # optional, for W&B tracking
MAX_STEPS=100                      # optional, for smoke tests
```

## Output

After training, the `outputs/` directory contains:

- `adapter/` - LoRA adapter weights + tokenizer
- `merged/` - Merged 16-bit model (if `merge_and_save: true`)
- `train_results.json` - Training metrics
- `eval_results.json` - Evaluation metrics
- `run_config.json` - Full config snapshot
- `checkpoint-*` - Intermediate checkpoints

## Links

- [QLoRA Paper](https://arxiv.org/abs/2305.14314)
- [Qwen2.5 Models](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct)
- [PEFT Documentation](https://huggingface.co/docs/peft)
- [TRL Documentation](https://huggingface.co/docs/trl)