"""
Resume Analyzer Module
Detects fabricated or AI-generated resumes based on patterns identified in the assessment document.
"""

import re
from datetime import datetime
from docx import Document
import PyPDF2
import io

class ResumeAnalyzer:
    def __init__(self):
        # Trap terms from the assessment document
        self.trap_terms = [
            'back-office engineering',  # Term from the document used as a plant
        ]

        # DevOps-specific incorrect terminology patterns
        self.incorrect_terms = {
            'kubenetes': 'kubernetes',  # Common typo
            'dock': 'docker',  # Should be Docker
            'jenkin': 'jenkins',  # Missing 's'
            'anisble': 'ansible',  # Typo
        }

        # Buzzwords commonly overused in fake resumes
        self.buzzwords = [
            'synergy', 'paradigm shift', 'blockchain', 'AI/ML', 'cloud-native',
            'microservices', 'kubernetes', 'docker', 'terraform', 'ansible',
            'CI/CD', 'DevOps', 'agile', 'scrum', 'serverless'
        ]

    def extract_text(self, file):
        """Extract text from resume file (PDF or DOCX)"""
        filename = file.filename.lower()

        if filename.endswith('.pdf'):
            return self._extract_from_pdf(file)
        elif filename.endswith('.docx'):
            return self._extract_from_docx(file)
        elif filename.endswith('.txt'):
            return file.read().decode('utf-8')
        else:
            raise ValueError("Unsupported file format. Please upload PDF, DOCX, or TXT")

    def _extract_from_pdf(self, file):
        """Extract text from PDF"""
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text

    def _extract_from_docx(self, file):
        """Extract text from DOCX"""
        doc = Document(io.BytesIO(file.read()))
        text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        return text

    def analyze_authenticity(self, resume_text, job_description=''):
        """Analyze resume for authenticity indicators"""
        results = {
            'generic_content': self._check_generic_content(resume_text, job_description),
            'unrealistic_progression': self._check_career_progression(resume_text),
            'buzzword_density': self._calculate_buzzword_density(resume_text),
            'trap_terms_found': self._check_trap_terms(resume_text),
            'specificity_score': self._calculate_specificity(resume_text)
        }

        return results

    def _check_generic_content(self, resume_text, job_description):
        """Check if resume closely mirrors job description"""
        if not job_description:
            return {'is_generic': False, 'match_percentage': 0}

        resume_lower = resume_text.lower()
        jd_lower = job_description.lower()

        # Extract key phrases from job description (3+ word sequences)
        jd_phrases = set(re.findall(r'\b\w+(?:\s+\w+){2,}\b', jd_lower))

        # Check how many JD phrases appear in resume
        matches = sum(1 for phrase in jd_phrases if phrase in resume_lower)

        match_percentage = (matches / len(jd_phrases) * 100) if jd_phrases else 0

        return {
            'is_generic': match_percentage > 80,
            'match_percentage': round(match_percentage, 2),
            'warning': match_percentage > 80
        }

    def _check_career_progression(self, resume_text):
        """Check for unrealistic career progression"""
        # Look for job titles and time periods
        title_patterns = [
            r'(junior|associate|senior|lead|principal|staff|architect|manager|director|vp|cto|ceo)',
            r'(engineer|developer|analyst|administrator|specialist)'
        ]

        positions = []
        lines = resume_text.split('\n')

        for line in lines:
            # Look for dates (various formats)
            date_match = re.search(r'(\d{4})\s*[-–]\s*(\d{4}|present|current)', line, re.IGNORECASE)
            if date_match:
                # Look for title in same or adjacent lines
                for title_pattern in title_patterns:
                    if re.search(title_pattern, line, re.IGNORECASE):
                        positions.append({
                            'line': line,
                            'year': int(date_match.group(1))
                        })
                        break

        # Check for rapid progression
        rapid_progression = False
        if len(positions) >= 2:
            sorted_positions = sorted(positions, key=lambda x: x['year'])
            # Check if someone went from junior to senior/lead in < 2 years
            for i in range(len(sorted_positions) - 1):
                time_diff = sorted_positions[i+1]['year'] - sorted_positions[i]['year']
                if time_diff < 2:
                    if ('junior' in sorted_positions[i]['line'].lower() and
                        ('senior' in sorted_positions[i+1]['line'].lower() or
                         'lead' in sorted_positions[i+1]['line'].lower())):
                        rapid_progression = True

        return {
            'has_rapid_progression': rapid_progression,
            'positions_found': len(positions)
        }

    def _calculate_buzzword_density(self, resume_text):
        """Calculate density of buzzwords in resume"""
        words = resume_text.lower().split()
        buzzword_count = sum(1 for word in words if any(buzz in word for buzz in self.buzzwords))

        density = (buzzword_count / len(words) * 100) if words else 0

        return {
            'density': round(density, 2),
            'buzzword_count': buzzword_count,
            'is_excessive': density > 5  # More than 5% buzzwords is suspicious
        }

    def _check_trap_terms(self, resume_text):
        """Check for planted trap terms"""
        found_traps = []
        resume_lower = resume_text.lower()

        for trap in self.trap_terms:
            if trap.lower() in resume_lower:
                found_traps.append(trap)

        return {
            'has_trap_terms': len(found_traps) > 0,
            'terms_found': found_traps,
            'critical_flag': len(found_traps) > 0  # This is a critical indicator
        }

    def _calculate_specificity(self, resume_text):
        """Calculate how specific the resume is (vs generic)"""
        # Look for specific indicators:
        # - Numbers/metrics (e.g., "reduced costs by 30%", "managed team of 5")
        # - Specific technologies with version numbers
        # - Concrete project names
        # - Specific company/product names

        metrics_pattern = r'\d+%|\$\d+|reduced|increased|improved|managed \d+|team of \d+'
        version_pattern = r'\d+\.\d+'
        specific_detail_pattern = r'(implemented|designed|built|created|developed)\s+\w+'

        metrics_count = len(re.findall(metrics_pattern, resume_text, re.IGNORECASE))
        version_count = len(re.findall(version_pattern, resume_text))
        detail_count = len(re.findall(specific_detail_pattern, resume_text, re.IGNORECASE))

        # Score out of 100
        score = min((metrics_count * 5 + version_count * 3 + detail_count * 2), 100)

        return {
            'score': score,
            'metrics_count': metrics_count,
            'version_references': version_count,
            'specific_details': detail_count,
            'is_vague': score < 30
        }

    def check_consistency(self, resume_text):
        """Check for timeline and experience consistency"""
        # Extract all dates
        date_pattern = r'(\d{1,2}/\d{4}|\d{4})\s*[-–]\s*(\d{1,2}/\d{4}|\d{4}|present|current)'
        dates = re.findall(date_pattern, resume_text, re.IGNORECASE)

        overlaps = []
        gaps = []
        total_experience_years = 0

        # Convert dates and check for overlaps
        parsed_dates = []
        for start, end in dates:
            start_year = int(re.search(r'\d{4}', start).group())
            end_year = datetime.now().year if end.lower() in ['present', 'current'] else int(re.search(r'\d{4}', end).group())

            # Check for impossible dates
            if end_year < start_year:
                gaps.append(f"End date before start date: {start} - {end}")
            elif end_year > datetime.now().year:
                gaps.append(f"Future end date: {end}")

            parsed_dates.append((start_year, end_year))
            total_experience_years += (end_year - start_year)

        # Check for overlapping positions
        for i, (start1, end1) in enumerate(parsed_dates):
            for start2, end2 in parsed_dates[i+1:]:
                if (start1 <= start2 <= end1) or (start2 <= start1 <= end2):
                    overlaps.append(f"Overlapping dates: {start1}-{end1} and {start2}-{end2}")

        return {
            'dates_valid': len(gaps) == 0,
            'has_overlaps': len(overlaps) > 0,
            'overlaps': overlaps,
            'date_errors': gaps,
            'total_experience_years': total_experience_years,
            'career_progression_valid': total_experience_years >= 0
        }

    def check_terminology(self, resume_text):
        """Check for incorrect industry terminology"""
        errors = []
        resume_lower = resume_text.lower()

        for incorrect, correct in self.incorrect_terms.items():
            if incorrect in resume_lower:
                errors.append({
                    'found': incorrect,
                    'should_be': correct,
                    'context': 'Possible typo or lack of familiarity with technology'
                })

        return {
            'has_errors': len(errors) > 0,
            'errors': errors,
            'error_count': len(errors)
        }

    def identify_red_flags(self, resume_text, job_description=''):
        """Identify all red flags based on the assessment document"""
        critical = []
        warning = []
        minor = []

        # Check trap terms (CRITICAL)
        trap_check = self._check_trap_terms(resume_text)
        if trap_check['has_trap_terms']:
            critical.append({
                'type': 'TRAP_TERM_DETECTED',
                'severity': 'CRITICAL',
                'description': f"Resume contains planted trap term(s): {', '.join(trap_check['terms_found'])}",
                'recommendation': 'REJECT - This is a clear indicator of resume scraping'
            })

        # Check generic content (WARNING)
        if job_description:
            generic_check = self._check_generic_content(resume_text, job_description)
            if generic_check['match_percentage'] > 90:
                critical.append({
                    'type': 'EXACT_JD_MATCH',
                    'severity': 'CRITICAL',
                    'description': f"Resume matches job description {generic_check['match_percentage']}%",
                    'recommendation': 'Likely AI-generated or copy-pasted from job description'
                })
            elif generic_check['match_percentage'] > 75:
                warning.append({
                    'type': 'HIGH_JD_SIMILARITY',
                    'severity': 'WARNING',
                    'description': f"Resume closely mirrors job description ({generic_check['match_percentage']}%)",
                    'recommendation': 'Investigate further - may be tailored excessively'
                })

        # Check buzzword density (WARNING)
        buzzword_check = self._calculate_buzzword_density(resume_text)
        if buzzword_check['density'] > 8:
            warning.append({
                'type': 'EXCESSIVE_BUZZWORDS',
                'severity': 'WARNING',
                'description': f"High buzzword density: {buzzword_check['density']}%",
                'recommendation': 'Resume may lack substance, verify claims thoroughly'
            })
        elif buzzword_check['density'] > 5:
            minor.append({
                'type': 'MODERATE_BUZZWORDS',
                'severity': 'MINOR',
                'description': f"Moderate buzzword usage: {buzzword_check['density']}%",
                'recommendation': 'Monitor during interview'
            })

        # Check specificity (WARNING)
        specificity = self._calculate_specificity(resume_text)
        if specificity['is_vague']:
            warning.append({
                'type': 'VAGUE_CONTENT',
                'severity': 'WARNING',
                'description': f"Lack of specific details (score: {specificity['score']}/100)",
                'recommendation': 'Resume lacks concrete metrics and project details'
            })

        # Check terminology errors (WARNING)
        terminology = self.check_terminology(resume_text)
        if terminology['has_errors']:
            for error in terminology['errors']:
                warning.append({
                    'type': 'TERMINOLOGY_ERROR',
                    'severity': 'WARNING',
                    'description': f"Incorrect terminology: '{error['found']}' (should be '{error['should_be']}')",
                    'recommendation': 'Candidate may lack real-world experience with the technology'
                })

        # Check career progression (WARNING)
        progression = self._check_career_progression(resume_text)
        if progression['has_rapid_progression']:
            warning.append({
                'type': 'RAPID_PROGRESSION',
                'severity': 'WARNING',
                'description': 'Unrealistic career progression detected',
                'recommendation': 'Verify employment history and responsibilities'
            })

        return {
            'critical': critical,
            'warning': warning,
            'minor': minor,
            'total_count': len(critical) + len(warning) + len(minor)
        }
