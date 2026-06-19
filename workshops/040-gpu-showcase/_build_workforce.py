"""Generates 020_AI_Workforce_Analysis.ipynb — a 32B model analyzing real job data. No external deps."""
import json, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notebooks")
cells = []
def md(t):
    L=t.split("\n"); cells.append({"cell_type":"markdown","metadata":{},"source":[l+"\n" for l in L[:-1]]+[L[-1]]})
def code(t):
    L=t.split("\n"); cells.append({"cell_type":"code","metadata":{},"execution_count":None,"outputs":[],"source":[l+"\n" for l in L[:-1]]+[L[-1]]})

md(r"""# AI & the Workforce: Analyzing Real Job Data with a 32B Model

**NAIRR Workshop · the H100 as a research instrument (run on `g5.xl` / H100)**

This is the demo that **needs a big GPU.** We load a **32‑billion‑parameter** model — which uses
~**64 GB of GPU memory**, impossible on a laptop — and point it at a **real dataset of tech/security job
postings**, asking it to forecast, for each role: *will AI most likely **automate**, **augment**, or leave
**human‑driven** the core of this job?* Then we aggregate the results into a research‑style finding.

> **This is AI Horizon's actual research question** (how AI reshapes the cybersecurity workforce),
> run on real labor‑market data at a scale and model size you simply can't reach on local hardware.

> ⚠️ **Two things:** (1) the 32B model is a **~64 GB download** — for a live demo, **pre‑warm and shelve**
> the instance so it's instant. (2) A full GPU burns SUs fast — **shelve or delete when done.**

**Status: DRAFT** — test on the GPU before presenting.""")

md(r"""## 1. Setup""")
code(r'''import sys, subprocess, os
def pip(*a): subprocess.run([sys.executable,"-m","pip","install","-q",*a], check=True)
print("Installing libraries ...")
pip("torch", "transformers", "accelerate", "datasets", "pandas", "matplotlib")
import torch
assert torch.cuda.is_available(), "Run this on a full-GPU instance (g5.xl / H100)."
print("GPU:", torch.cuda.get_device_name(0))''')

code(r'''# ============================ CONFIG ============================
MODEL       = "Qwen/Qwen3-32B"   # ~64 GB VRAM — the "needs a big GPU" model.
                                  # For a quick test, use "Qwen/Qwen3-8B" (smaller download).
DATASET     = "lukebarousse/data_jobs"   # real tech/data job postings (titles + skills)
N_POSTINGS  = 120                # how many postings the model analyzes (scale on purpose)
# ===============================================================
import time, re, gc
print("Model:", MODEL, "| dataset:", DATASET, "| postings:", N_POSTINGS)''')

md(r"""## 2. The "look at the GPU" moment
We check GPU memory **before** and **after** loading the model. A 32B model alone consumes ~64 GB —
that number is the whole point of this workshop.""")
code(r'''def gpu_mem():
    out = subprocess.run(["nvidia-smi","--query-gpu=memory.used,memory.total","--format=csv,noheader,nounits"],
                         capture_output=True, text=True).stdout.strip().splitlines()[0]
    used, total = [int(x) for x in out.split(",")]
    return used, total

u,t = gpu_mem(); print(f"GPU memory BEFORE loading the model: {u:,} / {t:,} MiB used")''')

code(r'''from transformers import AutoTokenizer, AutoModelForCausalLM
tok = AutoTokenizer.from_pretrained(MODEL, padding_side="left")
if tok.pad_token is None: tok.pad_token = tok.eos_token
print("Loading the model (downloads ~64 GB the first time) ...")
model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.bfloat16,
                                             device_map="cuda", attn_implementation="sdpa")
model.eval()
u,t = gpu_mem()
print(f"\nGPU memory AFTER loading the model: {u:,} / {t:,} MiB used")
print(f">> This model alone is using ~{u/1024:.0f} GB of GPU memory. A laptop has none of this.")''')

md(r"""## 3. Load the real job-postings data
We pull a real dataset of tech/security job postings and select roles to analyze. (Swap `DATASET` for
any Hugging Face job dataset, or a Kaggle CSV you've downloaded.)""")
code(r'''from datasets import load_dataset
import pandas as pd

try:
    raw = load_dataset(DATASET, split="train")
    df = raw.to_pandas()
except Exception as e:
    print("Dataset load failed (", e, ") -> using a small built-in sample.")
    df = pd.DataFrame({"job_title":[
        "Security Operations Center Analyst","Cybersecurity Engineer","Penetration Tester",
        "Incident Response Specialist","Data Security Analyst","Cloud Security Architect",
        "Threat Intelligence Analyst","Vulnerability Management Engineer"],
        "job_skills":["siem, splunk, log analysis","python, firewalls, iam","kali, metasploit, scripting",
        "forensics, containment, playbooks","sql, dlp, encryption","aws, terraform, zero-trust",
        "osint, malware, reporting","nessus, patching, scripting"]})

def title_of(r): return str(r.get("job_title") or r.get("job_title_short") or "")
def skills_of(r): return str(r.get("job_skills") or "")

# Prefer security-related roles; fall back to the broader tech workforce if too few.
KW = ["security","cyber","soc","infosec","threat","incident","siem","vulnerab","penetration","malware"]
mask = df.apply(lambda r: any(k in (title_of(r)+" "+skills_of(r)).lower() for k in KW), axis=1)
sub = df[mask] if mask.sum() >= 20 else df
sub = sub.head(N_POSTINGS).reset_index(drop=True)
print(f"Analyzing {len(sub)} postings ({'security-focused' if mask.sum()>=20 else 'broad tech'}).")
print("Example:", title_of(sub.iloc[0]), "|", skills_of(sub.iloc[0])[:80])''')

