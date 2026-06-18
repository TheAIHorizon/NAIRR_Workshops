"""Generates the 5 train/tune/RAG notebooks (nbformat 4.5). No external deps."""
import json, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notebooks")

def nb_new():
    return []

def md(cells, text):
    lines = text.split("\n")
    src = [l + "\n" for l in lines[:-1]] + [lines[-1]]
    cells.append({"cell_type": "markdown", "metadata": {}, "source": src})

def code(cells, text):
    lines = text.split("\n")
    src = [l + "\n" for l in lines[:-1]] + [lines[-1]]
    cells.append({"cell_type": "code", "metadata": {}, "execution_count": None,
                  "outputs": [], "source": src})

def write(cells, name):
    nb = {"cells": cells,
          "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                       "language_info": {"name": "python"}},
          "nbformat": 4, "nbformat_minor": 5}
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1)
    print("wrote", name, "(", len(cells), "cells )")

# ============================================================ 00 SETUP
c = nb_new()
md(c, r"""# 00 · Setup & Shared Ingredients

**Train vs. Tune vs. RAG — a side-by-side workshop**

This series shows three different ways to make an AI model useful for *your* topic, all on the
**same base model, the same knowledge, and the same test questions** so you can compare them fairly:

| Notebook | Approach | What changes | Who runs it |
|----------|----------|--------------|-------------|
| 01 | **Train from scratch** | The model learns everything from your data, from zero | Instructor (GPU) |
| 02 | **Fine-tune (LoRA)** | Nudges a pretrained model toward your task/format | Instructor (GPU) |
| 03 | **RAG** | *Nothing* in the model — it retrieves facts at question time | Anyone (CPU ok) |
| 04 | **Compare** | Same questions to all of them, side by side | Students (CPU ok) |

> **The big idea:** *need new **facts** → RAG; need new **behavior/format** → fine-tune; need a brand-new
> **capability** → train (and you'll see why that's expensive).*

This notebook defines the **shared ingredients** every other notebook uses: the base model, a small
knowledge corpus, and the fixed set of test questions.""")

md(c, r"""## Install dependencies
The instructor's build notebooks (01, 02) need the full set; the student compare (04) and RAG (03)
need only the lighter ones. Installing everything here is fine.""")
code(c, r'''import sys, subprocess
def pip(*a): subprocess.run([sys.executable, "-m", "pip", "install", "-q", *a], check=True)
pip("transformers", "datasets", "accelerate", "peft", "trl",
    "sentence-transformers", "faiss-cpu", "huggingface_hub")
print("dependencies installed")''')

md(c, r"""## Configuration
One base model for everything. We use a small model so training and tuning are quick and the whole
thing runs on modest hardware.""")
code(c, r'''from pathlib import Path

# Small instruct model used for fine-tuning (02) and RAG (03).
BASE_MODEL = "Qwen/Qwen3-1.7B"

# Where artifacts (trained model, LoRA adapter, RAG index) are saved/loaded.
ARTIFACTS = Path("artifacts"); ARTIFACTS.mkdir(exist_ok=True)

# OPTIONAL: to share with students via Hugging Face, set your repo (e.g. "your-org/ttr-demo").
HF_REPO = None

print("Base model:", BASE_MODEL)
print("Artifacts dir:", ARTIFACTS.resolve())''')

