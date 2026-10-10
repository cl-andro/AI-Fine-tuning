> **© 2026 [CL-Andro](https://github.com/cl-andro) / Mohammad Zaid — All Rights Reserved.**
>
> All source code, training datasets, documentation, and associated materials in this
> repository are the exclusive intellectual property of CL-Andro / Mohammad Zaid.
> Unauthorized copying, modification, redistribution, or commercial use — in whole or
> in part — without prior written consent is strictly prohibited.

---

# Kaggle LLM Fine-tuning Lab

Monorepo for QLoRA fine-tuning experiments on Kaggle free GPUs, plus the custom
training sets they consume.

## What's inside

| Folder | Description |
|---|---|
| [`kaggle-0point5-finetunning/`](./kaggle-0point5-finetunning) | QLoRA fine-tune of **Qwen2.5-0.5B-Instruct** on a SQL training set (2,500 examples). Single T4/P100 16 GB GPU. |
| [`kaggle-7b-modle-finetunning/`](./kaggle-7b-modle-finetunning) | QLoRA fine-tune of **Qwen2.5-7B-Instruct** (swappable for Mistral/Llama-3.1/Phi-3.5) on any custom dataset. Kaggle GPU kernel included. |
| [`sql-training-set/`](./sql-training-set) | Custom SQL training set (Alpaca-style instruction → SQL), split into 10 parts. |
| [`terminal-training-set/`](./terminal-training-set) | Terminal / Linux-ops training set with reasoning traces (systemd, nginx, Docker, AWS CLI, security, etc.), 21 parts + batch files. |
| [`terminal-training-set-nothinking/`](./terminal-training-set-nothinking) | Same terminal corpus without thinking traces (direct answers only). |
| [`python-debugging-training-set/`](./python-debugging-training-set) | Python debugging / error-fixing set (Alpaca-style), 12 parts · 243 entries. |
| [`function-calling-training-set/`](./function-calling-training-set) | Tool / function-calling examples for chat models, 12 parts · 240 entries. |
| [`dockerfile-generation-training-set/`](./dockerfile-generation-training-set) | Dockerfile generation from natural-language specs, 12 parts · 243 entries. |
| [`regex-training-set/`](./regex-training-set) | Regular-expression writing (match, extract, validate), 12 parts · 239 entries. |
| [`kubernetes-helm-training-set/`](./kubernetes-helm-training-set) | Kubernetes manifests + Helm chart authoring, 12 parts · 264 entries. |
| [`multi-turn-debugging-training-set/`](./multi-turn-debugging-training-set) | Multi-turn debugging conversations (transcript → fix), 12 parts · 240 entries. |
| [`bash-scripting-training-set/`](./bash-scripting-training-set) | Bash scripting (quoting, traps, awk/sed, cron, real scripts), 12 parts · 240 entries. |
| [`pandas-data-wrangling-training-set/`](./pandas-data-wrangling-training-set) | pandas data wrangling (IO, cleaning, groupby, merge, reshape), 12 parts · 240 entries. |

## Quick start

Each fine-tuning project is self-contained — see its own README:

```bash
cd kaggle-7b-modle-finetunning     # or kaggle-0point5-finetunning
cp .env.example .env && nano .env  # add Kaggle / HF credentials
./setup.sh
./run_local.sh --dry-run           # validate config + data
./scripts/push_kernel.sh --run     # train on Kaggle free GPU
```

## Data format

Training sets feed the projects in Alpaca / ShareGPT / OpenAI-chat formats —
`src/prepare_data.py` auto-detects per record:

```json
{"instruction": "...", "input": "...", "output": "..."}
{"prompt": "...", "response": "..."}
{"messages": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
```

## Notes

- **Secrets never go in git**: `.env`, `kaggle.json`, `.kaggle/` are gitignored everywhere.
  Copy `.env.example` → `.env` and fill in your own Kaggle / Hugging Face tokens.
- Model weights, checkpoints (`outputs/`), and `*.safetensors` are gitignored —
  pull them from Kaggle or Hugging Face instead.
- The two fine-tuning projects both run on a single 16 GB Kaggle GPU via QLoRA
  (4-bit base + LoRA adapters).

## Stack

Python · Transformers · TRL · PEFT · bitsandbytes · QLoRA · Kaggle GPUs
