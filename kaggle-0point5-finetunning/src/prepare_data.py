#!/usr/bin/env python3
"""
prepare_data.py - turn a custom training set into chat-format train/val JSONL.

Works with the Python standard library only (no pandas/torch needed), so it
runs on this machine, on Kaggle, anywhere.

Supported input formats (auto-detected per record):
  * Alpaca        {"instruction": ..., "input": ..., "output": ...}
  * Prompt/resp   {"prompt"|"question"|"query": ..., "response"|"answer"|"completion": ...}
  * ShareGPT      {"conversations": [{"from": "human", "value": ...}, {"from": "gpt", ...}]}
  * Ready-made    {"messages": [{"role": "user", "content": ...}, {"role": "assistant", ...}]}
  * CSV with one of the header sets above

Usage:
  python src/prepare_data.py --input data/raw --output data/processed
  python src/prepare_data.py --input data/my_set.jsonl --val-split 0.1
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import random
import sys

PROMPT_KEYS = ("prompt", "question", "query", "input_text")
RESPONSE_KEYS = ("response", "answer", "completion", "output_text", "reply")
HUMAN_ALIASES = {"human", "user", "prompt"}
GPT_ALIASES = {"gpt", "assistant", "ai", "bot", "model"}


def _find(record: dict, keys) -> str | None:
    for k in keys:
        v = record.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def _conversation_to_messages(convs: list) -> list | None:
    """ShareGPT-style list -> openai-style messages."""
    messages = []
    for turn in convs:
        if not isinstance(turn, dict):
            return None
        speaker = str(turn.get("from", turn.get("role", ""))).lower()
        content = turn.get("value", turn.get("content", ""))
        if not isinstance(content, str) or not content.strip():
            continue
        if speaker in HUMAN_ALIASES:
            role = "user"
        elif speaker in GPT_ALIASES:
            role = "assistant"
        elif speaker == "system":
            role = "system"
        else:
            return None
        if messages and messages[-1]["role"] == role:
            messages[-1]["content"] += "\n" + content.strip()
        else:
            messages.append({"role": role, "content": content.strip()})
    return messages or None


def record_to_messages(record: dict) -> list | None:
    """Convert one raw record to openai-style messages, or None if invalid."""
    if not isinstance(record, dict):
        return None

    # 1) Already in chat format
    msgs = record.get("messages")
    if isinstance(msgs, list) and msgs:
        clean = [
            {"role": m["role"], "content": str(m["content"]).strip()}
            for m in msgs
            if isinstance(m, dict) and m.get("role") and str(m.get("content", "")).strip()
        ]
        if clean and any(m["role"] == "assistant" for m in clean):
            return clean

    # 2) ShareGPT conversations
    if isinstance(record.get("conversations"), list):
        conv = _conversation_to_messages(record["conversations"])
        if conv and any(m["role"] == "assistant" for m in conv):
            return conv

    # 3) Alpaca: instruction (+ optional input) -> output
    instruction = _find(record, ("instruction",))
    output = _find(record, ("output", "response", "answer", "completion"))
    if instruction and output:
        user_content = instruction
        extra = record.get("input")
        if isinstance(extra, str) and extra.strip():
            user_content = f"{instruction}\n\n{extra.strip()}"
        messages = []
        if isinstance(record.get("system"), str) and record["system"].strip():
            messages.append({"role": "system", "content": record["system"].strip()})
        messages.append({"role": "user", "content": user_content})
        messages.append({"role": "assistant", "content": output})
        return messages

    # 4) Generic prompt/response pairs
    prompt = _find(record, PROMPT_KEYS)
    response = _find(record, RESPONSE_KEYS)
    if prompt and response:
        messages = []
        if isinstance(record.get("system"), str) and record["system"].strip():
            messages.append({"role": "system", "content": record["system"].strip()})
        messages.append({"role": "user", "content": prompt})
        messages.append({"role": "assistant", "content": response})
        return messages

    return None


def read_records(path: str) -> list[dict]:
    ext = os.path.splitext(path)[1].lower()
    records: list[dict] = []
    if ext == ".csv":
        with open(path, newline="", encoding="utf-8-sig") as fh:
            records = [row for row in csv.DictReader(fh)]
    elif ext == ".json":
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict):  # {"data": [...]} style
            for key in ("data", "train", "examples", "records"):
                if isinstance(data.get(key), list):
                    data = data[key]
                    break
            else:
                data = [data]
        records = data if isinstance(data, list) else [data]
    elif ext in (".jsonl", ".ndjson"):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    print(f"  [warn] skipping malformed JSON line in {path}")
    else:
        print(f"  [warn] unsupported file type skipped: {path}")
    return records


def collect_inputs(input_path: str) -> list[str]:
    if os.path.isdir(input_path):
        files = []
        for pattern in ("*.jsonl", "*.ndjson", "*.json", "*.csv"):
            files.extend(sorted(glob.glob(os.path.join(input_path, "**", pattern), recursive=True)))
        return files
    return [input_path]


def write_jsonl(path: str, rows: list[dict]) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Prepare a custom training set for chat fine-tuning.")
    parser.add_argument("--input", default="data/raw", help="File or folder with raw data (jsonl/json/csv)")
    parser.add_argument("--output", default="data/processed", help="Output folder for train.jsonl / val.jsonl")
    parser.add_argument("--val-split", type=float, default=0.05, help="Validation fraction (0 disables the split)")
    parser.add_argument("--seed", type=int, default=42, help="Shuffle seed")
    parser.add_argument("--min-response-chars", type=int, default=3, help="Drop assistant replies shorter than this")
    args = parser.parse_args(argv)

    files = collect_inputs(args.input)
    if not files:
        print(f"[error] no supported data files found under: {args.input}")
        return 1

    print(f"[prepare] found {len(files)} file(s):")
    all_rows: list[dict] = []
    total_raw = 0
    for path in files:
        records = read_records(path)
        total_raw += len(records)
        kept = 0
        for rec in records:
            messages = record_to_messages(rec)
            if not messages:
                continue
            assistant_len = sum(len(m["content"]) for m in messages if m["role"] == "assistant")
            if assistant_len < args.min_response_chars:
                continue
            all_rows.append({"messages": messages})
            kept += 1
        print(f"  - {os.path.basename(path)}: {len(records)} records -> {kept} usable")

    if not all_rows:
        print("[error] no usable examples after conversion. Check the input format (see module docstring).")
        return 1

    rng = random.Random(args.seed)
    rng.shuffle(all_rows)

    val_n = int(len(all_rows) * args.val_split)
    if args.val_split <= 0 or len(all_rows) < 10:
        val_n = 0
    val_rows = all_rows[:val_n]
    train_rows = all_rows[val_n:]

    train_path = os.path.join(args.output, "train.jsonl")
    val_path = os.path.join(args.output, "val.jsonl")
    write_jsonl(train_path, train_rows)
    if val_rows:
        write_jsonl(val_path, val_rows)
    elif os.path.exists(val_path):
        os.remove(val_path)

    print(f"[prepare] raw records: {total_raw} | usable: {len(all_rows)}")
    print(f"[prepare] train: {len(train_rows)} -> {train_path}")
    print(f"[prepare] val:   {len(val_rows)} -> {val_path if val_rows else '(none)'}")
    if train_rows:
        sample = train_rows[0]["messages"]
        print("[prepare] sample conversation roles:", [m["role"] for m in sample])
    return 0


if __name__ == "__main__":
    sys.exit(main())