md(c, r"""## The shared knowledge corpus
A small, self-contained cybersecurity corpus — no downloads, so it always works. A few entries are
**deliberately fictional/proprietary** (a made-up university's policies). No pretrained model could
possibly know those — so later, **only RAG will answer them correctly.** That makes the difference
between the approaches unmistakable.""")
code(c, r'''import json

CORPUS = [
    {"title": "Phishing", "text": "Phishing is a social-engineering attack where an attacker sends fraudulent messages designed to trick a person into revealing sensitive information or installing malware."},
    {"title": "Ransomware", "text": "Ransomware is malware that encrypts a victim's files and demands payment, usually in cryptocurrency, in exchange for the decryption key."},
    {"title": "Zero-day", "text": "A zero-day is a software vulnerability unknown to the vendor, for which no patch yet exists, leaving systems exposed until one is released."},
    {"title": "Multi-factor authentication", "text": "Multi-factor authentication (MFA) requires two or more independent factors to verify identity, such as a password plus a one-time code from a phone."},
    {"title": "Least privilege", "text": "The principle of least privilege means giving each user or process only the access strictly required to do its job, and no more."},
    {"title": "SIEM", "text": "A Security Information and Event Management (SIEM) system collects and correlates logs from across an organization to detect and investigate security incidents."},
    {"title": "Defense in depth", "text": "Defense in depth is a strategy of layering multiple, independent security controls so that if one fails, others still protect the system."},
    {"title": "SQL injection", "text": "SQL injection is an attack that inserts malicious SQL into an application's query, letting an attacker read or modify a database they should not access."},
    {"title": "Patch management", "text": "Patch management is the process of regularly identifying, testing, and applying software updates to fix security vulnerabilities."},
    {"title": "Incident response", "text": "Incident response is the organized approach to detecting, containing, eradicating, and recovering from a cybersecurity incident, followed by lessons learned."},
    # --- Fictional / proprietary facts: only RAG can know these ---
    {"title": "Redlake University password policy", "text": "Redlake University requires all account passwords to be at least 16 characters long and rotated every 180 days. Reuse of the last 10 passwords is prohibited."},
    {"title": "Redlake University SOC hours", "text": "The Redlake University Security Operations Center (SOC) is staffed 24/7, and all suspected incidents must be reported to soc@redlake.example within 30 minutes of discovery."},
    {"title": "Redlake VPN requirement", "text": "Remote access to Redlake University systems requires the GlobalGuard VPN client and a hardware security key; software one-time codes are not accepted for VPN login."},
]

with open(ARTIFACTS / "corpus.json", "w", encoding="utf-8") as f:
    json.dump(CORPUS, f, indent=2)
print(f"Saved {len(CORPUS)} corpus entries to {ARTIFACTS/'corpus.json'}")''')

md(c, r"""## The fixed test questions
The same questions go to every approach in Notebook 04. They're chosen so each one *exposes* a
difference — note the **"who should win"** column.""")
code(c, r'''TEST_PROMPTS = [
    {"type": "corpus fact",     "q": "What is Redlake University's password policy?",            "win": "RAG (it's a private fact no model was trained on)"},
    {"type": "corpus fact",     "q": "How quickly must incidents be reported at Redlake, and to whom?", "win": "RAG"},
    {"type": "general fact",    "q": "What is phishing?",                                        "win": "Base/tune/RAG all OK (common knowledge)"},
    {"type": "format/behavior", "q": "Define 'least privilege' in one sentence for a beginner.",  "win": "Fine-tuned (learned the style)"},
    {"type": "reasoning",       "q": "A new employee reuses one short password everywhere. Which two ideas from security best practice would help, and why?", "win": "Larger/instruct models; shows reasoning"},
    {"type": "out-of-scope",    "q": "Write a haiku about the ocean.",                            "win": "Base/instruct (shows specialization trade-offs)"},
]

with open(ARTIFACTS / "test_prompts.json", "w", encoding="utf-8") as f:
    json.dump(TEST_PROMPTS, f, indent=2)
print(f"Saved {len(TEST_PROMPTS)} test prompts.")
for p in TEST_PROMPTS:
    print(f"  [{p['type']:14}] {p['q']}")''')

md(c, r"""✅ **Setup done.** The corpus and test prompts are saved in `artifacts/`. Next:
- **Instructor:** run **01 (train)** and **02 (fine-tune)** on a GPU, then **03 (RAG)**.
- **Students:** once the instructor shares the `artifacts/` folder, jump to **04 (compare)**.""")
write(c, "00_Setup_and_Ingredients.ipynb")

