# Batch Processing Guide

This guide explains how to use the batch processing feature to screen multiple candidates at once.

## Overview

The batch processing feature allows you to:
- Upload an entire folder of resumes at once
- Automatically analyze all resumes for fraud indicators
- Get a comprehensive dashboard with risk scores
- Filter and sort results
- Export findings to CSV

## Step-by-Step Instructions

### 1. Prepare Your Resume Folder

Organize your resumes in a folder on your computer. The system supports:
- **PDF files** (.pdf)
- **Word documents** (.docx)
- **Text files** (.txt)

**Naming Convention Tip:** Name files with candidate names (e.g., `John_Doe.pdf`, `Jane_Smith.docx`) - the system will extract names from filenames.

### 2. Access Batch Processing

1. Open the Candidate Verification System in your browser
2. Click on the **"Batch Processing"** tab

### 3. Select Files

You have two options:

**Option A: Select an Entire Folder**
1. Click the "Choose Files" button
2. Navigate to your resume folder
3. Select the folder
4. All compatible files will be loaded

**Option B: Select Multiple Individual Files**
1. Click the "Choose Files" button
2. Hold Ctrl (Windows/Linux) or Cmd (Mac)
3. Click on each resume file you want to process
4. Click "Open"

You'll see a count of selected files (e.g., "25 files selected")

### 4. Add Job Description (Optional but Recommended)

Paste the job description in the text area. This helps the system:
- Detect resumes that suspiciously match the job description too closely
- Identify AI-generated content tailored to the role
- Catch trap terms you may have planted

### 5. Process Resumes

Click **"Process All Resumes"**

The system will:
- Analyze each resume for AI-generated content
- Check for trap terms and fraud indicators
- Calculate risk scores
- Identify red flags

Processing time: ~2-5 seconds per resume

### 6. Review Results

#### Summary Dashboard

The top of the results shows:
- **Total Processed**: Number of resumes analyzed
- **Critical Risk**: Candidates with severe fraud indicators (REJECT)
- **High Risk**: Candidates requiring extensive verification
- **Medium Risk**: Candidates needing additional screening
- **Low/Minimal**: Candidates safe to proceed with
- **AI Generated**: Count of AI-generated resumes
- **Trap Terms Found**: Resumes containing planted keywords

#### Results Table

Each candidate appears in a sortable table with:
- **Risk Score**: 0-100 (higher = more suspicious)
- **Risk Level**: CRITICAL | HIGH | MEDIUM | LOW | MINIMAL
- **AI Generated**: Yes/No with confidence percentage
- **Red Flags**: Count of critical/warning/minor issues
- **Specificity Score**: How detailed the resume is
- **Experience**: Total years of experience

### 7. Filter and Sort

Use the controls above the table:

**Filter by Risk Level:**
- All Levels (default)
- Critical Only
- High Only
- Medium Only
- Low Only
- Minimal Only

**Sort by:**
- Risk (High to Low) - **Recommended for initial review**
- Risk (Low to High)
- Name (A-Z)
- Name (Z-A)

**Additional Filters:**
- ☑️ **AI-Generated Only** - Show only resumes flagged as AI-generated

### 8. View Detailed Analysis

Click the **"📋 Details"** button on any row to see:
- Full filename
- Specific recommendation
- Buzzword density
- Trap term detection
- Timeline validation
- All red flags with descriptions
- Detailed fraud indicators

### 9. Export to CSV

Click **"📊 Export to CSV"** to download results including:
- All candidate names
- Risk scores and levels
- AI detection results
- Flag counts
- Recommendations
- All metrics

The CSV file is named: `candidate_verification_results_YYYY-MM-DD.csv`

## Interpreting Results

### Risk Levels

