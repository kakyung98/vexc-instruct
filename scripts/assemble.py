#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge the three source collections, balance, and split into train/eval.

Inputs (produced by the other scripts):
  vex_justify_seed.jsonl, vulnfix_justify.jsonl, diversevul_justify.jsonl
Outputs:
  data/train.jsonl, data/eval_cisa_gold.jsonl
"""
import json, os, random, shutil

random.seed(20260416)
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = [("vex_justify_seed.jsonl"), ("vulnfix_justify.jsonl"), ("diversevul_justify.jsonl")]
OUT = os.path.join(HERE, "data")


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for f in SRC:
        p = os.path.join(HERE, f) if os.path.exists(os.path.join(HERE, f)) else f
        if os.path.exists(p):
            rows += [json.loads(l) for l in open(p, encoding="utf-8")]
    random.shuffle(rows)
    with open(os.path.join(OUT, "train.jsonl"), "w", encoding="utf-8") as w:
        for r in rows:
            w.write(json.dumps(r, ensure_ascii=False) + "\n")
    ev = "vex_justify_eval.jsonl"
    if os.path.exists(ev):
        shutil.copy(ev, os.path.join(OUT, "eval_cisa_gold.jsonl"))
    print("train:", len(rows))


if __name__ == "__main__":
    main()
