# ISI Proposal Assignment System

*Intelligent assignment of ISI World Statistics Congress proposals to Scientific Programme Committee reviewers*

The [International Statistical Institute (ISI)](https://isi-web.org/Global-ISI-Events) is a non-governmental organization dedicated to creating a better world through statistics and data science. Every two years, the ISI organizes the World Statistics Congress, a leading global forum for the exchange of statistical knowledge and methodological developments. Within the Congress, the Invited Paper Sessions (IPS) showcase innovative and highly relevant academic contributions.

To support the development of this programme, the ISI invites the statistical community to submit proposals for the IPS. These proposals are then reviewed by the Scientific Programme Committee (SPC), and the highest-rated papers are selected for presentation at the World Statistics Congress.

Given the large number of proposals submitted, this code supports the matching of IPS proposals to SPC reviewers by ensuring that each paper is assigned to at least two reviewers with the highest possible topical and methodological alignment. The Python workflow uses text embeddings to compare proposals and reviewer profiles. Text embeddings are numerical representations of text that capture meaning and context, allowing the code to measure semantic similarity beyond simple keyword matching. In practice, this means the system identifies reviewers whose expertise is conceptually aligned with a proposal even when different terminology is used. The output is an assignment sheet listing all papers and their corresponding most qualified reviewers.


## Table of Contents // review this

- [Overview](#overview)
- [System Workflow](#system-workflow)
- [Directory Structure](#directory-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Data Preparation Methodology](#data-preparation-methodology)
- [Usage](#usage)
  - [Step 1: Generate Proposal Embeddings](#step-1-generate-proposal-embeddings)
  - [Step 2: Generate Member Embeddings](#step-2-generate-member-embeddings)
  - [Step 3: Assign Reviewers](#step-3-assign-reviewers)
- [Assignment Algorithm](#assignment-algorithm)
- [Input File Formats](#input-file-formats)
- [Output](#output)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Overview

This system assigns reviewers to proposals following these key principles:

1. **Complete Association Coverage**: ALL reviewers from a specific association review ALL papers from that association
2. **Dual Review Requirement**: Every proposal receives exactly 2 reviewers
3. **Fair Workload Distribution**: Reviews are distributed as equitably as possible across all reviewers
4. **Similarity-Based Matching**: Uses embedding vectors to match proposals with reviewers based on expertise

## System Workflow

The assignment process consists of three sequential steps:

```
Input CSVs → [1] Embed Proposals → [2] Embed Members → [3] Assign Reviewers → Output Excel
```

1. **Embed Proposals**: Generates vector embeddings from proposal text (title, description, participants)
2. **Embed Members**: Generates vector embeddings from member expertise
3. **Assign Reviewers**: Matches proposals to reviewers using embeddings and association rules

## Directory Structure

```
isi-proposal-assignment/
├── Input/                          # Place your source CSV files here
│   ├── proposals.csv              # Proposal data
│   ├── members.csv                # Reviewer/member data
│   └── descriptions.csv           # Proposal descriptions
├── Intermediate/                   # Generated embedding files
│   ├── proposals_with_embeddings.json
│   └── members_with_embeddings.json
├── Scripts/                        # Python scripts
│   ├── embed_proposals.py         # Step 1: Generate proposal embeddings
│   ├── embed_members.py           # Step 2: Generate member embeddings
│   └── assign_reviewers.py        # Step 3: Assign reviewers
├── requirements.txt               # Python dependencies
├── .env.example                   # Configuration template
└── README.md                      # This file
```

## Prerequisites

### 1. Python Environment
- **Python 3.7 or higher**
- pip (Python package installer)

### 2. Ollama Server
The embedding scripts use [Ollama](https://ollama.ai/) to generate text embeddings locally.

**Installation:**
- Visit [https://ollama.ai/](https://ollama.ai/) and download Ollama
- Follow installation instructions for your platform
- Start Ollama server: `ollama serve`

**Download Embedding Model:**
```bash
ollama pull nomic-embed-text
```

Alternative models you can use:
- `mxbai-embed-large` - Larger, more accurate
- `all-minilm` - Smaller, faster

### 3. Network Access
- If using a remote Ollama server, ensure network connectivity to the server

## Installation

### 1. Clone or Download Repository
```bash
cd isi-proposal-assignment
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `openpyxl` - Excel file generation
- `backoff` - API retry logic
- `requests` - HTTP requests for Ollama API

### 3. Configure Environment
Copy the example configuration file:
```bash
cp .env.example .env
```

Edit `.env` with your settings:
```bash
# Default: local Ollama instance
OLLAMA_HOST=http://localhost:11434

# Or: remote Ollama server
# OLLAMA_HOST=http://10.0.9.83:11434

# Embedding model (must be pulled first)
IPS_EMBED_MODEL=nomic-embed-text

# API rate limiting (seconds between requests)
IPS_EMBED_SLEEP_SEC=0.5
```

**Note**: The scripts will read these environment variables. Alternatively, you can set them in your shell:
```bash
export OLLAMA_HOST=http://localhost:11434
export IPS_EMBED_MODEL=nomic-embed-text
```

### 4. Verify Ollama Connection
Test that Ollama is accessible:
```bash
curl http://localhost:11434/api/tags
```

You should see a JSON response listing available models.

## Configuration

### Supported Associations

The system recognizes these associations:
- BS, IAOS, IASC, IASE, IASS, IFC, ISBIS, ISI, KOSTAT, TIES, Women, Young

Proposals or members without these associations are categorized as "Other".

**Note**: Association names are **case-sensitive** and must match exactly between proposals and members.

### File Encoding

Input CSV files use:
- **Delimiter**: Semicolon (`;`)
- **Encoding**: Latin-1 (ISO-8859-1)

## Data Preparation Methodology

This section describes the recommended approach for preparing your input data files, based on the original implementation workflow.

### Gathering Member/Reviewer Information

**Building Reviewer Profiles:**

1. **Start with a member list** containing names and associations
2. **Research each member's expertise** using:
   - Personal/institutional webpages with biographical descriptions
   - Publication titles and abstracts (if no webpage available)
   - Professional profiles (ResearchGate, LinkedIn, university pages)
3. **Extract keywords** that represent their expertise areas
4. **Compile into structured format** with four columns:
   - ID - Unique identifier
   - Members - Full name
   - Association - Association affiliation
   - Expertise - Expertise description

**Expertise Field Best Practices:**

- **Use commas to separate concepts**: This helps the embedding model interpret distinct topics
  - ✅ Good: `Bayesian statistics, time series analysis, machine learning, causal inference`
  - ❌ Less effective: `Bayesian statistics and time series analysis using machine learning for causal inference`
- **Remove excess punctuation**: Clean the text of special characters that don't add meaning
- **Include specific methodologies**: Not just broad areas (e.g., "spatial statistics" vs "statistics")
- **Mention application domains**: Fields where expertise is applied (climate, health, economics, etc.)
- **Use consistent formatting**: Apply the same style across all member entries

**Example Member Entry:**
```csv
15;Sebastian Engelke;BS;Extreme value theory, graphical models, weather forecasting with AI, statistical climate science, causal inference methods
```

### Gathering Proposal Information

**Building Proposal Dataset:**

1. **Collect proposal data** including:
   - Unique identifiers
   - Titles
   - Author information
   - Abstracts or descriptions
   - Association affiliations
2. **Combine relevant text fields**: Title + abstract for better embedding context
3. **Structure into CSV files**:
   - `proposals.csv` - Basic info (ID, Title, Association)
   - `descriptions.csv` - Text content (ID, Brief Description, Full Description)

**Text Formatting Guidelines:**

- **Preserve natural language**: Keep descriptions readable
- **Remove excessive formatting**: Strip HTML tags, extra whitespace, special encoding
- **Maintain key information**: Don't over-clean; technical terms and phrases are valuable
- **Consistent delimiters**: Use semicolons to separate CSV fields

### Why Ollama and nomic-embed-text?

**Tool Selection Rationale:**

- **Open Source**: Freely available, no API costs or usage limits
- **Local Deployment**: Runs on your infrastructure, no data sent to external services
- **Privacy**: Sensitive proposal and member data stays within your organization
- **Quality**: The `nomic-embed-text` model provides good semantic understanding for this use case
- **Flexibility**: Can be deployed on organizational servers (e.g., CEPAL infrastructure)

**Alternative Options:**

If your organization has existing infrastructure:
- **OpenAI API**: Higher quality embeddings but requires paid API access and data leaves your network
- **Other Ollama models**: `mxbai-embed-large` for better accuracy, `all-minilm` for speed
- **Sentence Transformers**: Can be integrated with minor code modifications

### The Three-Script Pipeline

**Overview of the workflow:**

1. **Embedding Members** (`embed_members.py`):
   - Reads `members.csv`
   - Generates vector embeddings from expertise text
   - Creates `members_with_embeddings.json`

2. **Embedding Proposals** (`embed_proposals.py`):
   - Reads `proposals.csv` and `descriptions.csv`
   - Combines text fields (title + description)
   - Generates vector embeddings
   - Creates `proposals_with_embeddings.json`

3. **Assigning Reviewers** (`assign_reviewers.py`):
   - Loads both JSON files with embeddings
   - Implements two-round assignment algorithm:
     - **Round 1**: Association-based matching (all members from association X review all proposals from association X)
     - **Round 2**: Similarity-based completion (ensures every proposal gets exactly 2 reviewers)
   - Balances workload across all reviewers
   - Generates Excel output with assignments

### Data Quality Tips

**For Best Results:**

1. **Comprehensive Expertise**: More detailed expertise descriptions lead to better matches
2. **Accurate Associations**: Ensure association codes match exactly between proposals and members
3. **Complete Descriptions**: Fuller proposal descriptions improve similarity calculations
4. **Consistent Formatting**: Apply same text cleaning rules to all entries
5. **Review Embeddings**: Check that generated embeddings are non-zero and have reasonable dimensionality

**Common Issues to Avoid:**

- Empty expertise fields (members will match poorly)
- Association mismatches (members won't be matched to relevant proposals)
- Missing proposals from member associations (some members will have very low workload)
- Overly brief descriptions (similarity scores will be less reliable)

## Usage

### Step 1: Generate Proposal Embeddings

Converts proposal CSV files into embeddings.

**Input Files** (place in `Input/` folder):
- `proposals.csv` - Basic proposal info
- `descriptions.csv` - Proposal descriptions
- `members.csv` - Proposal participants (optional)

**Run:**
```bash
python Scripts/embed_proposals.py \
  --proposals Input/proposals.csv \
  --descriptions Input/descriptions.csv \
  --out Intermediate/proposals_with_embeddings.json
```

**What it does:**
- Reads proposal data from CSVs
- Combines title, description, and participant info into text
- Generates embeddings using Ollama
- Saves to `Intermediate/proposals_with_embeddings.json`
- **Resumes**: Skips already-embedded proposals (can restart safely)

**Progress Output:**
```
✓ Connected to Ollama at http://localhost:11434
✓ Using model: nomic-embed-text
[1/50] Embedding proposal P001...
[2/50] Embedding proposal P002...
...
✓ Wrote 50 records to Intermediate/proposals_with_embeddings.json
```

### Step 2: Generate Member Embeddings

Converts member/reviewer CSV into embeddings.

**Input Files** (place in `Input/` folder):
- `members.csv` - Reviewer information and expertise

**Run:**
```bash
python Scripts/embed_members.py \
  --members Input/members.csv \
  --out Intermediate/members_with_embeddings.json
```

**What it does:**
- Reads member data from CSV
- Generates embeddings from expertise field
- Saves to `Intermediate/members_with_embeddings.json`
- **Resumes**: Skips already-embedded members (can restart safely)

**Progress Output:**
```
✓ Connected to Ollama at http://localhost:11434
✓ Using model: nomic-embed-text
[1/25] Embedding member M001...
[2/25] Embedding member M002...
...
✓ Wrote 25 records to Intermediate/members_with_embeddings.json
```

### Step 3: Assign Reviewers

Matches proposals to reviewers using embeddings and association rules.

**Input Files** (from Step 1 & 2):
- `Intermediate/proposals_with_embeddings.json`
- `Intermediate/members_with_embeddings.json`

**Run:**
```bash
python Scripts/assign_reviewers.py \
  --proposals Intermediate/proposals_with_embeddings.json \
  --members Intermediate/members_with_embeddings.json \
  --out assignment_results.xlsx
```

**Shorthand** (uses default paths):
```bash
python Scripts/assign_reviewers.py
```

**What it does:**
- Loads embeddings from JSON files
- Calculates cosine similarity between all proposal-member pairs
- Assigns reviewers following the algorithm (see below)
- Generates Excel file with three worksheets
- Prints detailed statistics

**Progress Output:**
```
=== Workload Calculation ===
Total proposals: 50
Total members: 25
Total reviews needed: 100
Base reviews per member: 4

=== ROUND 1: Association-based Assignment ===
BS: 5 proposal(s), 3 member(s)
  ✓ Proposal P001 → John Smith (BS) [sim=0.856]
  ...

=== Round 2 Complete ===
✓ All proposals have 2 reviewers!

=== Final Workload Distribution ===
Min: 3 | Max: 5 | Avg: 4.0

✓ Assignments saved to assignment_results.xlsx
```

## Assignment Algorithm

### Round 1A: Association-Based Assignment

**Rule**: ALL members from an association review ALL proposals from that association.

- For each specific association (BS, IAOS, etc.):
  - Every member from that association is assigned to every proposal from that association
  - Ensures complete coverage and domain expertise
  - Example: 5 BS members × 10 BS proposals = 50 assignments

### Round 1B: "Other" Category Assignment

**Rule**: Proposals with "Other" association get their first reviewer.

- Uses embedding similarity scores
- Balances similarity with fairness (prefers reviewers with lower workload)
- Scoring formula: `similarity - (current_workload × 0.1)`

### Round 2: Completion Phase

**Rule**: Ensure every proposal has exactly 2 reviewers.

- Iteratively assigns second reviewers to proposals with fewer than 2
- Selection criteria (in order):
  1. Not already assigned to this proposal
  2. Lowest current workload (fairest distribution)
  3. Highest similarity score (when workload is equal)

### Workload Balancing

Target workload is calculated as:
```
total_reviews_needed = num_proposals × 2
base_reviews_per_member = total_reviews_needed ÷ num_members
extra_reviews = total_reviews_needed % num_members
```

Result: Most members get `base` reviews, some get `base + 1` to cover the remainder.

## Input File Formats

### proposals.csv
```csv
Proposal ID;Title;Association
1;Statistical Methods for AI;BS
2;Data Quality Standards;IAOS
```

**Required Columns:**
- `Proposal ID` - Unique identifier
- `Title` - Proposal title
- `Association` - Association code (BS, IAOS, etc.)

### descriptions.csv
```csv
Proposal ID;Brief Description;WSC Proposal Description
1;Summary text here;Detailed description here
```

**Required Columns:**
- `Proposal ID` - Must match proposals.csv
- `Brief Description` - Short summary
- `WSC Proposal Description` - Full description

### members.csv
```csv
ID;Members;Association;Expertise
15;John Smith;BS;Bayesian statistics, time series analysis
7;Jane Doe;IAOS;Survey methodology, data quality
```

**Required Columns:**
- `ID` - Unique member identifier
- `Members` - Member name
- `Association` - Association code
- `Expertise` - Text describing expertise (used for embeddings)

**Notes:**
- All files use **semicolon (;)** as delimiter
- Encoding: **Latin-1** (ISO-8859-1)
- Missing associations default to "Other"

## Output

### Excel File Structure

The assignment script generates an Excel file with three worksheets:

#### Sheet 1: By Proposal

One row per proposal with up to 2 reviewers.

**Columns:**
- Proposal ID, Title, Description, Category, Association
- Reviewer 1 ID, Name, Association, Expertise, Similarity Score
- Reviewer 2 ID, Name, Association, Expertise, Similarity Score

#### Sheet 2: By Reviewer

One row per reviewer showing their workload.

**Columns:**
- Reviewer ID, Name, Association, Expertise
- Number of Proposals
- Proposal IDs (comma-separated list)
- Proposal Associations (comma-separated list)
- Average Similarity Score

#### Sheet 3: Detailed Assignments

One row per proposal-reviewer pair (expanded view).

**Columns:**
- All proposal details
- All reviewer details
- Similarity score

**Formatting:**
- Blue headers with white text
- Frozen header rows
- Auto-adjusted column widths
- Border styling
- Sorted by Association and Proposal ID

### Statistics Output

Console output includes:

**Proposal Coverage:**
- Count of proposals with 0, 1, 2, or >2 reviewers
- Total assignments made

**Reviewer Workload:**
- Min, max, and average proposals per reviewer
- Distribution histogram (how many reviewers have N proposals)
- List of reviewers above/below target

**Similarity Scores:**
- Average, min, and max similarity scores across all assignments
- Helps assess match quality

**Example:**
```
=== Assignment Statistics ===

Proposal coverage:
  Proposals with 0 reviewers: 0
  Proposals with 1 reviewer: 0
  Proposals with 2 reviewers: 50
  Total assignments: 100

Reviewer workload:
  Min proposals per reviewer: 3
  Max proposals per reviewer: 5
  Average proposals per reviewer: 4.0

  Workload distribution:
    10 reviewers have 3 proposal(s)
    12 reviewers have 4 proposal(s)
    3 reviewers have 5 proposal(s)

Similarity scores:
  Average: 0.742
  Min: 0.421
  Max: 0.956
```

## Troubleshooting

### Embedding Scripts (Steps 1 & 2)

**Cannot connect to Ollama**
```
RuntimeError: Cannot connect to Ollama at http://localhost:11434
```
- **Fix**: Ensure Ollama is running: `ollama serve`
- **Fix**: Check `OLLAMA_HOST` environment variable points to correct server
- **Fix**: Verify network connectivity if using remote server

**Model not found**
```
RuntimeError: Model nomic-embed-text not available
```
- **Fix**: Pull the model: `ollama pull nomic-embed-text`
- **Fix**: List available models: `ollama list`
- **Fix**: Update `IPS_EMBED_MODEL` to use available model

**Script stops midway**
- **Resume**: The scripts skip already-embedded items, just rerun
- **Check**: Ollama server may have crashed, restart with `ollama serve`

**Encoding errors reading CSV**
- **Fix**: Ensure files are Latin-1 encoded
- **Fix**: Check delimiter is semicolon (`;`)

### Assignment Script (Step 3)

**No assignments for certain proposals**
- **Check**: Proposal associations match member associations **exactly** (case-sensitive)
- **Check**: Verify both proposals and members have embeddings
- **Check**: Ensure at least some members exist for each association

**Proposals have >2 reviewers**
- This happens when association members outnumber association proposals
- Round 1A assigns ALL association members to ALL association proposals
- **Expected behavior** for small associations

**Uneven workload distribution**
- Expected when `total_reviews ÷ num_reviewers` isn't a whole number
- Algorithm minimizes variance while respecting association rules
- Some members will have `base + 1` reviews

**Low similarity scores**
- May indicate embedding quality issues
- **Fix**: Regenerate embeddings with different model
- **Fix**: Check that expertise/description text is meaningful
- **Fix**: Ensure embeddings were generated correctly (not empty)

**File path errors**
- **Fix**: Run scripts from the repository root directory
- **Fix**: Use correct relative paths: `Intermediate/` not root directory
- **Fix**: Check that input files exist in expected locations

### General Issues

**Missing dependencies**
```
ModuleNotFoundError: No module named 'backoff'
```
- **Fix**: Install dependencies: `pip install -r requirements.txt`

**Permission errors**
- **Fix**: Ensure write permissions for `Intermediate/` and output directories
- **Fix**: Close Excel files before regenerating them

**Memory issues with large datasets**
- Embedding generation is done one-at-a-time to minimize memory usage
- Assignment script loads all data into memory
- For very large datasets (>10,000 proposals), consider batch processing

## Notes

- **Embeddings are cached**: Rerunning embedding scripts only processes new items
- **Cosine similarity**: Ranges from -1 to 1, where 1 is identical, 0 is orthogonal
- **Association matching**: Case-sensitive; "BS" ≠ "bs"
- **Resume capability**: All scripts can be safely interrupted and restarted
- **Idempotent**: Running scripts multiple times with same data produces same results

## License

Internal use only - ISI IPS Review System

---

**For questions or issues**, please contact the system maintainer.