# ============================================================ 01 TRAIN
c = nb_new()
md(c, r"""# 01 · Train a Model From Scratch  *(Instructor · GPU)*

**Approach 1 of 3.** Here we build a language model's "brain" **from zero** — random weights — and let
it learn *only* from our small corpus.

> **Set expectations honestly:** a real model is trained on *trillions* of words using enormous compute.
> We have a tiny corpus and one GPU, so our from-scratch model will be **small and not very good.**
> **That weakness is the lesson:** training from scratch needs huge data and compute. This is *why*,
> in practice, we almost always start from a pretrained model (Notebook 02) or use RAG (Notebook 03).""")

code(c, r'''import json, math, torch
from pathlib import Path
from transformers import (AutoTokenizer, GPT2Config, GPT2LMHeadModel,
                          Trainer, TrainingArguments, DataCollatorForLanguageModeling)
from datasets import Dataset

ARTIFACTS = Path("artifacts")
BASE_MODEL = "Qwen/Qwen3-1.7B"
device = "cuda" if torch.cuda.is_available() else "cpu"
print("Device:", device)

corpus = json.load(open(ARTIFACTS / "corpus.json"))
texts = [f"{e['title']}: {e['text']}" for e in corpus]
print(f"{len(texts)} documents to train on (this is TINY — that's the point).")''')

md(c, r"""### A small, randomly-initialized model
We borrow the base model's tokenizer (so words map to numbers the same way), but the model itself is
a **fresh, small GPT-style network with random weights** — it knows nothing yet.""")
code(c, r'''tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

config = GPT2Config(vocab_size=len(tokenizer), n_positions=256,
                    n_embd=256, n_layer=4, n_head=4)   # deliberately small
model = GPT2LMHeadModel(config).to(device)
print(f"From-scratch model: {model.num_parameters()/1e6:.1f}M random parameters")''')

code(c, r'''def tok(batch):
    return tokenizer(batch["text"], truncation=True, max_length=256)

ds = Dataset.from_dict({"text": texts}).map(tok, batched=True, remove_columns=["text"])
collator = DataCollatorForLanguageModeling(tokenizer, mlm=False)

args = TrainingArguments(output_dir=str(ARTIFACTS / "_scratch_train"),
                         num_train_epochs=40, per_device_train_batch_size=4,
                         learning_rate=3e-4, logging_steps=10, report_to=[],
                         save_strategy="no")
trainer = Trainer(model=model, args=args, train_dataset=ds, data_collator=collator)
trainer.train()

model.save_pretrained(ARTIFACTS / "scratch_model")
tokenizer.save_pretrained(ARTIFACTS / "scratch_model")
print("Saved from-scratch model to", ARTIFACTS / "scratch_model")''')

md(c, r"""### See what it learned (don't expect much!)
It has only ever seen our tiny corpus, so it produces security-*flavored* text — but it's wobbly and
makes things up. That's expected for a model this small trained on so little.""")
code(c, r'''def scratch_generate(prompt, max_new_tokens=40):
    ids = tokenizer(prompt, return_tensors="pt").to(device)
    out = model.generate(**ids, max_new_tokens=max_new_tokens, do_sample=True,
                         top_k=40, pad_token_id=tokenizer.pad_token_id)
    return tokenizer.decode(out[0], skip_special_tokens=True)

print(scratch_generate("Phishing is"))
print("---")
print(scratch_generate("Multi-factor authentication"))''')

md(c, r"""**Takeaway:** training from scratch = the model learns *everything* from your data. With little
data and compute, results are weak. In Notebook 02 we'll start from a model that already understands
language and just *adapt* it — far cheaper and far better.""")
write(c, "01_Train_From_Scratch.ipynb")

