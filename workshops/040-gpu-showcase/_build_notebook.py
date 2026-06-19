"""Generates 010_H100_Research_Showcase.ipynb (transformers-based, no vLLM). No external deps."""
import json, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notebooks")
cells = []
def md(t):
    L=t.split("\n"); cells.append({"cell_type":"markdown","metadata":{},"source":[l+"\n" for l in L[:-1]]+[L[-1]]})
def code(t):
    L=t.split("\n"); cells.append({"cell_type":"code","metadata":{},"execution_count":None,"outputs":[],"source":[l+"\n" for l in L[:-1]]+[L[-1]]})

md(r"""# What an H100 Unlocks: Throughput + a Real Research Workflow

**NAIRR Workshop · GPU showcase (run on a full GPU — e.g. Jetstream2 `g5.xl` / H100)**

NAIRR's big GPUs aren't just for demos — they're a **research instrument.** Two parts:

1. **Capability** — generate a big batch of text on the GPU and measure **throughput** (tokens/sec).
2. **A reproducible research workflow** — a small **benchmark study**: *how accurately do open LLMs answer
   cybersecurity exam questions, and does model size help?* We evaluate on **MMLU "computer security"**,
   compute accuracy, and compare a small vs. a larger model — a complete, publishable‑style mini‑result.

> Uses Hugging Face **`transformers`** (not vLLM) so it runs on a stock driver‑only GPU image with no
> CUDA‑toolkit/compiler setup. Same research workflow, maximum compatibility.

> ⚠️ **Cost:** a full‑GPU instance burns SUs fast. Run the demo, then **shelve or delete** the instance.

**Status: DRAFT** — test on the GPU before presenting.""")

md(r"""## 1. Setup (needs a GPU)
The model is loaded straight onto the GPU with `transformers` — no compiling, no extra CUDA install.""")
code(r'''import sys, subprocess, os
def pip(*a): subprocess.run([sys.executable,"-m","pip","install","-q",*a], check=True)
print("Installing libraries (a few minutes the first time) ...")
pip("torch", "transformers", "accelerate", "datasets", "pandas", "matplotlib")
import torch
assert torch.cuda.is_available(), "No GPU detected — run this on a full-GPU instance (g3.xl / g4.xl / g5.xl)."
print("GPU:", torch.cuda.get_device_name(0), "| ready")''')

code(r'''# ============================ CONFIG ============================
SMALL_MODEL  = "Qwen/Qwen3-1.7B"     # quick baseline
LARGE_MODEL  = "Qwen/Qwen3-8B"       # realistic local model (H100 runs it easily)
MMLU_SUBJECT = "computer_security"   # the cybersecurity exam set
N_QUESTIONS  = 100                   # cap for a snappy demo (subject has ~100)
# ===============================================================
import time, gc
from transformers import AutoTokenizer, AutoModelForCausalLM
print("Will evaluate:", SMALL_MODEL, "vs", LARGE_MODEL, "on MMLU:", MMLU_SUBJECT)''')

md(r"""## 2. Helpers — load a model on the GPU, and format chat prompts""")
code(r'''def load(model_id):
    tok = AutoTokenizer.from_pretrained(model_id, padding_side="left")
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch.bfloat16, device_map="cuda",
        attn_implementation="sdpa")        # SDPA = built into PyTorch, no compile needed
    model.eval()
    return tok, model

def chat(tok, text):
    return tok.apply_chat_template([{"role": "user", "content": text + " /no_think"}],
                                   tokenize=False, add_generation_prompt=True, enable_thinking=False)
print("helpers ready")''')

md(r"""## 3. Capability — throughput on the GPU
Generate a batch of prompts at once and measure tokens/sec. (We reuse this model for the benchmark.)""")
code(r'''tok, model = load(LARGE_MODEL)

prompts = [chat(tok, "Explain one cybersecurity best practice in 3 sentences.") for _ in range(64)]
inp = tok(prompts, return_tensors="pt", padding=True).to("cuda")
t0 = time.time()
with torch.no_grad():
    out = model.generate(**inp, max_new_tokens=128, do_sample=True, temperature=0.7,
                         pad_token_id=tok.pad_token_id)
dt = time.time() - t0
new_tokens = (out.shape[1] - inp["input_ids"].shape[1]) * out.shape[0]
print(f"\n{len(prompts)} prompts, ~{new_tokens} tokens in {dt:.1f}s")
print(f">> Throughput: {new_tokens/dt:,.0f} tokens/sec on {torch.cuda.get_device_name(0)}")''')

