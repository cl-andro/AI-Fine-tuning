#!/usr/bin/env python3
"""
inference.py - chat with the fine-tuned model (base model + LoRA adapter).

Examples:
  python src/inference.py --prompt "Summarize the rules of chess in 3 bullet points."
  python src/inference.py --interactive
  python src/inference.py --adapter outputs/adapter --model Qwen/Qwen2.5-7B-Instruct
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

FALLBACK_TEMPLATE = (
    "### System:\n{system}\n\n### Instruction:\n{user}\n\n### Response:\n"
)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Run inference with the fine-tuned adapter.")
    parser.add_argument("--model", default=os.environ.get("MODEL_NAME", "Qwen/Qwen2.5-7B-Instruct"))
    parser.add_argument("--adapter", default="outputs/adapter", help="Adapter dir ('' = base model only)")
    parser.add_argument("--prompt", default=None, help="Single prompt; omit for --interactive")
    parser.add_argument("--interactive", action="store_true", help="Chat loop (type 'exit' to quit)")
    parser.add_argument("--system", default="You are a helpful, concise and accurate assistant.")
    parser.add_argument("--max-new-tokens", type=int, default=512)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--top-p", type=float, default=0.9)
    parser.add_argument("--load-in-4bit", action="store_true", default=True,
                        help="Load base model in 4-bit (default on, needed for 16GB GPUs)")
    parser.add_argument("--load-in-8bit", action="store_true", help="Use 8-bit instead of 4-bit")
    args = parser.parse_args(argv)

    try:
        from dotenv import load_dotenv
        load_dotenv(REPO_ROOT / ".env")
    except ImportError:
        pass

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    if not torch.cuda.is_available():
        print("[error] inference needs a CUDA GPU (Kaggle: enable GPU runtime)")
        return 1

    hf_token = os.environ.get("HF_TOKEN") or None
    if hf_token in ("hf_replace_me", ""):
        hf_token = None

    dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    quant = None
    if args.load_in_8bit:
        quant = BitsAndBytesConfig(load_in_8bit=True)
    elif args.load_in_4bit:
        quant = BitsAndBytesConfig(
            load_in_4bit=True, bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=dtype,
        )

    print(f"[infer] loading model: {args.model}")
    tokenizer = AutoTokenizer.from_pretrained(args.model, token=hf_token, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        args.model, token=hf_token, trust_remote_code=True,
        quantization_config=quant, device_map="auto", torch_dtype=dtype,
    )

    adapter = args.adapter.strip()
    if adapter and adapter not in ("", "none", "None"):
        adapter_path = adapter if os.path.isabs(adapter) else str(REPO_ROOT / adapter)
        if os.path.isdir(adapter_path):
            from peft import PeftModel
            print(f"[infer] loading adapter: {adapter_path}")
            model = PeftModel.from_pretrained(model, adapter_path)
        else:
            print(f"[warn] adapter not found at {adapter_path} - using base model only")
    model.eval()

    def generate(user_text: str) -> str:
        messages = [{"role": "system", "content": args.system},
                    {"role": "user", "content": user_text}]
        if getattr(tokenizer, "chat_template", None):
            prompt = tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True)
        else:
            prompt = FALLBACK_TEMPLATE.format(system=args.system, user=user_text)
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            out = model.generate(
                **inputs,
                max_new_tokens=args.max_new_tokens,
                do_sample=args.temperature > 0,
                temperature=max(args.temperature, 1e-5),
                top_p=args.top_p,
                pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id,
            )
        gen = out[0][inputs["input_ids"].shape[1]:]
        return tokenizer.decode(gen, skip_special_tokens=True).strip()

    if args.prompt:
        print(generate(args.prompt))
        return 0

    if args.interactive:
        print("[infer] interactive mode - type 'exit' to quit")
        while True:
            try:
                user = input("\nYou> ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if not user or user.lower() in {"exit", "quit"}:
                break
            print(f"\nAssistant> {generate(user)}")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
