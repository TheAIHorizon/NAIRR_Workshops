"""Generates 010_Quantization.ipynb for the quantization workshop. No external deps."""
import json, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notebooks")
cells = []
def md(t):
    L=t.split("\n"); cells.append({"cell_type":"markdown","metadata":{},"source":[l+"\n" for l in L[:-1]]+[L[-1]]})
def code(t):
    L=t.split("\n"); cells.append({"cell_type":"code","metadata":{},"execution_count":None,"outputs":[],"source":[l+"\n" for l in L[:-1]]+[L[-1]]})

md(r"""# Quantization: How Small Can a Model Get Before It Gets Worse?

**NAIRR Workshop · running the *same* model at different quant sizes**

Quantization shrinks a model by storing its numbers at lower precision. Smaller = **less disk, less
memory, faster** — but at some point, **quality drops.** This lab runs **one model (Qwen3) at four
precisions** and measures the trade-off on identical prompts.

| Level | Bits (approx) | ~Size (1.7B) | Idea |
|-------|---------------|--------------|------|
| **Q4_K_M** | ~4-bit | ~1.1 GB | Smallest/fastest — the popular default |
| **Q6_K**   | ~6-bit | ~1.5 GB | A middle ground |
| **Q8_0**   | ~8-bit | ~1.8 GB | Near-full quality |
| **F16**    | 16-bit | ~3.4 GB | Full precision — the reference (un-quantized) |

> **The question:** as we go from F16 down to Q4, **how much speed/space do we save, and where (if
> anywhere) does the answer quality actually suffer?**""")

md(r"""## 1. Configuration

The default is **Qwen3‑1.7B** — all four quant files (~8 GB total) fit a basic 20 GB instance, so we
just load each, test it, and unload. Switch `MODEL_SIZE = "8b"` for a more realistic model; the 8B
files are large, so the notebook then **deletes each file after testing** to reclaim disk.""")
code(r'''# ============================ CONFIG ============================
MODEL_SIZE = "1.7b"          # "1.7b" (default, all fits) or "8b" (realistic; deletes between quants)

# Test depth: "single" (1 prompt), "simple" (3 prompts), "complete" (all 7).
TEST_MODE  = "simple"
MAX_TOKENS = 256

RUN_INSTALL = True
# ===============================================================
if MODEL_SIZE == "8b":
    GGUF_REPO = "Qwen/Qwen3-8B-GGUF"
    QUANTS    = ["Q4_K_M", "Q6_K", "Q8_0"]      # F16 (~16 GB) is too big / slow for a class box
    DELETE_AFTER = True                          # reclaim disk between quants
else:                                            # 1.7b
    GGUF_REPO = "Qwen/Qwen3-1.7B-GGUF"
    QUANTS    = ["Q4_K_M", "Q6_K", "Q8_0", "F16"]
    DELETE_AFTER = False                         # all four fit; keep them

# match each level to substrings that appear in the GGUF filename
QUANT_PATTERNS = {"Q4_K_M": ["q4_k_m"], "Q6_K": ["q6_k"], "Q8_0": ["q8_0"],
                  "F16": ["f16", "bf16", "fp16"]}
ENABLE_THINKING = False
TEMPERATURE = 0.7
print(f"Model: {GGUF_REPO} | quants: {QUANTS} | delete-after: {DELETE_AFTER} | mode: {TEST_MODE}")''')

md(r"""## 2. Environment check
This lab runs on **CPU** (llama.cpp). If a usable GPU is present it'll use it; otherwise CPU is fine.""")
code(r'''import subprocess, platform, sys, os, ctypes
print("Python:", sys.version.split()[0], "| CPUs:", os.cpu_count())
GPU_DRIVER = False
try:
    subprocess.run(["nvidia-smi"], capture_output=True, check=True); GPU_DRIVER = True
except Exception:
    pass
CUDA_OK = False
if GPU_DRIVER:
    try: ctypes.CDLL("libcudart.so.12"); CUDA_OK = True
    except OSError: pass
HAS_GPU = GPU_DRIVER and CUDA_OK
N_GPU_LAYERS = -1 if HAS_GPU else 0
print(">> GPU mode" if HAS_GPU else ">> CPU mode (fine for this lab)")''')

