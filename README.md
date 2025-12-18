# Candidate Verification System

A comprehensive web application for detecting fraudulent job candidates using AI-powered analysis, OSINT techniques, and fraud detection patterns identified in tech recruitment.

## 🎯 Features

### Comprehensive Verification
- **Resume Analysis**: Detect AI-generated content, inconsistencies, and fraud indicators
- **Batch Processing**: Upload entire folders of resumes for automated screening
- **LinkedIn Profile Verification**: Automated checks and manual verification checklists
- **Online Presence Verification**: OSINT tools integration for digital footprint analysis
- **Interview Fraud Detection**: Guidelines and red flags for identifying cheating during interviews

### Detection Capabilities
- ✅ AI-generated resume content detection
- ✅ Trap term identification (planted keywords to catch resume scrapers)
- ✅ Career progression validation
- ✅ Timeline consistency checking
- ✅ Buzzword density analysis
- ✅ Terminology error detection
- ✅ LinkedIn profile age and authenticity verification
- ✅ Email and phone validation
- ✅ GitHub presence checking
- ✅ OSINT recommendations

## 📋 Based On

This tool implements the fraud detection strategies from:
**"DevOps - Candidate Authenticity Assessment" (v1.0.1)**

Research based on screening 169 candidates with documented fraud patterns and detection techniques.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js (optional, for serving frontend)
- Modern web browser

### Installation

1. **Clone or navigate to the project directory**
```bash
cd candidate-verification-app
```

2. **Set up the backend**
```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

3. **Configure environment variables (optional)**
```bash
cp .env.template .env
# Edit .env with your API keys if needed
```

4. **Start the backend server**
```bash
python app.py
```

The API will be available at `http://localhost:5000`

5. **Serve the frontend**

In a new terminal:
```bash
cd frontend

# Option 1: Using Python's built-in server
python3 -m http.server 3000

# Option 2: Using Node.js http-server
# npm install -g http-server
# http-server -p 3000
```

The web interface will be available at `http://localhost:3000`

## 📖 Usage Guide

### Comprehensive Verification

1. Navigate to the "Comprehensive Check" tab
2. Upload the candidate's resume (PDF, DOCX, or TXT)
3. Fill in candidate information (name, email, phone, LinkedIn URL)
4. Optionally paste the job description to check for suspicious matches
5. Click "Run Comprehensive Verification"
6. Review the detailed risk assessment and recommendations

### Resume Analysis Only

1. Go to the "Resume Only" tab
2. Upload the resume file
3. Optionally provide the job description
4. Get detailed AI detection and fraud indicators

### LinkedIn Verification

1. Select the "LinkedIn Checker" tab
2. Enter the LinkedIn profile URL
3. Get a comprehensive manual verification checklist
4. Follow the step-by-step instructions to verify authenticity

### Batch Processing (Folder Upload)

1. Navigate to the "Batch Processing" tab
2. Click "Choose Files" and select a folder containing resumes
   - Or use Ctrl/Cmd+Click to select multiple individual files
   - Supports PDF, DOCX, and TXT formats
3. Optionally paste the job description
4. Click "Process All Resumes"
5. Review the summary dashboard showing:
   - Total processed
   - Risk level breakdown (Critical/High/Medium/Low)
   - AI-generated count
   - Trap terms detected
6. Use filters to narrow results:
   - Filter by risk level
   - Show AI-generated only
   - Sort by risk score or name
7. Click "Details" on any row to see complete analysis
8. Export results to CSV for further analysis

**Perfect for:** Screening large applicant pools, job fairs, recruiting agencies

### Interview Helper

1. Click on the "Interview Helper" tab
2. Review common fraud patterns (impersonation, shadowing, AI assistance)
3. Use the detection techniques during interviews
4. Reference the red flag checklist during candidate calls

## 🎨 Interface

The application features a professional dark theme interface with:
- Modern, clean design
- Easy-to-read risk scores and color-coded indicators
- Comprehensive reporting
- Mobile-responsive layout

## 🔍 Detection Methods

