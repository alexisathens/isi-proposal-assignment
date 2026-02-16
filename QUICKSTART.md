# Quick Start Guide

This guide walks you through running the IPS Reviewer Assignment System from scratch in under 10 minutes.

## Before You Start

**What you need:**
- Python 3.7+ installed
- Your CSV data files ready
- 15-30 minutes (depending on dataset size)

## Step-by-Step Instructions

### 1. Install Ollama

**Download and install:**
- Go to [https://ollama.ai/](https://ollama.ai/)
- Download for your platform (Windows/Mac/Linux)
- Run the installer

**Start Ollama:**
```bash
ollama serve
```

Keep this terminal window open.

**Download the embedding model** (in a new terminal):
```bash
ollama pull nomic-embed-text
```

This downloads ~275MB. Wait for completion.

### 2. Set Up Python Environment

**Navigate to project:**
```bash
cd isi-proposal-assignment
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Configure environment (optional):**
```bash
# On Windows
copy .env.example .env

# On Mac/Linux
cp .env.example .env
```

If using a remote Ollama server, edit `.env` and change `OLLAMA_HOST`.

### 3. Prepare Your Data

**Place CSV files in the `Input/` folder:**
```
Input/
├── proposals.csv
├── descriptions.csv
└── members.csv
```

**Required format:**
- **Delimiter**: Semicolon (`;`)
- **Encoding**: Latin-1
- See [README.md](README.md#input-file-formats) for column requirements

**Example proposals.csv:**
```csv
Proposal ID;Title;Association
1;My Proposal Title;BS
2;Another Proposal;IAOS
```

**Example members.csv:**
```csv
ID;Members;Association;Expertise
15;John Smith;BS;Statistics and data science
7;Jane Doe;IAOS;Survey methodology
```

**Example descriptions.csv:**
```csv
Proposal ID;Brief Description;WSC Proposal Description
1;Short summary;Detailed description here
```

### 4. Run the Pipeline

**Step 1: Generate proposal embeddings**
```bash
python Scripts/embed_proposals.py \
  --proposals Input/proposals.csv \
  --descriptions Input/descriptions.csv \
  --out Intermediate/proposals_with_embeddings.json
```

⏱️ **Time**: ~1-2 seconds per proposal (e.g., 50 proposals = ~2 minutes)

✅ **Success looks like:**
```
✓ Connected to Ollama at http://localhost:11434
✓ Using model: nomic-embed-text
[1/50] Embedding proposal 1...
[2/50] Embedding proposal 2...
...
✓ Wrote 50 records to Intermediate/proposals_with_embeddings.json
```

**Step 2: Generate member embeddings**
```bash
python Scripts/embed_members.py \
  --members Input/members.csv \
  --out Intermediate/members_with_embeddings.json
```

⏱️ **Time**: ~1-2 seconds per member (e.g., 25 members = ~1 minute)

✅ **Success looks like:**
```
✓ Connected to Ollama at http://localhost:11434
✓ Using model: nomic-embed-text
[1/25] Embedding member 15...
[2/25] Embedding member 7...
...
✓ Wrote 25 records to Intermediate/members_with_embeddings.json
```

**Step 3: Assign reviewers**
```bash
python Scripts/assign_reviewers.py \
  --proposals Intermediate/proposals_with_embeddings.json \
  --members Intermediate/members_with_embeddings.json \
  --out assignment_results.xlsx
```

⏱️ **Time**: Instant (seconds)

✅ **Success looks like:**
```
=== Workload Calculation ===
Total proposals: 50
Total members: 25
Total reviews needed: 100
...
✓ All proposals have 2 reviewers!
✓ Assignments saved to assignment_results.xlsx
```

### 5. Review Results

**Open the Excel file:**
```
assignment_results.xlsx
```

**Three sheets:**
1. **By Proposal** - See which reviewers assigned to each proposal
2. **By Reviewer** - See workload for each reviewer
3. **Detailed Assignments** - Full expanded view

**Check the console statistics:**
- Are all proposals covered?
- Is workload distributed fairly?
- Are similarity scores reasonable (>0.5 is good)?

## Common First-Run Issues

### "Cannot connect to Ollama"
```bash
# Fix: Start Ollama in another terminal
ollama serve
```

### "Model not found"
```bash
# Fix: Download the model
ollama pull nomic-embed-text
```

### "No module named 'backoff'"
```bash
# Fix: Install dependencies
pip install -r requirements.txt
```

### "File not found: Input/proposals.csv"
```bash
# Fix: Make sure you're in the right directory
cd isi-proposal-assignment

# Fix: Check files exist
ls Input/
```

### Script interrupted midway
```bash
# No problem! Just rerun it - it skips already-embedded items
python Scripts/embed_proposals.py ...
```

## What If I Need to Rerun?

**All scripts are resumable:**
- Embedding scripts skip items that already have embeddings
- Safe to interrupt with Ctrl+C and restart
- Only new/modified items are processed

**To force re-embedding everything:**
```bash
# Delete the intermediate files
rm Intermediate/proposals_with_embeddings.json
rm Intermediate/members_with_embeddings.json

# Then rerun Steps 1 & 2
```

## Next Steps

- **Adjust assignments**: Edit CSV files and rerun
- **Try different model**: Change `IPS_EMBED_MODEL` in `.env` to `mxbai-embed-large`
- **Understand the algorithm**: Read [README.md](README.md#assignment-algorithm)
- **Troubleshoot issues**: See [README.md](README.md#troubleshooting)

## Time Estimates

For typical dataset sizes:

| Proposals | Members | Step 1 | Step 2 | Step 3 | Total |
|-----------|---------|--------|--------|--------|-------|
| 10        | 10      | ~20s   | ~20s   | <5s    | ~1min |
| 50        | 25      | ~2min  | ~1min  | <5s    | ~3min |
| 100       | 50      | ~4min  | ~2min  | ~10s   | ~6min |
| 500       | 100     | ~20min | ~5min  | ~30s   | ~25min|

*Times assume ~2s per embedding with `nomic-embed-text` on standard hardware*

## Complete Example Session

Here's what a complete run looks like:

```bash
# Terminal 1: Start Ollama
$ ollama serve
# Leave running...

# Terminal 2: Run pipeline
$ cd isi-proposal-assignment
$ pip install -r requirements.txt
$ python Scripts/embed_proposals.py \
    --proposals Input/proposals.csv \
    --descriptions Input/descriptions.csv \
    --out Intermediate/proposals_with_embeddings.json
# Wait ~2 minutes...

$ python Scripts/embed_members.py \
    --members Input/members.csv \
    --out Intermediate/members_with_embeddings.json
# Wait ~1 minute...

$ python Scripts/assign_reviewers.py
# Instant!

# Open assignment_results.xlsx
$ open assignment_results.xlsx  # Mac
$ start assignment_results.xlsx  # Windows
$ xdg-open assignment_results.xlsx  # Linux
```

## Need Help?

- **Full documentation**: [README.md](README.md)
- **Detailed workflow**: `Documentation_of_the_assignment_flow_for_reviewers_to_papers.docx`
- **Input file specs**: [README.md - Input File Formats](README.md#input-file-formats)
- **Algorithm details**: [README.md - Assignment Algorithm](README.md#assignment-algorithm)

---

**Ready to start?** Go to [Step 1](#step-by-step-instructions) above!