# ============================================================ 02 FINETUNE
c = nb_new()
md(c, r"""# 02 · Fine-Tune a Model (LoRA)  *(Instructor · GPU)*

**Approach 2 of 3.** Instead of starting from zero, we take a model that **already understands
language** and gently **adapt** it to answer in our style/format, using our corpus.

We use **LoRA** (Low-Rank Adaptation) — it trains a tiny set of extra weights (an "adapter") instead
of the whole model. That's why fine-tuning fits on one GPU and the result we share is only a few MB.

> **What fine-tuning is good at:** new **behavior, tone, and format.** It's *less* reliable for
> injecting brand-new facts — for that, you'll want RAG (Notebook 03).""")

code(c, r'''import json, torch
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import LoraConfig, get_peft_model
from datasets import Dataset

ARTIFACTS = Path("artifacts")
BASE_MODEL = "Qwen/Qwen3-1.7B"
device = "cuda" if torch.cuda.is_available() else "cpu"
corpus = json.load(open(ARTIFACTS / "corpus.json"))
print("Device:", device, "| corpus entries:", len(corpus))''')

md(c, r"""### Build a small instruction dataset from the corpus
Fine-tuning learns from **examples of the behavior we want** — here, concise Q&A in a consistent style.""")
code(c, r'''def example(entry):
    return {"messages": [
        {"role": "user", "content": f"Define '{entry['title']}' clearly and concisely."},
        {"role": "assistant", "content": entry["text"]},
    ]}

train_ds = Dataset.from_list([example(e) for e in corpus])
print("Training examples:", len(train_ds))
print(train_ds[0]["messages"])''')

code(c, r'''tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

def to_text(ex):
    # Render each chat example with the model's template into one training string.
    return {"text": tokenizer.apply_chat_template(ex["messages"], tokenize=False,
                                                  add_generation_prompt=False)}
train_text = train_ds.map(to_text, remove_columns=["messages"])
print(train_text[0]["text"][:300])''')

code(c, r'''from trl import SFTTrainer, SFTConfig

model = AutoModelForCausalLM.from_pretrained(BASE_MODEL, torch_dtype="auto").to(device)
lora = LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, bias="none",
                  task_type="CAUSAL_LM",
                  target_modules=["q_proj", "k_proj", "v_proj", "o_proj"])

sft_args = SFTConfig(output_dir=str(ARTIFACTS / "_lora_train"),
                     num_train_epochs=10, per_device_train_batch_size=2,
                     learning_rate=2e-4, logging_steps=5, report_to=[],
                     dataset_text_field="text", max_seq_length=512, save_strategy="no")
trainer = SFTTrainer(model=model, args=sft_args, train_dataset=train_text, peft_config=lora)
trainer.train()

trainer.model.save_pretrained(ARTIFACTS / "lora_adapter")
tokenizer.save_pretrained(ARTIFACTS / "lora_adapter")
print("Saved LoRA adapter (small!) to", ARTIFACTS / "lora_adapter")''')

md(c, r"""### Optional: share the adapter on Hugging Face
The adapter is only a few MB — perfect for sharing. Set `HF_REPO` in Notebook 00 and log in first
(`huggingface-cli login`). Skipped if `HF_REPO` is None.""")
code(c, r'''HF_REPO = None  # e.g. "your-org/ttr-demo-lora"
if HF_REPO:
    trainer.model.push_to_hub(HF_REPO)
    tokenizer.push_to_hub(HF_REPO)
    print("Pushed adapter to", HF_REPO)
else:
    print("Skipped HF upload (HF_REPO is None). Share the artifacts/ folder instead.")''')

md(c, r"""**Takeaway:** fine-tuning reused everything the base model already knew about language and just
taught it our *style*. It cost a fraction of training from scratch and the shareable result is tiny.
But notice we taught **behavior**, not new facts — for the private Redlake facts, we need RAG.""")
write(c, "02_FineTune_LoRA.ipynb")

# ============================================================ 03 RAG
c = nb_new()
md(c, r"""# 03 · Retrieval-Augmented Generation (RAG)  *(CPU ok)*

**Approach 3 of 3.** Here we change **nothing** in the model. Instead, at question time we **look up
the most relevant documents** from our corpus and hand them to the model as context.

> **What RAG is good at:** new, changing, or **private facts** — exactly the Redlake University
> policies that no pretrained model could know. The model's weights never change; we just give it the
> right reading material at the right moment.""")