### Resume Verification
- **Trap Terms**: Planted keywords to catch scraped resumes
- **Generic Content Detection**: Identifies resumes that mirror job descriptions
- **AI Detection**: Multiple heuristics to identify AI-generated text
- **Buzzword Analysis**: Flags excessive use of trendy terms without substance
- **Specificity Scoring**: Measures concrete details vs vague statements
- **Timeline Validation**: Checks for date inconsistencies and overlaps

### LinkedIn Profile Verification
- Profile age checking
- Verification badge status
- Connection count analysis
- Experience detail validation
- Wayback Machine integration for historical data
- Account rotation detection

### Online Presence
- Email validation (disposable email detection)
- Phone number verification
- GitHub profile discovery
- Google search presence
- OSINT tool recommendations:
  - ThatsThem
  - HaveIBeenPwned
  - WhatsMyName
  - Intelligence X
  - FamilyTreeNow

### Interview Fraud Detection
- Impersonation indicators
- Shadowing detection techniques
- AI assistance patterns
- Context recall testing
- Progressive drilling methods
- Counterintuitive questioning
- Behavioral assessment techniques

## 🛡️ Risk Scoring

The system provides risk scores on a 0-100 scale:
- **0-15**: MINIMAL RISK - Proceed normally
- **15-30**: LOW RISK - Standard screening recommended
- **30-50**: MEDIUM RISK - Additional verification needed
- **50-70**: HIGH RISK - Extensive verification required
- **70-100**: CRITICAL RISK - Recommend rejection

## 📊 API Endpoints

### `POST /api/verify/comprehensive`
Complete candidate verification with all checks

**Form Data:**
- `file`: Resume file (PDF/DOCX/TXT)
- `name`: Candidate name
- `email`: Email address
- `phone`: Phone number (optional)
- `location`: Location (optional)
- `linkedin_url`: LinkedIn profile URL (optional)
- `job_description`: Job description text (optional)

**Response:**
```json
{
  "overall_risk_score": 45.5,
  "overall_risk_level": "MEDIUM",
  "recommendation": "INVESTIGATE - Additional screening recommended",
  "resume_verification": { ... },
  "online_verification": { ... }
}
```

### `POST /api/verify/resume`
Resume-only analysis

### `POST /api/verify/batch`
Process multiple resumes at once

**Form Data:**
- `files`: Array of resume files (PDF/DOCX/TXT)
- `job_description`: Job description text (optional)

**Response:**
```json
{
  "total_files": 25,
  "processed": 24,
  "failed": 1,
  "results": [
    {
      "filename": "John_Doe.pdf",
      "candidate_name": "John Doe",
      "risk_score": 75.5,
      "risk_level": "CRITICAL",
      "ai_generated": true,
      "critical_flags": 2,
      "warning_flags": 3,
      ...
    }
  ],
  "summary": {
    "critical_risk": 3,
    "high_risk": 5,
    "medium_risk": 8,
    "low_risk": 8,
    "ai_generated_count": 6,
    "trap_terms_count": 2
  }
}
```

### `POST /api/verify/linkedin`
LinkedIn profile verification

### `POST /api/verify/online-presence`
Online presence checking

## 🔧 Customization

### Adding Trap Terms

Edit `backend/verification/resume_analyzer.py`:
```python
self.trap_terms = [
    'back-office engineering',
    'your-custom-trap-term',
]
```

### Adjusting Risk Thresholds

Modify the scoring functions in `backend/app.py`:
- `calculate_risk_score()`
- `calculate_comprehensive_risk()`
- `get_risk_level()`

### Custom Detection Patterns

Add AI patterns in `backend/verification/ai_detector.py`:
```python
self.ai_patterns = [
    r'your-custom-pattern',
]
```

## 🤝 Contributing

This tool is designed to help combat recruitment fraud in the tech industry. Contributions and improvements are welcome.

## ⚠️ Disclaimer

This tool is designed to assist in fraud detection but should not be the sole basis for hiring decisions. Always conduct thorough verification and use human judgment. False positives can occur.

## 📄 License

This project is provided as-is for fraud prevention in recruitment processes.

## 🙏 Acknowledgments

Based on real-world fraud detection research by hthu@alvaka.net, documenting patterns from 169+ candidate assessments.

---

**Version**: 1.0.0
**Last Updated**: 2024
