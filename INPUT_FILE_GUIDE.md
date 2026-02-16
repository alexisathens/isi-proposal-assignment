# Input File Format Guide

This guide provides detailed specifications and examples for preparing your input CSV files.

## Overview

The system requires **three CSV files** in the `Input/` folder:

1. **proposals.csv** - Basic proposal information
2. **descriptions.csv** - Detailed proposal descriptions
3. **members.csv** - Reviewer information and expertise

## General CSV Requirements

**All CSV files must follow these rules:**

- **Delimiter**: Semicolon (`;`) not comma
- **Encoding**: Latin-1 (ISO-8859-1)
- **Headers**: First row must contain column names (case-sensitive)
- **Line endings**: Any (Windows CRLF, Unix LF both work)
- **Quotes**: Use double quotes for fields containing semicolons

### Why Semicolon Delimiter?

Proposal descriptions and expertise often contain commas, making semicolon a safer delimiter.

### Why Latin-1 Encoding?

Handles special characters in names and descriptions (e.g., "José", "Müller", "São Paulo").

## File 1: proposals.csv

### Required Columns

| Column Name | Type | Required | Description | Example |
|-------------|------|----------|-------------|---------|
| Proposal ID | String/Number | ✅ Yes | Unique identifier | `1`, `P001`, `IPS-2024-001` |
| Title | Text | ✅ Yes | Proposal title | `Statistical Methods for AI` |
| Association | String | ✅ Yes | Association code | `BS`, `IAOS`, `Other` |

### Optional Columns