| Score | Level | Action |
|-------|-------|--------|
| 70-100 | CRITICAL | **REJECT** - Multiple fraud indicators detected |
| 50-69 | HIGH | **CAUTION** - Extensive verification required |
| 30-49 | MEDIUM | **INVESTIGATE** - Additional screening needed |
| 15-29 | LOW | **PROCEED CAUTIOUSLY** - Minor concerns noted |
| 0-14 | MINIMAL | **PROCEED** - No significant fraud indicators |

### Red Flags to Watch For

**Critical (Immediate Rejection):**
- Trap terms detected (resume was scraped from job posting)
- 90%+ match with job description
- Multiple inconsistencies

**Warnings (Investigate Further):**
- AI-generated content detected
- Excessive buzzwords without substance
- Career progression anomalies
- Timeline gaps or overlaps

**Minor (Monitor During Interview):**
- Moderate buzzword usage
- Vague descriptions
- Limited specific details

## Best Practices

### 1. Review Critical/High Risk First
Sort by "Risk (High to Low)" and focus on top candidates first. These need immediate attention.

### 2. Use Filters Strategically
- Start with "Critical Only" to identify obvious fraud
- Then move to "High" for candidates needing verification
- Review "AI-Generated Only" to see content quality issues

### 3. Combine with Manual Review
The system flags suspicious patterns, but human judgment is essential:
- Check critical flags candidates manually
- Verify employment history for high-risk candidates
- Use the LinkedIn verification checklist

### 4. Document Findings
Export to CSV and maintain records of:
- Which candidates were flagged
- Verification steps taken
- Final hiring decisions

### 5. Update Trap Terms
If you notice new fraud patterns, add custom trap terms in:
`backend/verification/resume_analyzer.py`

## Common Scenarios

### Scenario 1: Job Fair Screening
**Situation:** 100+ resumes collected at a job fair

**Process:**
1. Scan or collect resumes into one folder
2. Batch process all resumes
3. Export to CSV
4. Sort by risk score
5. Only interview candidates with MINIMAL/LOW risk
6. Manually verify MEDIUM risk candidates

### Scenario 2: Online Job Posting Response
**Situation:** 50 applicants for a DevOps position

**Process:**
1. Download all resumes to a folder
2. Copy the job description
3. Batch process with job description
4. Check "AI-Generated Only" filter
5. Reject all CRITICAL risk
6. Investigate HIGH risk candidates manually
7. Proceed normally with MEDIUM/LOW

### Scenario 3: Recruiting Agency Validation
**Situation:** Agency sent 20 "pre-screened" candidates

**Process:**
1. Batch process agency-provided resumes
2. Compare agency claims vs. fraud detection
3. Flag discrepancies
4. Provide feedback to agency
5. Only proceed with verified candidates

## Troubleshooting

### Files Not Processing
- **Check file format**: Only PDF, DOCX, TXT supported
- **File corruption**: Ensure files aren't password-protected
- **File size**: Very large files (>10MB) may fail

### Unexpected Risk Scores
- **Too high**: May have trap terms or match JD too closely
- **Too low**: Could be an experienced, genuine candidate
- Remember: The system flags patterns; human review is essential

### No Trap Terms Detected
If you planted trap terms but none were found:
- Verify trap terms are in `resume_analyzer.py`
- Check spelling/capitalization
- Ensure job description with trap terms was posted

## Advanced Usage

### Custom Trap Terms
Edit `backend/verification/resume_analyzer.py`:

```python
self.trap_terms = [
    'back-office engineering',
    'quantum-agile methodology',  # Your custom term
    'blockchain DevOps',          # Another custom term
]
```

Restart the backend server to apply changes.

### Adjusting Risk Thresholds
Edit `backend/app.py` in the `calculate_risk_score()` function to adjust weights.

### Integration with ATS
Export CSV and import into your Applicant Tracking System for record-keeping.

## Support

For issues or questions:
- Check the main README.md
- Review the fraud detection document
- Examine the code in `/backend/verification/` for detection logic

---

**Remember:** This tool assists in fraud detection but should not be the sole basis for hiring decisions. Always verify critical findings and use human judgment in the final decision.