md(r"""## 3. Install
`llama-cpp-python` lets us load any specific GGUF quant file. On CPU we compile a CPU-only build (a few
minutes) so it can't pull a CUDA-linked wheel that fails to load.""")
code(r'''if RUN_INSTALL:
    def pip(*a): subprocess.run([sys.executable,"-m","pip","install","-q",*a], check=True)
    pip("huggingface_hub", "pandas", "matplotlib", "tqdm")
    if HAS_GPU:
        subprocess.run([sys.executable,"-m","pip","install","-q","llama-cpp-python",
                        "--extra-index-url","https://abetlen.github.io/llama-cpp-python/whl/cu124"], check=True)
    else:
        print("compiling CPU-only llama-cpp-python (a few minutes) ...")
        subprocess.run("sudo apt-get update -y && sudo apt-get install -y build-essential cmake python3-dev", shell=True)
        env={**os.environ,"CMAKE_ARGS":"-DGGML_CUDA=off","FORCE_CMAKE":"1"}
        subprocess.run([sys.executable,"-m","pip","install","-q","--no-cache-dir",
                        "--no-binary=llama-cpp-python","llama-cpp-python"], env=env, check=True)
    print("install done")
else:
    print("skipped install")''')

md(r"""## 4. The benchmark prompts
Same prompts for every quant level. Some are easy (any precision handles them); the **hard ones
(reasoning, code, precise format)** are where lower precision tends to show cracks.""")
code(r'''ALL_PROMPTS = {
 "greeting":  "Hi! In one short sentence, who are you?",
 "sky":       "Why is the sky blue? Explain in 3-4 sentences.",
 "primes":    "Write an efficient Python function that returns all prime numbers up to 10000. Only output the code.",
 "essay":     "Write a clear ~200-word explanation of how public-key encryption works, for a beginner.",
 "reasoning": "A store takes 25% off, then 10% off the discounted price. What is the single overall percentage discount? Show your steps, then give the final number.",
 "json":      'Return ONLY a JSON array of the 4 seasons, each an object with keys "name" and "avg_temp_c" (number). No prose.',
 "longctx":   "Summarize the key idea in one sentence: Quantization stores a neural network's weights at lower numeric precision to save memory and speed up inference, usually with only a small loss in accuracy.",
}
SUBSET = {"single":["reasoning"], "simple":["sky","primes","reasoning"]}.get(TEST_MODE)
PROMPTS = {k:ALL_PROMPTS[k] for k in SUBSET} if SUBSET else ALL_PROMPTS
print(f"[{TEST_MODE}] {len(PROMPTS)} prompts:", ", ".join(PROMPTS))''')

md(r"""## 5. Helpers
Download a specific quant file, load it, time generation, then free it (and optionally delete the file).""")
code(r'''import time, gc, json, glob
from pathlib import Path
from huggingface_hub import list_repo_files, hf_hub_download
from tqdm.auto import tqdm

RESULTS = []   # one row per (quant, prompt)
SIZES   = {}   # quant -> file size MB
LOADS   = {}   # quant -> load seconds

def ram_used_mb():
    try:
        info={}
        for line in open("/proc/meminfo"):
            k,v=line.split(":",1); info[k]=int(v.split()[0])
        return (info["MemTotal"]-info.get("MemAvailable",info["MemFree"]))/1024
    except Exception: return -1

_repo_files = [f for f in list_repo_files(GGUF_REPO) if f.endswith(".gguf")]
def gguf_for(quant):
    pats = QUANT_PATTERNS[quant]
    matches = [f for f in _repo_files if any(p in f.lower() for p in pats)]
    if not matches:
        raise FileNotFoundError(f"No GGUF for {quant} in {GGUF_REPO}. Files: {_repo_files}")
    return sorted(matches, key=len)[0]   # shortest match = the plain single-file build

def record(quant, name, ptok, ctok, ttft, total_s, text):
    gen = max(total_s-(ttft or 0),1e-6); tps = ctok/gen if ctok else 0
    RESULTS.append({"quant":quant,"prompt":name,"prompt_tokens":ptok,"completion_tokens":ctok,
                    "ttft_s":round(ttft,3) if ttft else None,"total_s":round(total_s,2),
                    "tokens_per_sec":round(tps,1),"output":text})
    tqdm.write(f"  [{quant:7}] {name:10} {ctok:4d} tok {total_s:6.2f}s {tps:6.1f} tok/s")
print("helpers ready")''')

