"""Generates 010_H100_Research_Showcase.ipynb. No external deps."""
import json, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notebooks")
cells = []
def md(t):
    L=t.split("\n"); cells.append({"cell_type":"markdown","metadata":{},"source":[l+"\n" for l in L[:-1]]+[L[-1]]})
def code(t):
    L=t.split("\n"); cells.append({"cell_type":"code","metadata":{},"execution_count":None,"outputs":[],"source":[l+"\n" for l in L[:-1]]+[L[-1]]})

md(r"""# What an H100 Unlocks: Throughput + a Real Research Workflow

**NAIRR Workshop · GPU showcase (run on a full GPU — e.g. Jetstream2 `g5.xl` / H100)**

This notebook makes the case that NAIRR's big GPUs aren't just for demos — they're a **research
instrument.** Two parts:

1. **Capability** — serve a real model with **vLLM** and measure raw **throughput** (tokens/sec under
   batching). The kind of number a laptop can't touch.
2. **A reproducible research workflow** — run a small **benchmark study**: *how accurately do open LLMs
   answer cybersecurity exam questions, and does model size help?* We evaluate on the **MMLU
   "computer security"** set, compute accuracy, and compare a small vs. a larger model — a complete,
   publishable‑style mini‑result.

> The point for researchers: the H100 lets you **evaluate models at scale, run realistic model sizes,
> and produce reproducible results** in minutes. Not original work here — a known benchmark — but it
> shows exactly the workflow real studies use.

> ⚠️ **Cost:** a full‑GPU instance burns SUs fast. Run the demo, then **shelve or delete** the instance.
> Shelving frees your quota and stops SU charges while preserving the disk.

**Status: DRAFT** — test‑run on the GPU before presenting (vLLM/dataset versions can need small tweaks).""")

md(r"""## 1. Setup (needs a GPU)

> **Heads‑up:** `pip install vllm` is a **large download** (PyTorch + CUDA) — give it a few minutes. Also,
> vLLM doesn't always release GPU memory cleanly between models, so **if loading the second model later
> fails with an out‑of‑memory error, just do Kernel → Restart and run one model at a time.**""")
code(r'''import sys, subprocess, os
def pip(*a): subprocess.run([sys.executable,"-m","pip","install","-q",*a], check=True)
print("Installing vLLM (it brings PyTorch + CUDA) — a few minutes the first time ...")
pip("vllm", "datasets", "pandas", "matplotlib")

# vLLM defaults to the FlashInfer backend, which JIT-COMPILES CUDA kernels at load time and
# needs `nvcc` / the CUDA toolkit -- absent on driver-only GPU images (you get the driver, not
# the dev toolkit). Remove FlashInfer so vLLM falls back to prebuilt flash-attn, and pin it.
subprocess.run([sys.executable,"-m","pip","uninstall","-y","-q","flashinfer-python","flashinfer"],
               check=False)
os.environ.setdefault("VLLM_ATTENTION_BACKEND", "FLASH_ATTN")  # fallback if needed: "TORCH_SDPA"

import torch   # available now that vLLM pulled it in
assert torch.cuda.is_available(), "No GPU detected — run this on a full-GPU instance (g3.xl / g4.xl / g5.xl)."
print("GPU:", torch.cuda.get_device_name(0), "| attention:", os.environ["VLLM_ATTENTION_BACKEND"], "| ready")''')

code(r'''# ============================ CONFIG ============================
SMALL_MODEL = "Qwen/Qwen3-1.7B"     # quick baseline
LARGE_MODEL = "Qwen/Qwen3-8B"       # realistic local model (H100 runs it easily)
MMLU_SUBJECT = "computer_security"  # the cybersecurity exam set
N_QUESTIONS  = 100                  # cap for a snappy demo (subject has ~100)
# ===============================================================
from transformers import AutoTokenizer
import time, gc, json
print("Will evaluate:", SMALL_MODEL, "vs", LARGE_MODEL, "on MMLU:", MMLU_SUBJECT)''')

md(r"""## 2. Capability — raw throughput with vLLM
Load a model and generate a big batch at once. vLLM's continuous batching keeps the GPU saturated; the
**aggregate tokens/sec** is the headline number. (We reuse this model for the benchmark below.)""")
code(r'''from vllm import LLM, SamplingParams

llm = LLM(model=LARGE_MODEL, dtype="bfloat16", gpu_memory_utilization=0.90,
          max_model_len=4096, enforce_eager=True)
tok = AutoTokenizer.from_pretrained(LARGE_MODEL)

def chat_prompt(text):
    return tok.apply_chat_template([{"role":"user","content":text+" /no_think"}],
                                   tokenize=False, add_generation_prompt=True, enable_thinking=False)

# fire 128 prompts at once and measure aggregate throughput
batch = [chat_prompt("Explain one cybersecurity best practice in 3 sentences.") for _ in range(128)]
t0 = time.time()
outs = llm.generate(batch, SamplingParams(temperature=0.7, max_tokens=128))
dt = time.time() - t0
gen_tokens = sum(len(o.outputs[0].token_ids) for o in outs)
print(f"\n{len(batch)} prompts, {gen_tokens} tokens generated in {dt:.1f}s")
print(f">> Aggregate throughput: {gen_tokens/dt:,.0f} tokens/sec on this GPU")''')