code(c, r'''import json, numpy as np, torch
from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss

ARTIFACTS = Path("artifacts")
corpus = json.load(open(ARTIFACTS / "corpus.json"))
docs = [f"{e['title']}: {e['text']}" for e in corpus]
print(len(docs), "documents to index")''')

md(c, r"""### Build the search index (embeddings + FAISS)
We turn each document into a vector ("embedding") that captures its meaning, then store them in a
FAISS index so we can find the closest documents to any question.""")
code(c, r'''embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
emb = embedder.encode(docs, normalize_embeddings=True).astype("float32")
index = faiss.IndexFlatIP(emb.shape[1])
index.add(emb)

faiss.write_index(index, str(ARTIFACTS / "rag.faiss"))
np.save(ARTIFACTS / "rag_docs.npy", np.array(docs, dtype=object))
print("Saved RAG index to", ARTIFACTS / "rag.faiss")''')

md(c, r"""### Retrieve + answer
Given a question, find the top matching documents, put them in the prompt, and ask the instruct model
to answer **using only that context.**""")
code(c, r'''from transformers import AutoTokenizer, AutoModelForCausalLM

BASE_MODEL = "Qwen/Qwen3-1.7B"
device = "cuda" if torch.cuda.is_available() else "cpu"
tok = AutoTokenizer.from_pretrained(BASE_MODEL)
model = AutoModelForCausalLM.from_pretrained(BASE_MODEL, torch_dtype="auto").to(device)

def retrieve(question, k=3):
    q = embedder.encode([question], normalize_embeddings=True).astype("float32")
    scores, idx = index.search(q, k)
    return [docs[i] for i in idx[0]]

def rag_answer(question, k=3, max_new_tokens=200):
    context = "\n".join(f"- {d}" for d in retrieve(question, k))
    msgs = [{"role": "user", "content":
             f"Use ONLY the context to answer. If it's not in the context, say so.\n\n"
             f"Context:\n{context}\n\nQuestion: {question} /no_think"}]
    prompt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True,
                                     enable_thinking=False)
    ids = tok(prompt, return_tensors="pt").to(device)
    out = model.generate(**ids, max_new_tokens=max_new_tokens, do_sample=False)
    return tok.decode(out[0][ids["input_ids"].shape[1]:], skip_special_tokens=True).strip()

# A private fact only the corpus knows — RAG nails it; a plain model could not.
print(rag_answer("What is Redlake University's password policy?"))''')

md(c, r"""**Takeaway:** no training at all — RAG answered a **private fact** correctly just by retrieving it.
That's its superpower: new and changing knowledge, with the model untouched. The trade-off is that it
only knows what's in the corpus, and answers depend on retrieving the right documents.""")
write(c, "03_RAG.ipynb")

# ============================================================ 04 COMPARE
c = nb_new()
md(c, r"""# 04 · Compare Them Head-to-Head  *(Students · CPU ok)*

This is the payoff. We send the **same questions** to four setups and read the answers side by side:

1. **Base** — the instruct model with no help
2. **From scratch** — the tiny model from Notebook 01
3. **Fine-tuned** — base + the LoRA adapter from Notebook 02
4. **RAG** — base + retrieval from Notebook 03

> **Before you run:** make sure you have the `artifacts/` folder the instructor shared (it holds the
> trained model, the LoRA adapter, the RAG index, the corpus, and the test prompts). This runs on CPU.""")

code(c, r'''import json, numpy as np, torch
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
from sentence_transformers import SentenceTransformer
import faiss

ARTIFACTS = Path("artifacts")
BASE_MODEL = "Qwen/Qwen3-1.7B"
device = "cuda" if torch.cuda.is_available() else "cpu"
prompts = json.load(open(ARTIFACTS / "test_prompts.json"))
print("Device:", device, "| test prompts:", len(prompts))''')

