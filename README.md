# vexc-instruct

**An instruction-tuning dataset for teaching language models to make VEX
(Vulnerability Exploitability eXchange) judgments about C/C++ code.**

Given a function from a software component and a referenced weakness, the model
must decide whether the product is **affected** or **not_affected**, following
the four [CISA VEX status justification](https://www.cisa.gov/sites/default/files/publications/VEX_Status_Justification_Jun22.pdf)
questions, and emit a structured judgment.

This dataset reframes existing C/C++ vulnerability corpora (which are built for
vulnerability *detection*) into the *VEX-justification* task: not "write an
exploit," but "judge exploitability and name the justification."

---

## The task

Each example is an `instruction` → `completion` pair.

**Instruction** presents the CISA questions and a function:

```
You are a VEX analyst. Given a function from an ICS/OT software component,
decide whether the product is affected by the referenced weakness, following
the CISA justification questions in order:
Q1 Is the vulnerable code present?
Q2 Is it on a path the product executes?
Q3 Can an adversary control input that reaches it?
Q4 Is there an inline mitigation already present?
Answer with JSON: {"status": ..., "justification": ..., "rationale": ...}.

CWE: CWE-416
Component: ImageMagick
Function in this build:
```c
static boolean ReadICCProfile(j_decompress_ptr jpeg_info) { ... }
```
```

**Completion** is the judgment:

```json
{"status": "affected", "justification": null,
 "rationale": "The vulnerable construct (CWE-416) is present in this function."}
```

The `justification` field is one of the five CISA labels
(`component_not_present`, `vulnerable_code_not_present`,
`vulnerable_code_not_in_execute_path`,
`vulnerable_code_cannot_be_controlled_by_adversary`,
`inline_mitigations_already_exist`) or `null` when the status is `affected`.

---

## Files

| File | Rows | Purpose |
|---|---|---|
| `data/train.jsonl` | 10,068 | training set, balanced 5,034 affected / 5,034 not_affected |
| `data/eval_cisa_gold.jsonl` | 18 | held-out gold: real CISA-published justifications (never train on this) |

Fields: `instruction`, `completion`, `src` (provenance), and where available `cve`.

### Composition of `train.jsonl`

| Source | Rows | What it contributes |
|---|---|---|
| DiverseVul | 7,000 | C/C++ functions labelled vulnerable/safe → present vs not-present |
| BigVul | 3,000 | C/C++ vulnerable/patched function pairs → same construct, before vs after fix |
| project seed | 68 | vuln/patched code pairs collected from upstream fix commits |

Labels map directly to VEX status:
- a **vulnerable** function → `affected`
- a **patched / safe** function → `not_affected` + `vulnerable_code_not_present`

### The gold eval set

`eval_cisa_gold.jsonl` holds the **18 (advisory × CVE) pairs** that are the only
public ICS VEX justifications — extracted from the 12 CISA ICS-CERT advisories
whose CSAF documents carry a `vulnerabilities[].flags[].label`. Notably, all of
them use *code/build* justifications; none use an environment-based one. Use it
to measure whether a model reproduces real vendor/CISA judgments.

---

## Scope and honest limits

- The training labels are strongest for **Q1** (is the vulnerable construct
  present?), because the underlying corpora label vulnerable vs. non-vulnerable
  code. **Q2 (reachability)** and **Q3 (adversary control)** are under-specified
  in the source data and are better answered by program analysis (call graphs,
  taint, fuzzing) alongside a model; treat model answers to Q2/Q3 as reasoning,
  not proof.
- Functions are shown in isolation, without whole-program context.
- C/C++ only.

---

## Generation

The dataset is reproducible from public sources:

```bash
python scripts/collect_bigvul.py       # BigVul  -> vulnfix rows
python scripts/collect_diversevul.py   # DiverseVul -> vuln/safe rows
python scripts/build_seed.py           # project fix-commit pairs
python scripts/assemble.py             # merge, balance, split
```

---

## Sources & license

Built from public vulnerability datasets, reused under their terms:

- **DiverseVul** — Chen et al., *DiverseVul: A New Vulnerable Source Code Dataset*
  (RAID 2023). HF: `bstee615/diversevul`.
- **BigVul** — Fan et al., *A C/C++ Code Vulnerability Dataset with Code Changes
  and CVE Summaries* (MSR 2020). HF: `bstee615/bigvul`.
- Project seed pairs are derived from upstream open-source fix commits (GitHub).
- CISA gold labels are from CISA ICS-CERT CSAF advisories (public).

The transformation scripts and dataset packaging in this repository are released
under the MIT License (see `LICENSE`). The underlying code samples remain under
the licenses of their originating projects and datasets; users must observe
those. This dataset is intended for **defensive security research** — building
tools that assess vulnerability exploitability (VEX) — not for producing
exploits.

## Citation

```
@misc{vexc-instruct,
  title  = {vexc-instruct: an instruction dataset for VEX judgment over C/C++ code},
  author = {kakyung98},
  year   = {2026},
  url    = {https://github.com/kakyung98/vexc-instruct}
}
```
