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
| [`python-function-writing-training-set/`](./python-function-writing-training-set) | Python function writing from natural-language specs, 12 parts · 240 entries. |
| [`unit-test-generation-training-set/`](./unit-test-generation-training-set) | Unit test generation (pytest, fixtures, parametrize), 12 parts · 240 entries. |
| [`code-review-training-set/`](./code-review-training-set) | Code review with issues, severity and fixes, 12 parts · 240 entries. |
| [`refactoring-training-set/`](./refactoring-training-set) | Code refactoring (extract, simplify, modernize), 12 parts · 240 entries. |
| [`code-conversion-training-set/`](./code-conversion-training-set) | Code conversion between languages (Py↔JS↔SQL etc.), 12 parts · 240 entries. |
| [`javascript-typescript-training-set/`](./javascript-typescript-training-set) | JavaScript / TypeScript bugs, async and types, 12 parts · 240 entries. |
| [`html-css-tailwind-training-set/`](./html-css-tailwind-training-set) | HTML / CSS / Tailwind UI generation, 12 parts · 240 entries. |
| [`algorithms-data-structures-training-set/`](./algorithms-data-structures-training-set) | Algorithms & data structures (implement, trace, analyze), 12 parts · 240 entries. |
| [`github-actions-training-set/`](./github-actions-training-set) | GitHub Actions CI/CD workflow authoring, 12 parts · 240 entries. |
| [`terraform-training-set/`](./terraform-training-set) | Terraform infrastructure-as-code (resources, modules, state), 12 parts · 240 entries. |
| [`nginx-config-training-set/`](./nginx-config-training-set) | nginx server/proxy config and troubleshooting, 12 parts · 240 entries. |
| [`systemd-services-training-set/`](./systemd-services-training-set) | systemd units, timers and journal debugging, 12 parts · 240 entries. |
| [`prometheus-grafana-training-set/`](./prometheus-grafana-training-set) | Prometheus PromQL, exporters and Grafana dashboards, 12 parts · 240 entries. |
| [`log-parsing-training-set/`](./log-parsing-training-set) | Log parsing / extraction with awk, sed and regex, 12 parts · 240 entries. |
| [`json-schema-extraction-training-set/`](./json-schema-extraction-training-set) | JSON → schema inference and validation rules, 12 parts · 240 entries. |
| [`commit-message-generation-training-set/`](./commit-message-generation-training-set) | Conventional-commit message generation from diffs, 12 parts · 240 entries. |
| [`stacktrace-rootcause-training-set/`](./stacktrace-rootcause-training-set) | Stacktrace / error → root cause and fix, 12 parts · 240 entries. |
| [`instruction-following-training-set/`](./instruction-following-training-set) | Strict instruction-following (format, constraints), 12 parts · 240 entries. |
| [`pytorch-tensor-ops-training-set/`](./pytorch-tensor-ops-training-set) | PyTorch tensor ops, autograd and training loops, 12 parts · 240 entries. |
| [`sklearn-pipeline-training-set/`](./sklearn-pipeline-training-set) | scikit-learn pipelines, preprocessing and CV, 12 parts · 240 entries. |
| [`matplotlib-plot-code-training-set/`](./matplotlib-plot-code-training-set) | matplotlib plotting code from plot descriptions, 12 parts · 240 entries. |
| [`secure-code-audit-training-set/`](./secure-code-audit-training-set) | Security code audit (injection, XSS, SSRF, secrets, deps), 12 parts · 240 entries. |
| [`networking-diagnostics-training-set/`](./networking-diagnostics-training-set) | Networking diagnostics (DNS, TLS, routing, tcpdump), 12 parts · 240 entries. |
| [`technical-docs-training-set/`](./technical-docs-training-set) | Technical documentation (README, docstrings, ADRs), 12 parts · 240 entries. |
| [`text-classification-training-set/`](./text-classification-training-set) | Text classification labels and rules, 12 parts · 240 entries. |

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