md(c, r"""### Load everything (one base model, shared to save memory)
We load the instruct model once and attach the LoRA adapter to it; turning the adapter on/off gives us
both the **base** and the **fine-tuned** answers from a single copy in memory.""")
code(c, r'''tok = AutoTokenizer.from_pretrained(BASE_MODEL)
base = AutoModelForCausalLM.from_pretrained(BASE_MODEL, torch_dtype="auto").to(device)
tuned = PeftModel.from_pretrained(base, str(ARTIFACTS / "lora_adapter"))  # adapter on top of base

# From-scratch tiny model
scratch_tok = AutoTokenizer.from_pretrained(ARTIFACTS / "scratch_model")
scratch = AutoModelForCausalLM.from_pretrained(ARTIFACTS / "scratch_model").to(device)

# RAG index
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
index = faiss.read_index(str(ARTIFACTS / "rag.faiss"))
docs = list(np.load(ARTIFACTS / "rag_docs.npy", allow_pickle=True))
print("All four setups loaded.")''')

code(c, r'''def chat(model, question, max_new_tokens=160):
    msgs = [{"role": "user", "content": question + " /no_think"}]
    prompt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True,
                                     enable_thinking=False)
    ids = tok(prompt, return_tensors="pt").to(device)
    out = model.generate(**ids, max_new_tokens=max_new_tokens, do_sample=False)
    return tok.decode(out[0][ids["input_ids"].shape[1]:], skip_special_tokens=True).strip()

def answer_base(q):
    with tuned.disable_adapter():     # adapter off => plain base model
        return chat(tuned, q)

def answer_tuned(q):
    return chat(tuned, q)             # adapter on => fine-tuned

def answer_scratch(q, n=40):
    ids = scratch_tok(q, return_tensors="pt").to(device)
    out = scratch.generate(**ids, max_new_tokens=n, do_sample=True, top_k=40,
                           pad_token_id=scratch_tok.eos_token_id)
    return scratch_tok.decode(out[0], skip_special_tokens=True)

def answer_rag(q, k=3):
    qv = embedder.encode([q], normalize_embeddings=True).astype("float32")
    ctx = "\n".join(f"- {docs[i]}" for i in index.search(qv, k)[1][0])
    with tuned.disable_adapter():     # RAG on the plain base model (no fine-tuning)
        return chat(tuned, f"Use ONLY this context; if it's not there, say so.\n"
                           f"Context:\n{ctx}\n\nQuestion: {q}")
print("Answer functions ready.")''')

md(c, r"""### Run the comparison
For each test question, see all four answers and the note on **who should win**.""")
code(c, r'''for p in prompts:
    print("=" * 100)
    print(f"Q [{p['type']}]: {p['q']}")
    print(f"(expected to favor: {p['win']})\n")
    print("BASE        :", answer_base(p["q"])[:300]); print()
    print("FINE-TUNED  :", answer_tuned(p["q"])[:300]); print()
    print("RAG         :", answer_rag(p["q"])[:300]); print()
    print("FROM-SCRATCH:", answer_scratch(p["q"])[:200]); print()''')

md(c, r"""## What you should notice
| Question type | Winner | Why |
|---|---|---|
| Private "Redlake" facts | **RAG** | Only RAG can see facts no model was trained on |
| Common definitions | Base / tuned / RAG | All know common knowledge |
| Specific format/style | **Fine-tuned** | It learned the house style |
| From-scratch, anything | (loses) | Too little data/compute — shows why we rarely train from scratch |

### The decision rule to remember
- **New or changing facts?** → **RAG**
- **New behavior, tone, or format?** → **Fine-tune**
- **A brand-new capability from nothing?** → **Train** (expensive — usually not worth it)

Same base model, same knowledge, three very different tools. Pick the one that matches your problem.""")
write(c, "04_Compare.ipynb")

print("\nAll notebooks generated.")
