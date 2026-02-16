IPS Reviewer Assignment System

A Python script that intelligently assigns reviewers to IPS (Invited Paper Session) proposals using embedding-based similarity scoring and association-based rules.

Overview

This system assigns reviewers to proposals following these key principles:
1.	Complete Association Coverage: ALL reviewers from a specific association review ALL papers from that association
2.	Dual Review Requirement: Every proposal receives exactly 2 reviewers
3.	Fair Workload Distribution: Reviews are distributed as equitably as possible across all reviewers
4.	Similarity-Based Matching: Uses embedding vectors to match proposals with reviewers based on expertise
Requirements
•	Python 3.7+
•	Required packages: 
o	pandas
o	numpy
o	openpyxl
Install dependencies:
pip install pandas numpy openpyxl
Input Files
1. Proposals File (proposals_with_embeddings.json)
JSON file containing proposal data with the following fields:
•	Proposal ID: Unique identifier
•	Title: Proposal title
•	Description: Object containing Brief Description and WSC Proposal Description
•	Category: Proposal category
•	Association: Association affiliation (BS, IAOS, IASC, IASE, IASS, IFC, ISBIS, ISI, KOSTAT, TIES, Women, Young, or Other)
•	embedding: Vector representation of the proposal (list of floats)
2. Members File (members_with_embeddings.json)
JSON file containing reviewer data with the following fields:
•	ID: Unique identifier
•	Members: Reviewer name
•	Expertise: Area of expertise
•	Association: Association affiliation
•	embedding: Vector representation of expertise (list of floats)
Both files can also be CSV format (semicolon-separated, Latin-1 encoding).
Usage
Basic usage:
python ips_assign_reviewers.py
With custom file paths:
python ips_assign_reviewers.py \
  --proposals proposals_with_embeddings.json \
  --members members_with_embeddings.json \
  --out assignment_results.xlsx
Command-line Arguments
•	--proposals: Path to proposals file (default: proposals_with_embeddings.json)
•	--members: Path to members file (default: members_with_embeddings.json)
•	--out: Path to output Excel file (default: assignment_results.xlsx)
Assignment Algorithm
Round 1A: Association-Based Assignment
•	For each specific association (not "Other"): 
o	ALL members from that association are assigned to ALL proposals from that association
o	Ensures domain expertise and complete coverage
Round 1B: "Other" Category Assignment
•	Proposals with "Other" association are assigned to "Other" members
•	Uses embedding similarity scores with fairness balancing
•	Prioritizes members with lower current workloads
Round 2: Completion Phase
•	Ensures every proposal has exactly 2 reviewers
•	Assigns second reviewers based on: 
1.	Current workload (prioritizes reviewers with fewer assignments)
2.	Similarity scores (when workload is equal)
Output
The script generates an Excel file with three sheets:
Sheet 1: By Proposal
Each row contains:
•	Proposal information (ID, Title, Description, Category, Association)
•	Up to 2 reviewers with their details (ID, Name, Association, Expertise)
•	Similarity scores for each reviewer
Sheet 2: By Reviewer
Each row contains:
•	Reviewer information (ID, Name, Association, Expertise)
•	Number of assigned proposals
•	List of assigned proposal IDs
•	Proposal associations
•	Average similarity score
Sheet 3: Detailed Assignments
Expanded view with one row per proposal-reviewer pair containing:
•	All proposal details
•	All reviewer details
•	Similarity score
All sheets include:
•	Professional formatting with blue headers
•	Auto-adjusted column widths
•	Frozen header rows
•	Border styling
Statistics and Validation
The script outputs detailed statistics including:
Proposal Coverage
•	Count of proposals with 0, 1, 2, or >2 reviewers
•	Total assignments made
Reviewer Workload
•	Minimum, maximum, and average proposals per reviewer
•	Distribution histogram
•	List of reviewers above/below target workload
Similarity Scores
•	Average, minimum, and maximum similarity scores
•	Helps assess match quality
Example Output
=== Workload Calculation ===
Total proposals: 50
Total members: 25
Total reviews needed: 100
Base reviews per member: 4
Members who need +1 extra: 0
Target distribution: 25 members with 4 reviews

=== ROUND 1: Association-based Assignment ===
BS: 5 proposal(s), 3 member(s)
  ✓ Proposal P001 → John Smith (BS) [Round 1A: association match, sim=0.856]
  ...

=== Round 2 Complete ===
✓ All proposals have 2 reviewers!

=== Final Workload Distribution ===
Min: 3 | Max: 5 | Avg: 4.0
Features
•	Embedding Normalization: Handles various embedding formats (strings, arrays, nested structures)
•	Robust Error Handling: Graceful handling of missing embeddings or malformed data
•	Detailed Logging: Comprehensive progress reporting and debugging information
•	Fair Distribution: Workload balancing algorithm ensures equitable assignment
•	Excel Formatting: Professional output with color-coded headers and borders
Notes
•	Embeddings should be pre-computed using your preferred method (e.g., OpenAI, Sentence Transformers)
•	The script uses cosine similarity to measure proposal-reviewer matching
•	Association names are case-sensitive and should match exactly between proposals and members
•	Proposals or members without associations are automatically categorized as "Other"
Troubleshooting
No assignments for certain proposals:
•	Check that proposal associations match member associations exactly
•	Verify embeddings are present for both proposals and members
Uneven workload distribution:
•	This is expected when total reviews don't divide evenly by number of reviewers
•	The algorithm minimizes variance while respecting association rules
Low similarity scores:
•	May indicate embedding quality issues
•	Consider regenerating embeddings with better context or different models
License
Internal use only - ISI IPS Review System