md(r"""## 3. Research workflow — benchmarking LLM accuracy on cybersecurity questions

A standard research pattern: take a recognized **benchmark**, run the model over it, and report
**accuracy**. We use **MMLU `computer_security`** (multiple‑choice exam questions). This is exactly how
papers report "model X scores Y% on benchmark Z."

### Load the benchmark""")
code(r'''from datasets import load_dataset
ds = load_dataset("cais/mmlu", MMLU_SUBJECT, split="test")
if N_QUESTIONS: ds = ds.select(range(min(N_QUESTIONS, len(ds))))
print(f"{len(ds)} questions. Example:")
print(ds[0]["question"]); print(ds[0]["choices"]); print("gold:", "ABCD"[ds[0]["answer"]])''')

code(r'''LETTERS = ["A","B","C","D"]
def format_q(q):
    opts = "\n".join(f"{LETTERS[i]}. {c}" for i,c in enumerate(q["choices"]))
    return (f"Answer the multiple-choice question. Reply with ONLY the letter (A, B, C, or D).\n\n"
            f"{q['question']}\n{opts}\n\nAnswer:")
def parse_letter(text):
    for ch in text.upper():
        if ch in "ABCD": return ch
    return "?"

def evaluate(model_llm):
    prompts = [chat_prompt(format_q(q)) for q in ds]
    outs = model_llm.generate(prompts, SamplingParams(temperature=0, max_tokens=8))
    preds = [parse_letter(o.outputs[0].text) for o in outs]
    gold  = [LETTERS[q["answer"]] for q in ds]
    correct = sum(p==g for p,g in zip(preds,gold))
    return correct/len(ds), preds, gold
print("evaluator ready")''')

md(r"""### Evaluate the larger model (already loaded)""")
code(r'''acc_large, _, _ = evaluate(llm)
print(f"{LARGE_MODEL}: {acc_large*100:.1f}% on MMLU {MMLU_SUBJECT}")

# free the GPU before loading the smaller model
import contextlib
del llm; gc.collect(); torch.cuda.empty_cache()
with contextlib.suppress(Exception):
    from vllm.distributed.parallel_state import destroy_model_parallel; destroy_model_parallel()''')

md(r"""### Evaluate the smaller model — does size matter?

> If this cell errors while loading the model (GPU memory not fully freed by vLLM), **Kernel → Restart**
> and run just one model — each loads fine in a fresh kernel.""")
code(r'''llm_s = LLM(model=SMALL_MODEL, dtype="bfloat16", gpu_memory_utilization=0.90,
            max_model_len=4096, enforce_eager=True)
tok = AutoTokenizer.from_pretrained(SMALL_MODEL)
acc_small, _, _ = evaluate(llm_s)
print(f"{SMALL_MODEL}: {acc_small*100:.1f}% on MMLU {MMLU_SUBJECT}")
del llm_s; gc.collect(); torch.cuda.empty_cache()''')

md(r"""### The result""")
code(r'''import pandas as pd, matplotlib.pyplot as plt
res = pd.DataFrame({"model":[SMALL_MODEL, LARGE_MODEL],
                    "params":["1.7B","8B"],
                    "accuracy_%":[round(acc_small*100,1), round(acc_large*100,1)]})
print(res.to_string(index=False))
res.plot.bar(x="params", y="accuracy_%", legend=False, color=["#49c","#4c9"])
plt.title(f"Open-LLM accuracy on MMLU {MMLU_SUBJECT}"); plt.ylabel("accuracy (%)")
plt.xticks(rotation=0); plt.tight_layout(); plt.show()''')

md(r"""## 4. (Bonus) Synthetic data generation — another research workflow
LLMs on a fast GPU are also used to **generate datasets** (e.g., training data for a smaller classifier).
Here's the pattern in miniature — generate labeled examples in one batched call.""")
code(r'''gen = LLM(model=LARGE_MODEL, dtype="bfloat16", gpu_memory_utilization=0.90, max_model_len=4096, enforce_eager=True)
tok = AutoTokenizer.from_pretrained(LARGE_MODEL)
ask = chat_prompt('Write one realistic example phishing email. Then a blank line, then one realistic legitimate work email. Label each "PHISHING:" or "LEGIT:".')
out = gen.generate([ask]*5, SamplingParams(temperature=0.9, max_tokens=300))
for i,o in enumerate(out[:2]):
    print(f"--- sample {i+1} ---\n{o.outputs[0].text.strip()[:400]}\n")
del gen; gc.collect(); torch.cuda.empty_cache()
print("In a real study you'd generate thousands of these to train/augment a phishing detector.")''')

md(r"""## 5. What this shows researchers

- **Throughput:** the GPU served a large batch at thousands of tokens/sec — enough to evaluate or
  generate over **large datasets** in minutes, not days.
- **Realistic model sizes:** an 8B model (and far larger) runs comfortably — impossible on a laptop.
- **Reproducible results:** we produced an **accuracy number on a recognized benchmark** and a clear
  finding (**bigger model → higher accuracy on security questions**). That's the backbone of real
  evaluation research.
- **Beyond eval:** the same setup powers **synthetic data generation, large‑scale annotation,
  fine‑tuning, and RAG over big corpora** — all standard research workflows the H100 makes practical.

### Ideas to extend into actual research
- Add more MMLU subjects, or a domain‑specific question set, and compare several open models.
- Generate a synthetic security dataset and train/evaluate a classifier on it.
- Measure accuracy vs. quantization level (ties to the quantization workshop) — a real, citable study.

> 💡 **When you're done, shelve or delete the instance** — a full GPU is the most SU‑expensive resource.""")

nb={"cells":cells,"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},
    "language_info":{"name":"python"}},"nbformat":4,"nbformat_minor":5}
with open(os.path.join(OUT,"010_H100_Research_Showcase.ipynb"),"w",encoding="utf-8") as f:
    json.dump(nb,f,indent=1)
print("wrote 010_H100_Research_Showcase.ipynb with", len(cells), "cells")
