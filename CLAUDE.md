# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Flask-based web application for detecting fraudulent job candidates using AI-powered analysis, OSINT techniques, and fraud detection patterns. The system analyzes resumes, LinkedIn profiles, and online presence to assign risk scores (0-100) and recommendations.

## Commands

### Quick Start
```bash
# Start both backend and frontend servers (recommended)
./start-simple.sh

# Then open: http://localhost:8000
```

### Manual Development

**Backend (Terminal 1):**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py              # Runs on http://localhost:5001
```

**Frontend (Terminal 2):**
```bash
cd frontend
python3 -m http.server 8000  # Runs on http://localhost:8000
```

### Testing Individual Components
```bash
cd backend
source venv/bin/activate

# Test resume analysis
python -c "from verification.resume_analyzer import ResumeAnalyzer; ra = ResumeAnalyzer(); print(ra)"

# Test AI detection
python -c "from verification.ai_detector import AIContentDetector; ai = AIContentDetector(); print(ai)"
```

### Kill Stuck Processes
```bash
lsof -ti:5001 | xargs kill -9  # Kill backend
lsof -ti:8000 | xargs kill -9  # Kill frontend
```

## Architecture

### Backend Structure (`backend/`)

**Core Application:**
- `app.py` - Flask server with 5 main API endpoints + batch processing
- Runs on port 5001 (avoiding macOS AirPlay conflict with 5000)

**Verification Modules (`verification/`):**
All modules are independent and can be used separately:

1. **`resume_analyzer.py`** - Resume authenticity checks
   - Extracts text from PDF/DOCX/TXT
   - Detects trap terms (planted keywords to catch scraped resumes)
   - Checks career progression, timeline consistency
   - Calculates buzzword density and specificity scores

2. **`ai_detector.py`** - AI-generated content detection
   - Pattern matching for GPT/ChatGPT artifacts
   - Sentence structure analysis
   - Repetition and phrase detection
   - Returns confidence scores (0-1)

3. **`linkedin_checker.py`** - LinkedIn profile verification
   - Generates manual verification checklists
   - Provides Wayback Machine integration instructions
   - Checks for common fraud patterns (new accounts, rotation schemes)

4. **`online_presence.py`** - OSINT and digital footprint
   - Email validation (disposable email detection)
   - Phone number verification
   - GitHub profile discovery
   - Recommends additional OSINT tools

5. **`report_generator.py`** - Formats verification results
   - Consolidates findings from all modules
   - Generates structured reports with recommendations

### Frontend Structure (`frontend/`)

**Single Page Application:**
- `index.html` - 5 tabs: Comprehensive Check, Resume Only, LinkedIn Checker, Batch Processing, Interview Helper
- `app.js` - Handles all API calls, file uploads, batch processing, CSV export
- `styles.css` - Dark theme with color-coded risk indicators

**No build step required** - vanilla HTML/CSS/JS served via Python's http.server

### Data Flow

```
User uploads resume → Flask receives file → ResumeAnalyzer extracts text
                                         ↓
                         AIContentDetector analyzes content
                                         ↓
                         ResumeAnalyzer checks fraud indicators
                                         ↓
                         Risk score calculated (weighted sum)
                                         ↓
                         Response with risk_level and recommendations
```

## API Endpoints

All endpoints are POST and return JSON:

- `/api/verify/resume` - Resume-only analysis (file + optional job_description)
- `/api/verify/linkedin` - LinkedIn verification checklist (profile_url)
- `/api/verify/online-presence` - OSINT checks (name, email, phone, location)
- `/api/verify/comprehensive` - Full verification (combines resume + online presence)
- `/api/verify/batch` - Batch processing (multiple files + optional job_description)
- `/api/health` - Health check endpoint

## Risk Scoring System

Risk scores are 0-100 (higher = more suspicious):

- **0-14**: MINIMAL RISK - Proceed normally
- **15-29**: LOW RISK - Standard screening
- **30-49**: MEDIUM RISK - Additional verification needed
- **50-69**: HIGH RISK - Extensive verification required
- **70-100**: CRITICAL RISK - Recommend rejection

**Calculation:** Weighted sum in `app.py:calculate_risk_score()`
- AI detection confidence × 30
- Trap terms detected × 40
- Buzzword density × 10
- Career inconsistencies × 15
- Timeline gaps/overlaps × 5

## Key Customization Points

### 1. Trap Terms (Most Common Edit)

Edit `backend/verification/resume_analyzer.py`:
```python
self.trap_terms = [
    'back-office engineering',
    'quantum-agile methodology',  # Add your custom terms
]
```

These are fake job requirements you plant in job descriptions to catch candidates who copy-paste requirements into resumes.

### 2. Risk Thresholds

Edit `backend/app.py` functions:
- `calculate_risk_score()` - Adjust weights for different fraud indicators
- `get_risk_level()` - Modify score ranges for risk levels

### 3. AI Detection Patterns

Edit `backend/verification/ai_detector.py`:
```python
self.ai_patterns = [
    r'your-custom-pattern',
]
```

## Development Workflow

### Adding a New Verification Module

1. Create `backend/verification/new_module.py`
2. Import in `backend/app.py`
3. Initialize in app.py global scope
4. Add new endpoint if needed
5. Update risk scoring to include new signals
6. Add UI tab in `frontend/index.html` and handler in `app.js`

### Modifying Verification Logic

All verification modules follow the same pattern:
- Take input (text, URL, candidate info)
- Return dict with `findings`, `flags`, `score`/`confidence`
- Never throw exceptions - return error messages in response

### Testing Changes

After modifying verification modules:
1. Restart Flask app (`Ctrl+C` and `python app.py`)
2. No need to restart frontend for backend changes
3. Hard refresh browser (`Cmd+Shift+R` or `Ctrl+Shift+R`) for frontend changes

## Dependencies

**Backend** (`backend/requirements.txt`):
- Flask 3.0.0 - Web framework
- PyPDF2 - PDF text extraction
- python-docx - Word document parsing
- transformers + torch - AI content detection (large dependencies ~2GB)
- beautifulsoup4 - HTML parsing for LinkedIn checks
- phonenumbers, email-validator - Contact validation

**Frontend**: No dependencies (vanilla JS)

## Important Files

- `.env` - Configuration (created from `.env.template`, not in git)
- `BATCH_PROCESSING_GUIDE.md` - Detailed guide for batch processing feature
- `QUICK_START.md` - Simplified startup instructions
- `README.md` - Full project documentation

## Batch Processing Notes

The batch processing feature (`/api/verify/batch`) is designed for high-volume screening:
- Processes multiple resumes in parallel
- Returns summary dashboard with risk distribution
- Supports CSV export of all results
- Frontend handles file selection and progress display

When modifying batch processing:
- Backend: `app.py:batch_verification()`
- Frontend: `app.js:processBatch()` and `renderBatchResults()`

## Port Configuration

- Backend: Port 5001 (not 5000 - conflicts with macOS AirPlay)
- Frontend: Port 8000 (arbitrary choice, can be changed)
- Update `frontend/app.js` API_BASE_URL if changing backend port

## Common Issues

**Virtual environment not activating**: Use bash/zsh, not fish shell
**Module not found**: Ensure `source venv/bin/activate` before running
**CORS errors**: Flask-CORS is configured to allow all origins in development
**Large ML models**: First run downloads ~2GB transformers models (torch, transformers)

## Security Notes

- Never commit `.env` file (contains API keys)
- No authentication on API endpoints (development only)
- File uploads are not persisted (processed in-memory)
- No database - all processing is stateless
