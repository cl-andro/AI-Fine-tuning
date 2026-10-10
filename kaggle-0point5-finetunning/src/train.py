#!/usr/bin/env python3
"""
train.py - QLoRA fine-tune of a 7B (or any) causal LM on a custom chat dataset.

Designed to run on Kaggle (T4/P100/L4 GPU) or any Linux GPU box.

    python src/train.py --config config.yaml            # full training
    python src/train.py --config config.yaml --dry-run  # validate config+data only

Precedence for settings:  CLI args  >  .env / environment  >  config.yaml
"""
from __future__ import annotations

import argparse
import glob
import inspect
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Environment variables that may override config.yaml values
ENV_OVERRIDES = {
    "MODEL_NAME": "model_name",
    "TRAIN_DATASET_PATH": "train_dataset_path",
    "OUTPUT_DIR": "output_dir",
}


def load_env_file() -> None:
    """Load .env if python-dotenv is available (never overrides real env vars)."""
    try:
        from dotenv import load_dotenv
        load_dotenv(REPO_ROOT / ".env")
    except ImportError:
        pass


def load_config(path: str) -> dict:
    try:
        import yaml
    except ImportError:
        print("[error] pyyaml is not installed - run ./setup.sh (or: pip install pyyaml)")
        raise SystemExit(1)
    with open(path, "r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh) or {}
    for env_key, cfg_key in ENV_OVERRIDES.items():
        val = os.environ.get(env_key)
        if val:
            cfg[cfg_key] = val
    return cfg


def resolve_data_files(processed_dir: str) -> dict:
    train_path = os.path.join(processed_dir, "train.jsonl")
    val_path = os.path.join(processed_dir, "val.jsonl")
    files = {}
    if os.path.isfile(train_path):
        files["train"] = train_path
    if os.path.isfile(val_path):
        files["val"] = val_path
    return files


def count_jsonl(path: str) -> int:
    n = 0
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                n += 1
    return n


def dry_run(cfg: dict) -> int:
    """Validate configuration + prepared dataset WITHOUT importing torch."""
    print("=" * 70)
    print("DRY RUN - configuration and dataset validation (no model download)")
    print("=" * 70)
    ok = True

    print(f"model_name           : {cfg.get('model_name')}")
    print(f"train_dataset_path   : {cfg.get('train_dataset_path')}")
    print(f"processed_dir        : {cfg.get('processed_dir')}")
    print(f"max_seq_length       : {cfg.get('max_seq_length')}")
    print(f"lora_r / alpha       : {cfg.get('lora_r')} / {cfg.get('lora_alpha')}")
    print(f"epochs / batch / grad: {cfg.get('num_train_epochs')} / "
          f"{cfg.get('per_device_train_batch_size')} x {cfg.get('gradient_accumulation_steps')}")
    print(f"learning_rate        : {cfg.get('learning_rate')}")
    print(f"use_4bit (QLoRA)     : {cfg.get('use_4bit')}")

    raw = cfg.get("train_dataset_path")
    if raw:
        if os.path.isdir(raw):
            entries = sorted(glob.glob(os.path.join(raw, "*")))
            print(f"raw dataset folder   : {raw} ({len(entries)} file(s))")
            for e in entries[:10]:
                print(f"    - {os.path.basename(e)}")
        elif os.path.isfile(raw):
            print(f"raw dataset file     : {raw}")
        else:
            print(f"[error] train_dataset_path not found: {raw}")
            ok = False

    files = resolve_data_files(cfg.get("processed_dir", "data/processed"))
    if "train" not in files:
        print(f"[error] {cfg.get('processed_dir')}/train.jsonl missing - run src/prepare_data.py first")
        ok = False
    else:
        n_train = count_jsonl(files["train"])
        n_val = count_jsonl(files["val"]) if "val" in files else 0
        print(f"prepared train/val   : {n_train} / {n_val} examples")
        if n_train == 0:
            print("[error] train.jsonl is empty")
            ok = False
        with open(files["train"], "r", encoding="utf-8") as fh:
            first = json.loads(fh.readline())
        roles = [m.get("role") for m in first.get("messages", [])]
        print(f"first example roles  : {roles}")
        if "assistant" not in roles:
            print("[error] first example has no assistant turn")
            ok = False

    print("-" * 70)
    print("RESULT:", "OK - ready for training" if ok else "FAILED - fix the errors above")
    return 0 if ok else 1


def manual_chat_template(messages: list[dict], add_generation_prompt: bool = False) -> str:
    """Fallback template when the tokenizer has no chat template."""
    parts = []
    for m in messages:
        if m["role"] == "system":
            parts.append(f"### System:\n{m['content']}")
        elif m["role"] == "user":
            parts.append(f"### Instruction:\n{m['content']}")
        elif m["role"] == "assistant":
            parts.append(f"### Response:\n{m['content']}")
    text = "\n\n".join(parts)
    if add_generation_prompt:
        text += "\n\n### Response:\n"
    return text


def find_lora_targets(model, train_lm_head: bool = False) -> list[str]:
    """Auto-detect linear layer names to wrap with LoRA (works for Qwen/Llama/Mistral/Phi)."""
    import torch
    leaves: set[str] = set()
    for name, module in model.named_modules():
        if isinstance(module, torch.nn.Linear):
            leaves.add(name.split(".")[-1])
    preferred = [
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
        "query_key_value", "dense", "dense_h_to_4h", "dense_4h_to_h",
        "fc1", "fc2",
    ]
    targets = [m for m in preferred if m in leaves]
    if not targets:
        targets = sorted(leaves)
    if not train_lm_head:
        targets = [t for t in targets if t != "lm_head"]
    return targets


def build_training(cfg: dict) -> int:
    # ---- Heavy imports (kept out of --dry-run) ------------------------
    try:
        import torch
        from datasets import load_dataset
        from transformers import (
            AutoModelForCausalLM,
            AutoTokenizer,
            BitsAndBytesConfig,
            TrainingArguments,
        )
        from peft import LoraConfig, PeftModel, prepare_model_for_kbit_training
        from trl import SFTTrainer
        try:
            from trl import SFTConfig
        except ImportError:
            SFTConfig = None
    except ImportError as _exc:
        print(f"[error] missing training dependency: {_exc}")
        print("        run ./setup.sh   (or: pip install -r requirements.txt)")
        print("        tip: 'python src/train.py --dry-run' works without the GPU stack")
        return 1


    # ---- Hardware sanity check ---------------------------------------
    if not torch.cuda.is_available():
        print("[error] no CUDA GPU detected. On Kaggle: Runtime -> Change runtime type -> GPU.")
        print("        Locally: run 'python src/train.py --dry-run' to validate without a GPU.")
        return 1
    gpu = torch.cuda.get_device_name(0)
    print(f"[train] GPU: {gpu} | VRAM: {torch.cuda.get_device_properties(0).total_mem / 1e9:.1f} GB")

    use_bf16 = torch.cuda.is_bf16_supported()
    if cfg.get("bf16") is True:
        use_bf16 = True
    elif cfg.get("bf16") is False:
        use_bf16 = False
    use_fp16 = (not use_bf16)
    if cfg.get("fp16") is True:
        use_fp16, use_bf16 = True, False
    compute_dtype = torch.bfloat16 if use_bf16 else torch.float16
    print(f"[train] compute dtype: {'bfloat16' if use_bf16 else 'float16'}")

    # ---- Tokenizer / base model --------------------------------------
    model_name = cfg["model_name"]
    hf_token = os.environ.get("HF_TOKEN") or None
    if hf_token in ("hf_replace_me", ""):
        hf_token = None
    print(f"[train] loading base model: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(
        model_name, revision=cfg.get("model_revision", "main"),
        token=hf_token, trust_remote_code=True, use_fast=True,
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    bnb_config = None
    if cfg.get("use_4bit", True):
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type=cfg.get("bnb_4bit_quant_type", "nf4"),
            bnb_4bit_use_double_quant=cfg.get("bnb_4bit_use_double_quant", True),
            bnb_4bit_compute_dtype=compute_dtype,
        )

    model = AutoModelForCausalLM.from_pretrained(
        model_name, revision=cfg.get("model_revision", "main"),
        token=hf_token, trust_remote_code=True,
        quantization_config=bnb_config,
        device_map="auto",
        attn_implementation="sdpa",
    )
    model.config.use_cache = False
    model.config.pad_token_id = tokenizer.pad_token_id
    if hasattr(model, "enable_input_require_grads"):
        model.enable_input_require_grads()

    resume_adapter = cfg.get("resume_adapter_path")
    if resume_adapter:
        print(f"[train] stacking existing adapter: {resume_adapter}")
        model = PeftModel.from_pretrained(model, resume_adapter, is_trainable=True)
    elif bnb_config is not None:
        model = prepare_model_for_kbit_training(
            model, use_gradient_checkpointing=bool(cfg.get("gradient_checkpointing", True))
        )

    # ---- Dataset ------------------------------------------------------
    data_files = resolve_data_files(cfg.get("processed_dir", "data/processed"))
    if "train" not in data_files:
        print("[error] processed train.jsonl missing - run src/prepare_data.py first")
        return 1
    all_files = {"train": data_files["train"]}
    if "val" in data_files:
        all_files["validation"] = data_files["val"]
    raw_ds = load_dataset("json", data_files=all_files)
    default_system = cfg.get("system_prompt") or ""

    def render(example):
        messages = example["messages"]
        if default_system and not any(m["role"] == "system" for m in messages):
            messages = [{"role": "system", "content": default_system}] + list(messages)
        if getattr(tokenizer, "chat_template", None):
            text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
        else:
            text = manual_chat_template(messages)
        if tokenizer.eos_token and not text.endswith(tokenizer.eos_token):
            text += tokenizer.eos_token
        return {"text": text}

    drop_cols = list(raw_ds["train"].column_names)  # keep only the rendered "text"
    ds = raw_ds.map(render, remove_columns=drop_cols, desc="rendering chat template")
    train_ds = ds["train"]
    eval_ds = ds.get("validation")
    print(f"[train] examples: train={len(train_ds)}" + (f" eval={len(eval_ds)}" if eval_ds else ""))
    print("[train] sample rendered text: " +
          repr(train_ds[0]["text"][:400]))

    # ---- LoRA ---------------------------------------------------------
    targets = cfg.get("lora_target_modules") or find_lora_targets(
        model, train_lm_head=bool(cfg.get("train_lm_head", False))
    )
    print(f"[train] LoRA target modules: {targets}")
    lora_config = LoraConfig(
        r=int(cfg.get("lora_r", 16)),
        lora_alpha=int(cfg.get("lora_alpha", 32)),
        lora_dropout=float(cfg.get("lora_dropout", 0.05)),
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=targets,
    )

    # ---- Training arguments (defensive across transformers/TRL versions) ----
    output_dir = cfg.get("output_dir", "outputs")
    os.makedirs(output_dir, exist_ok=True)

    report_to = cfg.get("report_to", "auto")
    if report_to == "auto":
        report_to = ["wandb"] if os.environ.get("WANDB_API_KEY") else "none"

    ta_params = inspect.signature(TrainingArguments.__init__).parameters
    eval_key = "eval_strategy" if "eval_strategy" in ta_params else "evaluation_strategy"

    hp = dict(
        output_dir=output_dir,
        num_train_epochs=float(cfg.get("num_train_epochs", 3)),
        max_steps=int(cfg.get("max_steps", -1)),
        per_device_train_batch_size=int(cfg.get("per_device_train_batch_size", 2)),
        per_device_eval_batch_size=int(cfg.get("per_device_eval_batch_size", 2)),
        gradient_accumulation_steps=int(cfg.get("gradient_accumulation_steps", 4)),
        learning_rate=float(cfg.get("learning_rate", 2e-4)),
        lr_scheduler_type=cfg.get("lr_scheduler_type", "cosine"),
        warmup_ratio=float(cfg.get("warmup_ratio", 0.03)),
        weight_decay=float(cfg.get("weight_decay", 0.001)),
        logging_steps=int(cfg.get("logging_steps", 5)),
        save_total_limit=int(cfg.get("save_total_limit", 2)),
        seed=int(cfg.get("seed", 42)),
        bf16=use_bf16,
        fp16=bool(use_fp16 and not use_bf16),
        gradient_checkpointing=bool(cfg.get("gradient_checkpointing", True)),
        report_to=report_to,
        load_best_model_at_end=False,
        remove_unused_columns=False,
        dataloader_pin_memory=False,
    )
    strategy = cfg.get("eval_strategy", "epoch")
    hp[eval_key] = strategy if (eval_ds is not None and strategy != "no") else "no"
    hp["save_strategy"] = cfg.get("save_strategy", "epoch")

    trainer_kwargs = dict(
        model=model,
        train_dataset=train_ds,
        eval_dataset=eval_ds,
        peft_config=None if resume_adapter else lora_config,
    )

    if SFTConfig is not None:
        sc_params = inspect.signature(SFTConfig.__init__).parameters
        if "dataset_text_field" in sc_params:
            hp["dataset_text_field"] = "text"
        for max_key in ("max_length", "max_seq_length"):
            if max_key in sc_params:
                hp[max_key] = int(cfg.get("max_seq_length", 1024))
                break
        if "packing" in sc_params:
            hp["packing"] = False
        hp = {k: v for k, v in hp.items() if k in sc_params}
        trainer_kwargs["args"] = SFTConfig(**hp)
    else:
        trainer_kwargs["args"] = TrainingArguments(**hp)

    # tokenizer / processing_class argument was renamed in newer TRL
    tr_params = inspect.signature(SFTTrainer.__init__).parameters
    if "processing_class" in tr_params:
        trainer_kwargs["processing_class"] = tokenizer
    elif "tokenizer" in tr_params:
        trainer_kwargs["tokenizer"] = tokenizer
    if SFTConfig is None:
        if "dataset_text_field" in tr_params:
            trainer_kwargs["dataset_text_field"] = "text"
        else:
            raise RuntimeError("Installed trl is too old/new for dataset_text_field; use trl>=0.12")
        for max_key in ("max_seq_length", "max_length"):
            if max_key in tr_params:
                trainer_kwargs[max_key] = int(cfg.get("max_seq_length", 1024))
                break

    trainer = SFTTrainer(**trainer_kwargs)
    # ---- Auto-resume from latest checkpoint --------------------------
    resume_ckpt = None
    if cfg.get("resume_from_checkpoint", True):
        ckpts = glob.glob(os.path.join(output_dir, "checkpoint-*"))
        if ckpts:
            resume_ckpt = max(ckpts, key=lambda p: int(p.rsplit("-", 1)[-1]))
            print(f"[train] resuming from checkpoint: {resume_ckpt}")

    # ---- Train -------------------------------------------------------
    print("[train] starting training ...")
    train_result = trainer.train(resume_from_checkpoint=resume_ckpt)
    metrics = dict(train_result.metrics)
    trainer.log_metrics("train", metrics)
    trainer.save_metrics("train", metrics)
    trainer.save_state()

    if eval_ds is not None:
        try:
            eval_metrics = trainer.evaluate()
            trainer.log_metrics("eval", eval_metrics)
            trainer.save_metrics("eval", eval_metrics)
        except Exception as exc:  # eval must never kill a finished run
            print(f"[warn] evaluation failed: {exc}")

    # ---- Save adapter + config snapshot ------------------------------
    adapter_dir = os.path.join(output_dir, "adapter")
    trainer.save_model(adapter_dir)
    tokenizer.save_pretrained(adapter_dir)
    with open(os.path.join(output_dir, "run_config.json"), "w", encoding="utf-8") as fh:
        json.dump(cfg, fh, indent=2, default=str)
    print(f"[train] adapter saved to: {adapter_dir}")
    print(f"[train] metrics: {json.dumps(metrics, indent=2, default=str)}")

    # ---- Optional: push adapter to Hugging Face ----------------------
    push = str(cfg.get("push_to_hub", False)).lower() == "true"
    repo = os.environ.get("HF_MODEL_REPO")
    if push and repo and hf_token and "your_hf_username" not in repo:
        try:
            trainer.model.push_to_hub(repo, token=hf_token)
            tokenizer.push_to_hub(repo, token=hf_token)
            print(f"[train] pushed adapter to https://huggingface.co/{repo}")
        except Exception as exc:
            print(f"[warn] HF push failed: {exc}")
    elif push:
        print("[warn] push_to_hub enabled but HF_TOKEN / HF_MODEL_REPO not set in .env")

    # ---- Optional: merge LoRA into standalone 16-bit weights ---------
    if str(cfg.get("merge_and_save", False)).lower() == "true":
        try:
            print("[train] merging adapter into fp16 weights (needs ~16GB RAM) ...")
            merged_base = AutoModelForCausalLM.from_pretrained(
                model_name, revision=cfg.get("model_revision", "main"),
                token=hf_token, trust_remote_code=True, torch_dtype=torch.float16,
            )
            merged = PeftModel.from_pretrained(merged_base, adapter_dir)
            merged = merged.merge_and_unload()
            merged_dir = os.path.join(output_dir, "merged")
            merged.save_pretrained(merged_dir, safe_serialization=True)
            tokenizer.save_pretrained(merged_dir)
            print(f"[train] merged model saved to: {merged_dir}")
        except Exception as exc:
            print(f"[warn] merge failed (adapter in {adapter_dir} is still valid): {exc}")

    print("[train] DONE")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="QLoRA fine-tune a causal LM on a custom chat dataset.")
    parser.add_argument("--config", default=None, help="Path to config.yaml (default: <repo>/config.yaml)")
    parser.add_argument("--model", default=None, help="Override base model id/path")
    parser.add_argument("--max-steps", type=int, default=None, help="Override max_steps (smoke tests)")
    parser.add_argument("--output-dir", default=None, help="Override output_dir")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate config + dataset only (no GPU / no model download)")
    args = parser.parse_args(argv)

    load_env_file()

    cfg_path = args.config
    if cfg_path is None:
        cfg_path = str(REPO_ROOT / "config.yaml")
    elif not os.path.isfile(cfg_path) and os.path.isfile(REPO_ROOT / cfg_path):
        cfg_path = str(REPO_ROOT / cfg_path)
    if not os.path.isfile(cfg_path):
        print(f"[error] config not found: {cfg_path}")
        return 1
    cfg_path = os.path.abspath(cfg_path)

    # Repo-relative paths (data/processed, outputs) resolve no matter where we're called from
    os.chdir(REPO_ROOT)

    cfg = load_config(cfg_path)
    if args.model:
        cfg["model_name"] = args.model
    if args.max_steps is not None:
        cfg["max_steps"] = args.max_steps
    if args.output_dir:
        cfg["output_dir"] = args.output_dir

    if args.dry_run:
        return dry_run(cfg)
    return build_training(cfg)


if __name__ == "__main__":
    sys.exit(main())