md(r"""## 4. Research workflow — benchmarking accuracy on cybersecurity questions

A standard research pattern: take a recognized **benchmark**, run the model over it, report **accuracy**.
We use **MMLU `computer_security`** (multiple‑choice exam questions) — exactly how papers report
"model X scores Y% on benchmark Z."

### Load the benchmark""")
code(r'''from datasets import load_dataset
ds = load_dataset("cais/mmlu", MMLU_SUBJECT, split="test")
if N_QUESTIONS:
    ds = ds.select(range(min(N_QUESTIONS, len(ds))))
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

def evaluate(tok, model, batch_size=16):
    prompts = [chat(tok, format_q(q)) for q in ds]
    preds = []
    for i in range(0, len(prompts), batch_size):
        chunk = prompts[i:i+batch_size]
        enc = tok(chunk, return_tensors="pt", padding=True).to("cuda")
        with torch.no_grad():
            o = model.generate(**enc, max_new_tokens=4, do_sample=False,
                               pad_token_id=tok.pad_token_id)
        for row in o:
            new = row[enc["input_ids"].shape[1]:]
            preds.append(parse_letter(tok.decode(new, skip_special_tokens=True)))
    gold = [LETTERS[q["answer"]] for q in ds]
    return sum(p==g for p,g in zip(preds,gold)) / len(ds)
print("evaluator ready")''')

md(r"""### Evaluate the larger model (already loaded)""")
code(r'''acc_large = evaluate(tok, model)
print(f"{LARGE_MODEL}: {acc_large*100:.1f}% on MMLU {MMLU_SUBJECT}")
del model; gc.collect(); torch.cuda.empty_cache()''')

md(r"""### Evaluate the smaller model — does size matter?""")
code(r'''tok_s, model_s = load(SMALL_MODEL)
acc_small = evaluate(tok_s, model_s)
print(f"{SMALL_MODEL}: {acc_small*100:.1f}% on MMLU {MMLU_SUBJECT}")
del model_s; gc.collect(); torch.cuda.empty_cache()''')

md(r"""### The result""")
code(r'''import pandas as pd, matplotlib.pyplot as plt
res = pd.DataFrame({"model":[SMALL_MODEL, LARGE_MODEL], "params":["1.7B","8B"],
                    "accuracy_%":[round(acc_small*100,1), round(acc_large*100,1)]})
print(res.to_string(index=False))
res.plot.bar(x="params", y="accuracy_%", legend=False, color=["#49c","#4c9"])
plt.title(f"Open-LLM accuracy on MMLU {MMLU_SUBJECT}"); plt.ylabel("accuracy (%)")
plt.xticks(rotation=0); plt.tight_layout(); plt.show()''')

md(r"""## 5. (Bonus) Synthetic data generation — another research workflow
LLMs on a fast GPU are also used to **generate datasets** (e.g., training data for a smaller classifier).""")
code(r'''tok, gen = load(LARGE_MODEL)
ask = chat(tok, 'Write one realistic example phishing email, then a blank line, then one realistic '
                'legitimate work email. Label each "PHISHING:" or "LEGIT:".')
enc = tok([ask]*3, return_tensors="pt", padding=True).to("cuda")
with torch.no_grad():
    o = gen.generate(**enc, max_new_tokens=300, do_sample=True, temperature=0.9,
                     pad_token_id=tok.pad_token_id)
for i in range(2):
    text = tok.decode(o[i][enc["input_ids"].shape[1]:], skip_special_tokens=True)
    print(f"--- sample {i+1} ---\n{text.strip()[:400]}\n")
del gen; gc.collect(); torch.cuda.empty_cache()
print("In a real study you'd generate thousands of these to train/augment a phishing detector.")''')

md(r"""## 6. What this shows researchers

- **Throughput:** the GPU generated a big batch of text fast — enough to evaluate or generate over
  **large datasets** in minutes, not days.
- **Realistic model sizes:** an 8B model (and far larger) runs comfortably — impossible on a laptop.
- **Reproducible results:** we produced an **accuracy number on a recognized benchmark** and a clear
  finding (**bigger model → higher accuracy on security questions**) — the backbone of evaluation research.
- **Beyond eval:** the same setup powers **synthetic data generation, large‑scale annotation,
  fine‑tuning, and RAG over big corpora.**

### Ideas to extend into actual research
- Add more MMLU subjects, or a domain‑specific question set, and compare several open models.
- Generate a synthetic security dataset and train/evaluate a classifier on it.
- Measure accuracy vs. quantization level (ties to the quantization workshop) — a real, citable study.

> 💡 **When done, shelve or delete the instance** — a full GPU is the most SU‑expensive resource.""")

nb={"cells":cells,"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},
    "language_info":{"name":"python"}},"nbformat":4,"nbformat_minor":5}
with open(os.path.join(OUT,"010_H100_Research_Showcase.ipynb"),"w",encoding="utf-8") as f:
    json.dump(nb,f,indent=1)
print("wrote 010_H100_Research_Showcase.ipynb with", len(cells), "cells")