md(r"""## 4. The 32B model forecasts AI impact for every posting
For each role it returns, in one line: whether AI will most likely **automate / augment / keep human**
the core of the job, plus the most AI‑exposed skills. This is the analysis that needs both a capable
model and the GPU throughput to run over the whole dataset.""")
code(r'''def prompt_for(r):
    msg = ("You are a workforce analyst studying how AI affects jobs. For the role below, answer in "
           "EXACTLY this one-line format:\n"
           "IMPACT: <AUTOMATE|AUGMENT|HUMAN> | SKILLS: skill1; skill2; skill3\n"
           "IMPACT = whether AI is most likely to automate, augment, or leave human-driven the CORE of "
           "this role. SKILLS = the 3 most AI-exposed skills.\n\n"
           f"Role title: {title_of(r)}\nListed skills: {skills_of(r)}\n\nAnswer: /no_think")
    return tok.apply_chat_template([{"role":"user","content":msg}], tokenize=False,
                                   add_generation_prompt=True, enable_thinking=False)

def analyze(rows, batch_size=8):
    out_rows=[]
    prompts=[prompt_for(r) for _,r in rows.iterrows()]
    t0=time.time()
    for i in range(0,len(prompts),batch_size):
        chunk=prompts[i:i+batch_size]
        enc=tok(chunk,return_tensors="pt",padding=True).to("cuda")
        with torch.no_grad():
            o=model.generate(**enc,max_new_tokens=64,do_sample=False,pad_token_id=tok.pad_token_id)
        for row in o:
            text=tok.decode(row[enc["input_ids"].shape[1]:],skip_special_tokens=True)
            m=re.search(r"IMPACT:\s*(AUTOMATE|AUGMENT|HUMAN)",text,re.I)
            s=re.search(r"SKILLS:\s*(.+)",text,re.I)
            out_rows.append({"impact":(m.group(1).upper() if m else "?"),
                             "skills":(s.group(1).strip() if s else "")})
        print(f"  analyzed {min(i+batch_size,len(prompts))}/{len(prompts)} ...", end="\r")
    print(f"\nDone in {time.time()-t0:.0f}s")
    return out_rows

results = analyze(sub)
sub2 = sub.copy(); sub2["impact"]=[r["impact"] for r in results]; sub2["ai_skills"]=[r["skills"] for r in results]
sub2[["job_title" if "job_title" in sub2 else sub2.columns[0]]].head() if False else None
print(sub2[[c for c in ["job_title","impact","ai_skills"] if c in sub2.columns]].head(8).to_string(index=False))''')

md(r"""## 5. The finding
Aggregate across all the roles the model analyzed.""")
code(r'''import matplotlib.pyplot as plt
counts = sub2["impact"].value_counts()
print("AI-impact breakdown across", len(sub2), "roles:"); print(counts.to_string())

fig,ax=plt.subplots(1,2,figsize=(13,4.5))
counts.reindex(["AUTOMATE","AUGMENT","HUMAN"]).fillna(0).plot.bar(
    ax=ax[0],color=["#c4502e","#d8a13a","#3a7d44"])
ax[0].set_title("Will AI automate, augment, or keep human?"); ax[0].tick_params(axis="x",rotation=0)

# top AI-exposed skills mentioned
from collections import Counter
skills=Counter()
for s in sub2["ai_skills"]:
    for tok_s in re.split(r"[;,]", s):
        tok_s=tok_s.strip().lower()
        if 2<len(tok_s)<30: skills[tok_s]+=1
top=pd.Series(dict(skills.most_common(10)))
top.sort_values().plot.barh(ax=ax[1],color="#49c"); ax[1].set_title("Most AI-exposed skills (model's view)")
plt.tight_layout(); plt.show()''')

md(r"""## 6. What this demonstrates

- **A model this size needs the GPU** — ~64 GB of VRAM just to *exist*. We showed it on `nvidia-smi`.
  This is the single clearest "you can't do this on a laptop."
- **Real analysis at scale** — the model read and classified a whole dataset of real job postings in
  minutes. That's a genuine research workflow (LLM‑assisted analysis), not a toy.
- **On mission** — this *is* AI Horizon's question — forecasting AI's effect on the cyber/tech workforce —
  answered with real labor data on national compute.

### Turn it into real research
- Scale to the **full dataset** (hundreds of thousands of postings) and track trends over time.
- Compare the **32B vs 8B** model's forecasts to study how model capability changes the analysis.
- Swap in a **cyber‑specific** postings dataset (e.g., a Kaggle CSV) for a pure cybersecurity study.

> 💡 **Done? Shelve or delete the instance.** A full GPU is the most SU‑expensive resource.""")

nb={"cells":cells,"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},
    "language_info":{"name":"python"}},"nbformat":4,"nbformat_minor":5}
with open(os.path.join(OUT,"020_AI_Workforce_Analysis.ipynb"),"w",encoding="utf-8") as f:
    json.dump(nb,f,indent=1)
print("wrote 020_AI_Workforce_Analysis.ipynb with", len(cells), "cells")