You can include additional columns (they'll be ignored):
- Category
- Status
- Submission Date
- etc.

### Association Codes

Valid codes (case-sensitive):
- `BS` - Bernoulli Society
- `IAOS` - International Association for Official Statistics
- `IASC` - International Association for Statistical Computing
- `IASE` - International Association for Statistical Education
- `IASS` - International Association of Survey Statisticians
- `IFC` - Irving Fisher Committee on Central Bank Statistics
- `ISBIS` - International Society for Business and Industrial Statistics
- `ISI` - International Statistical Institute
- `KOSTAT` - Korean National Statistical Office
- `TIES` - The International Environmetrics Society
- `Women` - Women in Statistics
- `Young` - Young Statisticians
- `Other` - Default for unknown/missing

### Example File

```csv
Proposal ID;Title;Association
1;A complete measure of wealth and wealth inequality;BS
2;An introduction to INEXDA metadata schema;IAOS
3;Birth registration an essential element for the individual and for government;IASC
4;Building and maintaining trust in today's data;IASE
5;Climate change impacts on agricultural statistics;TIES
6;Emerging methods in survey sampling;IASS
```

### Common Mistakes

❌ **Wrong delimiter:**
```csv
Proposal ID,Title,Association  ← Uses comma instead of semicolon
```

❌ **Missing association:**
```csv
Proposal ID;Title;Association
1;My Proposal;   ← Empty association (will default to "Other")
```

❌ **Case mismatch:**
```csv
Proposal ID;Title;Association
1;My Proposal;bs  ← Should be "BS" (uppercase)
```

✅ **Correct:**
```csv
Proposal ID;Title;Association
1;My Proposal;BS
```

## File 2: descriptions.csv

### Required Columns

| Column Name | Type | Required | Description | Example |
|-------------|------|----------|-------------|---------|
| Proposal ID | String/Number | ✅ Yes | Must match proposals.csv | `1`, `P001` |
| Brief Description | Text | ✅ Yes | Short summary | `This session explores...` |
| WSC Proposal Description | Text | ✅ Yes | Full description | `Detailed background...` |

### Important Notes

- **Proposal ID must match** the ID in proposals.csv exactly
- If a Proposal ID is missing here, that proposal will have no description
- Descriptions can be long (multiple paragraphs)
- Semicolons in text should be fine (within quotes)

### Example File

```csv
Proposal ID;Brief Description;WSC Proposal Description
1;This session examines new approaches to measuring wealth inequality using administrative data.;Wealth inequality has become a central topic in economic policy debates. Traditional survey methods often underestimate the wealth of the richest households due to sampling and response issues. This session brings together researchers who have developed innovative methods combining tax records, property registries, and survey data to create more complete measures of wealth distribution.
2;Introduction to the INEXDA metadata schema for cross-national data harmonization.;The INEXDA project has developed a comprehensive metadata schema to facilitate the harmonization and documentation of cross-national datasets. This session presents the schema, demonstrates tools for implementation, and discusses case studies from national statistical offices.
```

### Handling Long Text

**Option 1: Use quotes**
```csv
Proposal ID;Brief Description;WSC Proposal Description
1;"Short summary; with semicolon";"Long description; also with; semicolons"
```

**Option 2: Avoid semicolons in descriptions**
- Use commas, dashes, or rewrite sentences

### Common Mistakes

❌ **Mismatched IDs:**
```csv
# proposals.csv
Proposal ID;Title;Association
P001;My Proposal;BS

# descriptions.csv - WRONG
Proposal ID;Brief Description;WSC Proposal Description
1;Summary;Details  ← ID doesn't match (P001 vs 1)
```

❌ **Wrong column names:**
```csv
Proposal ID;Summary;Full Description  ← Should be "Brief Description" and "WSC Proposal Description"
```

## File 3: members.csv

### Required Columns

| Column Name | Type | Required | Description | Example |
|-------------|------|----------|-------------|---------|
| ID | String/Number | ✅ Yes | Unique member identifier | `15`, `M001` |
| Members | Text | ✅ Yes | Full name | `John Smith` |
| Association | String | ✅ Yes | Association code | `BS`, `IAOS`, `Other` |
| Expertise | Text | ✅ Yes | Description of expertise | `Bayesian statistics, time series` |

### Expertise Field

**This is critical** - it's used to generate embeddings that match members to proposals.

**Good expertise descriptions:**
- Detailed and specific
- Include methodological areas
- Mention application domains
- List key topics

**Examples:**

✅ **Good:**
```
Extreme value theory and graphical models. Weather forecasting with AI. Statistical climate science. Causal inference methods.
```

✅ **Good:**
```
Survey methodology, data quality assessment, sampling design, non-response analysis, questionnaire design
```

❌ **Too vague:**
```
Statistics
```

❌ **Too brief:**
```
Surveys
```

### Example File

```csv
ID;Members;Association;Expertise
15;Sebastian Engelke;BS;Extreme value theory and graphical models. Extrapolation in machine learning. Weather forecasting with AI. Statistical climate science. Extremes of structural causal models.
7;John L. Eltinge;IAOS;Statistical ethics and scientific integrity. Multiple-source extensions of adaptive survey design. Data quality assessment. Disclosure protection. Classification and regression trees for incomplete data.
12;Ray-Bing Chen;IASC;Statistical and machine learning. Bayesian variable selection. Computer experiments. Optimal design. Statistical modeling.
6;Felipe Ruz;IASE;Statistical education. Civic statistics. Statistical culture. Statistics applied to education.
```

### Common Mistakes

❌ **Empty expertise:**
```csv
ID;Members;Association;Expertise
15;John Smith;BS;   ← No expertise provided
```

❌ **Association mismatch:**
```csv
# members.csv
ID;Members;Association;Expertise
15;John Smith;Statistics;...  ← "Statistics" is not a valid association code
```

## File Validation Checklist

Before running the pipeline, verify:

### proposals.csv
- [ ] Delimiter is semicolon (`;`)
- [ ] Encoding is Latin-1
- [ ] Has columns: `Proposal ID`, `Title`, `Association`
- [ ] All Proposal IDs are unique
- [ ] All associations use valid codes (or blank for "Other")
- [ ] No empty Proposal IDs

### descriptions.csv
- [ ] Delimiter is semicolon (`;`)
- [ ] Encoding is Latin-1
- [ ] Has columns: `Proposal ID`, `Brief Description`, `WSC Proposal Description`
- [ ] All Proposal IDs match those in proposals.csv
- [ ] No empty descriptions

### members.csv
- [ ] Delimiter is semicolon (`;`)
- [ ] Encoding is Latin-1
- [ ] Has columns: `ID`, `Members`, `Association`, `Expertise`
- [ ] All member IDs are unique
- [ ] All members have expertise text
- [ ] All associations use valid codes (or blank for "Other")
- [ ] No empty member IDs

## Testing Your Files

### Quick Format Check

**Python script to validate format:**

```python
import csv

def check_csv(filename, required_cols):
    with open(f'Input/{filename}', 'r', encoding='latin-1') as f:
        reader = csv.DictReader(f, delimiter=';')
        headers = reader.fieldnames
        print(f"\n{filename}:")
        print(f"  Found columns: {headers}")

        missing = [col for col in required_cols if col not in headers]
        if missing:
            print(f"  ❌ Missing columns: {missing}")
        else:
            print(f"  ✅ All required columns present")

        rows = list(reader)
        print(f"  Rows: {len(rows)}")
        return len(rows)

# Check all files
check_csv('proposals.csv', ['Proposal ID', 'Title', 'Association'])
check_csv('descriptions.csv', ['Proposal ID', 'Brief Description', 'WSC Proposal Description'])
check_csv('members.csv', ['ID', 'Members', 'Association', 'Expertise'])
```

Save as `validate_inputs.py` and run:
```bash
python validate_inputs.py
```

## Converting From Other Formats

### From Excel

**Save As:**
1. Open Excel file
2. File → Save As → CSV (Comma delimited)
3. Manually edit in text editor to replace commas with semicolons
4. Save with Latin-1 encoding

**Better: Use Python**
```python
import pandas as pd

# Read Excel
df = pd.read_excel('proposals.xlsx')

# Save as CSV with correct format
df.to_csv('Input/proposals.csv', sep=';', encoding='latin-1', index=False)
```

### From Google Sheets

1. File → Download → CSV
2. Open in text editor (VSCode, Notepad++, etc.)
3. Replace all `,` with `;`
4. Save with Latin-1 encoding

### From Database

```python
import pandas as pd
import sqlalchemy

engine = sqlalchemy.create_engine('your-database-url')

# Export proposals
df = pd.read_sql('SELECT proposal_id, title, association FROM proposals', engine)
df.to_csv('Input/proposals.csv', sep=';', encoding='latin-1', index=False)

# Export members
df = pd.read_sql('SELECT id, name as Members, association, expertise FROM members', engine)
df.to_csv('Input/members.csv', sep=';', encoding='latin-1', index=False)
```

## Real-World Example

Here's a complete minimal example with 3 proposals and 2 members:

**Input/proposals.csv:**
```csv
Proposal ID;Title;Association
1;Bayesian Methods in Climate Science;BS
2;Survey Design for Administrative Data;IAOS
3;Teaching Statistics with Real Data;IASE
```

**Input/descriptions.csv:**
```csv
Proposal ID;Brief Description;WSC Proposal Description
1;Applying Bayesian methods to climate modeling;This session explores how Bayesian statistical methods can improve climate model predictions and uncertainty quantification. Topics include hierarchical models, ensemble methods, and extreme value analysis.
2;Integrating administrative and survey data;Modern statistical agencies increasingly combine survey data with administrative records. This session discusses design challenges, quality assessment, and statistical methods for integrated data sources.
3;Best practices for statistics education;Statistical education research has identified effective teaching methods. This session presents evidence-based approaches to teaching statistics using real-world datasets and active learning.
```

**Input/members.csv:**
```csv
ID;Members;Association;Expertise
1;Dr. Anna Schmidt;BS;Bayesian hierarchical modeling, climate statistics, extreme value theory, spatial statistics, uncertainty quantification
2;Dr. James Chen;IAOS;Survey methodology, administrative data integration, data quality, sampling design, statistical disclosure control
```

## Need Help?

**Issues with file formats:**
- Check encoding: `file -i Input/proposals.csv` (Linux/Mac)
- Check delimiter: Open in text editor and verify semicolons
- Check columns: Run the validation script above

**Still having problems:**
- See [README.md - Troubleshooting](README.md#troubleshooting)
- Review [QUICKSTART.md](QUICKSTART.md) for complete workflow

---

**Next step:** Once your files are ready, proceed to [QUICKSTART.md](QUICKSTART.md) to run the pipeline!