md(r"""## 6. Run every quant level
For each precision: download → load → run the prompts → record speed → unload (→ delete if needed).""")
code(r'''from llama_cpp import Llama

def messages(p):
    return [{"role":"user","content": p if ENABLE_THINKING else p+" /no_think"}]

for quant in QUANTS:
    print("="*70); print("QUANT:", quant)
    fname = gguf_for(quant)
    path  = hf_hub_download(repo_id=GGUF_REPO, filename=fname)
    SIZES[quant] = os.path.getsize(path)/1e6
    print(f"  file: {fname}  ({SIZES[quant]:.0f} MB)")

    t0=time.time()
    llm = Llama(model_path=path, n_gpu_layers=N_GPU_LAYERS, n_ctx=4096,
                n_threads=os.cpu_count(), verbose=False)
    LOADS[quant]=time.time()-t0
    print(f"  loaded in {LOADS[quant]:.1f}s | RAM {ram_used_mb():.0f} MB")

    for nm,pr in tqdm(PROMPTS.items(), total=len(PROMPTS), desc=quant):
        t0=time.time(); first=None; text=""
        for ch in llm.create_chat_completion(messages=messages(pr), max_tokens=MAX_TOKENS,
                                              temperature=TEMPERATURE, stream=True):
            d=ch["choices"][0]["delta"].get("content","")
            if d:
                if first is None: first=time.time()
                text+=d
        total=time.time()-t0
        ptok=len(llm.tokenize(pr.encode())); ctok=len(llm.tokenize(text.encode())) if text else 0
        record(quant, nm, ptok, ctok, (first-t0) if first else None, total, text)

    del llm; gc.collect(); time.sleep(1)
    if DELETE_AFTER:
        try: os.remove(path); print(f"  deleted {fname} to reclaim disk")
        except OSError as e: print("  (could not delete:", e, ")")
print("\nAll quant levels done.")''')

md(r"""## 7. The comparison

### Size, load time, and speed by quant level""")
code(r'''import pandas as pd
pd.set_option("display.max_colwidth", 60)
df = pd.DataFrame(RESULTS)

summary = (df.groupby("quant").agg(avg_tokens_per_sec=("tokens_per_sec","mean"),
                                   avg_ttft_s=("ttft_s","mean")).round(2))
summary["size_MB"]   = pd.Series(SIZES).round(0)
summary["load_s"]    = pd.Series(LOADS).round(1)
order = [q for q in QUANTS if q in summary.index]
summary = summary.loc[order, ["size_MB","load_s","avg_ttft_s","avg_tokens_per_sec"]]
print("=== size / speed by quant ===")
summary''')

code(r'''# tokens/sec per prompt x quant
print("=== tokens/sec by prompt ===")
df.pivot_table(index="prompt", columns="quant", values="tokens_per_sec", aggfunc="mean").round(1)''')

code(r'''import matplotlib.pyplot as plt
fig,ax=plt.subplots(1,2,figsize=(12,4))
summary["size_MB"].plot.bar(ax=ax[0],color="#49c"); ax[0].set_title("Size on disk (MB)"); ax[0].tick_params(axis="x",rotation=0)
summary["avg_tokens_per_sec"].plot.bar(ax=ax[1],color="#4c9"); ax[1].set_title("Avg speed (tokens/sec)"); ax[1].tick_params(axis="x",rotation=0)
plt.tight_layout(); plt.show()''')

md(r"""### Quality side-by-side
Read the answers for a hard prompt across precisions. Look for where the lower quants start to drift,
get sloppy, or break format — that's the quality cost of shrinking the model.""")
code(r'''def show(name, limit=400):
    if name not in PROMPTS:
        print(f"(prompt '{name}' not run in this TEST_MODE)"); return
    print("="*90); print("PROMPT:", PROMPTS[name][:120]); print()
    for q in QUANTS:
        rows=[r for r in RESULTS if r["prompt"]==name and r["quant"]==q]
        if rows:
            print(f"--- {q} ({rows[0]['tokens_per_sec']} tok/s) ---")
            print(rows[0]["output"][:limit].strip()); print()

# pick a revealing one that ran (reasoning is in every TEST_MODE)
show("reasoning")''')

md(r"""## 8. What to take away

- **Lower precision = smaller and faster.** Q4 is roughly a third of F16's size and noticeably quicker —
  that's why Q4_K_M is the popular default for running models locally.
- **Quality holds up surprisingly well** on everyday prompts; the gap usually only shows on the **hard
  ones** (multi-step reasoning, exact code, strict format).
- **The sweet spot** for most local use is **Q4_K_M or Q6_K** — most of the quality at a fraction of the
  size. Reach for **Q8/F16** only when you need the last bit of accuracy and have the memory to spare.

### Try next
- Set `TEST_MODE = "complete"` for all 7 prompts (longer run).
- Set `MODEL_SIZE = "8b"` to compare a realistic local model (the notebook will delete each file after
  testing to fit the disk).""")

nb={"cells":cells,"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},
    "language_info":{"name":"python"}},"nbformat":4,"nbformat_minor":5}
with open(os.path.join(OUT,"010_Quantization.ipynb"),"w",encoding="utf-8") as f:
    json.dump(nb,f,indent=1)
print("wrote 010_Quantization.ipynb with", len(cells), "cells")
