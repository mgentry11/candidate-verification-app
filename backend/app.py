from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import shutil
from datetime import datetime
from dotenv import load_dotenv
from verification.resume_analyzer import ResumeAnalyzer
from verification.linkedin_checker import LinkedInChecker
from verification.online_presence import OnlinePresenceChecker
from verification.ai_detector import AIContentDetector
from verification.report_generator import ReportGenerator

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize verification modules
resume_analyzer = ResumeAnalyzer()
linkedin_checker = LinkedInChecker()
presence_checker = OnlinePresenceChecker()
ai_detector = AIContentDetector()
report_generator = ReportGenerator()

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'version': '1.0.0'})

@app.route('/api/verify/resume', methods=['POST'])
def verify_resume():
    """Analyze resume for authenticity"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        job_description = request.form.get('job_description', '')

        # Parse resume
        resume_text = resume_analyzer.extract_text(file)

        # Run all verification checks
        results = {
            'resume_analysis': resume_analyzer.analyze_authenticity(resume_text, job_description),
            'ai_detection': ai_detector.detect_ai_content(resume_text),
            'consistency_check': resume_analyzer.check_consistency(resume_text),
            'terminology_check': resume_analyzer.check_terminology(resume_text),
            'red_flags': resume_analyzer.identify_red_flags(resume_text, job_description)
        }

        # Calculate overall risk score (0-100, higher = more suspicious)
        risk_score = calculate_risk_score(results)
        results['risk_score'] = risk_score
        results['risk_level'] = get_risk_level(risk_score)

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/verify/linkedin', methods=['POST'])
def verify_linkedin():
    """Verify LinkedIn profile authenticity"""
    try:
        data = request.get_json()
        profile_url = data.get('profile_url')

        if not profile_url:
            return jsonify({'error': 'No profile URL provided'}), 400

        results = linkedin_checker.verify_profile(profile_url)
        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/verify/online-presence', methods=['POST'])
def verify_online_presence():
    """Check candidate's online presence across multiple platforms"""
    try:
        data = request.get_json()
        candidate_info = {
            'name': data.get('name'),
            'email': data.get('email'),
            'phone': data.get('phone'),
            'location': data.get('location')
        }

        results = presence_checker.verify_presence(candidate_info)
        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/verify/comprehensive', methods=['POST'])
def comprehensive_verification():
    """Run all verification checks on a candidate"""
    try:
        # Get resume file
        if 'file' not in request.files:
            return jsonify({'error': 'No resume file provided'}), 400

        file = request.files['file']

        # Get additional data
        job_description = request.form.get('job_description', '')
        linkedin_url = request.form.get('linkedin_url', '')
        name = request.form.get('name', '')
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        location = request.form.get('location', '')

        # Parse resume
        resume_text = resume_analyzer.extract_text(file)

        # Run all checks
        results = {
            'candidate_info': {
                'name': name,
                'email': email,
                'linkedin': linkedin_url
            },
            'resume_verification': {
                'authenticity': resume_analyzer.analyze_authenticity(resume_text, job_description),
                'ai_detection': ai_detector.detect_ai_content(resume_text),
                'consistency': resume_analyzer.check_consistency(resume_text),
                'terminology': resume_analyzer.check_terminology(resume_text),
                'red_flags': resume_analyzer.identify_red_flags(resume_text, job_description)
            },
            'online_verification': {
                'linkedin': linkedin_checker.verify_profile(linkedin_url) if linkedin_url else None,
                'presence': presence_checker.verify_presence({
                    'name': name,
                    'email': email,
                    'phone': phone,
                    'location': location
                })
            }
        }

        # Calculate comprehensive risk score
        risk_score = calculate_comprehensive_risk(results)
        results['overall_risk_score'] = risk_score
        results['overall_risk_level'] = get_risk_level(risk_score)
        results['recommendation'] = get_recommendation(risk_score, results)

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/verify/batch', methods=['POST'])
def batch_verification():
    """Process multiple resumes from uploaded files"""
    try:
        files = request.files.getlist('files')

        if not files or len(files) == 0:
            return jsonify({'error': 'No files provided'}), 400

        job_description = request.form.get('job_description', '')

        results = []
        processed = 0
        failed = 0

        for file in files:
            try:
                # Skip non-resume files
                filename = file.filename.lower()
                if not (filename.endswith('.pdf') or filename.endswith('.docx') or filename.endswith('.txt')):
                    continue

                # Extract candidate name from filename (remove extension)
                candidate_name = os.path.splitext(file.filename)[0]

                # Parse resume
                resume_text = resume_analyzer.extract_text(file)

                # Run verification checks
                resume_verification = {
                    'authenticity': resume_analyzer.analyze_authenticity(resume_text, job_description),
                    'ai_detection': ai_detector.detect_ai_content(resume_text),
                    'consistency': resume_analyzer.check_consistency(resume_text),
                    'terminology': resume_analyzer.check_terminology(resume_text),
                    'red_flags': resume_analyzer.identify_red_flags(resume_text, job_description)
                }

                # Calculate risk score
                risk_score = calculate_risk_score({
                    'ai_detection': resume_verification['ai_detection'],
                    'red_flags': resume_verification['red_flags'],
                    'consistency_check': resume_verification['consistency']
                })

                # Compile result
                result = {
                    'filename': file.filename,
                    'candidate_name': candidate_name,
                    'risk_score': risk_score,
                    'risk_level': get_risk_level(risk_score),
                    'ai_generated': resume_verification['ai_detection'].get('is_ai_generated', False),
                    'ai_confidence': resume_verification['ai_detection'].get('confidence', 0),
                    'critical_flags': len(resume_verification['red_flags'].get('critical', [])),
                    'warning_flags': len(resume_verification['red_flags'].get('warning', [])),
                    'minor_flags': len(resume_verification['red_flags'].get('minor', [])),
                    'trap_terms_found': resume_verification['authenticity'].get('trap_terms_found', {}).get('has_trap_terms', False),
                    'buzzword_density': resume_verification['authenticity'].get('buzzword_density', {}).get('density', 0),
                    'specificity_score': resume_verification['authenticity'].get('specificity_score', {}).get('score', 0),
                    'dates_valid': resume_verification['consistency'].get('dates_valid', True),
                    'total_experience_years': resume_verification['consistency'].get('total_experience_years', 0),
                    'recommendation': get_recommendation(risk_score, {'resume_verification': resume_verification}),
                    'detailed_results': resume_verification
                }

                results.append(result)
                processed += 1

            except Exception as e:
                failed += 1
                results.append({
                    'filename': file.filename,
                    'candidate_name': os.path.splitext(file.filename)[0],
                    'error': str(e),
                    'risk_score': 0,
                    'risk_level': 'ERROR'
                })

        # Sort by risk score (highest first)
        results.sort(key=lambda x: x.get('risk_score', 0), reverse=True)

        return jsonify({
            'total_files': len(files),
            'processed': processed,
            'failed': failed,
            'results': results,
            'summary': {
                'critical_risk': sum(1 for r in results if r.get('risk_level') == 'CRITICAL'),
                'high_risk': sum(1 for r in results if r.get('risk_level') == 'HIGH'),
                'medium_risk': sum(1 for r in results if r.get('risk_level') == 'MEDIUM'),
                'low_risk': sum(1 for r in results if r.get('risk_level') == 'LOW'),
                'minimal_risk': sum(1 for r in results if r.get('risk_level') == 'MINIMAL'),
                'ai_generated_count': sum(1 for r in results if r.get('ai_generated')),
                'trap_terms_count': sum(1 for r in results if r.get('trap_terms_found'))
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    """Generate HTML or text report from batch results"""
    try:
        data = request.get_json()
        batch_results = data.get('results')
        report_format = data.get('format', 'html')  # html or text

        if not batch_results:
            return jsonify({'error': 'No results provided'}), 400

        if report_format == 'html':
            html_content = report_generator.generate_html_report(batch_results)
            return jsonify({
                'format': 'html',
                'content': html_content
            })
        else:
            text_content = report_generator.generate_text_report(batch_results)
            return jsonify({
                'format': 'text',
                'content': text_content
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/organize-files', methods=['POST'])
def organize_files():
    """Organize uploaded files by risk level into folders"""
    try:
        # Get the output directory from form
        output_dir = request.form.get('output_directory')
        if not output_dir:
            return jsonify({'error': 'No output directory specified'}), 400

        # Validate output directory exists or create it
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Get files and process them
        files = request.files.getlist('files')
        job_description = request.form.get('job_description', '')

        if not files or len(files) == 0:
            return jsonify({'error': 'No files provided'}), 400

        # Create folders for each risk level
        folders = {
            'CRITICAL': os.path.join(output_dir, '1_CRITICAL_RISK'),
            'HIGH': os.path.join(output_dir, '2_HIGH_RISK'),
            'MEDIUM': os.path.join(output_dir, '3_MEDIUM_RISK'),
            'LOW': os.path.join(output_dir, '4_LOW_RISK'),
            'MINIMAL': os.path.join(output_dir, '5_SAFE_TO_PROCEED')
        }

        for folder in folders.values():
            os.makedirs(folder, exist_ok=True)

        results = []
        organized_count = 0

        for file in files:
            try:
                filename = file.filename.lower()
                if not (filename.endswith('.pdf') or filename.endswith('.docx') or filename.endswith('.txt')):
                    continue

                # Parse and analyze resume
                resume_text = resume_analyzer.extract_text(file)
                resume_verification = {
                    'authenticity': resume_analyzer.analyze_authenticity(resume_text, job_description),
                    'ai_detection': ai_detector.detect_ai_content(resume_text),
                    'consistency': resume_analyzer.check_consistency(resume_text),
                    'terminology': resume_analyzer.check_terminology(resume_text),
                    'red_flags': resume_analyzer.identify_red_flags(resume_text, job_description)
                }

                risk_score = calculate_risk_score({
                    'ai_detection': resume_verification['ai_detection'],
                    'red_flags': resume_verification['red_flags'],
                    'consistency_check': resume_verification['consistency']
                })

                risk_level = get_risk_level(risk_score)

                # Copy file to appropriate folder
                destination_folder = folders[risk_level]
                destination_path = os.path.join(destination_folder, file.filename)

                # Save file to disk first (from file upload)
                file.seek(0)  # Reset file pointer
                with open(destination_path, 'wb') as f:
                    f.write(file.read())

                organized_count += 1

                results.append({
                    'filename': file.filename,
                    'risk_level': risk_level,
                    'destination': destination_folder
                })

            except Exception as e:
                results.append({
                    'filename': file.filename,
                    'error': str(e)
                })

        # Generate summary report in output directory
        batch_results_summary = {
            'processed': organized_count,
            'results': results,
            'summary': {
                'critical_risk': sum(1 for r in results if r.get('risk_level') == 'CRITICAL'),
                'high_risk': sum(1 for r in results if r.get('risk_level') == 'HIGH'),
                'medium_risk': sum(1 for r in results if r.get('risk_level') == 'MEDIUM'),
                'low_risk': sum(1 for r in results if r.get('risk_level') == 'LOW'),
                'minimal_risk': sum(1 for r in results if r.get('risk_level') == 'MINIMAL'),
                'ai_generated_count': 0,  # Would need full results for this
                'trap_terms_count': 0
            }
        }

        # Save summary text file
        summary_path = os.path.join(output_dir, 'ORGANIZATION_SUMMARY.txt')
        with open(summary_path, 'w') as f:
            f.write(f"File Organization Summary\n")
            f.write(f"========================\n\n")
            f.write(f"Total Files Organized: {organized_count}\n\n")
            f.write(f"Critical Risk: {batch_results_summary['summary']['critical_risk']} files → {folders['CRITICAL']}\n")
            f.write(f"High Risk: {batch_results_summary['summary']['high_risk']} files → {folders['HIGH']}\n")
            f.write(f"Medium Risk: {batch_results_summary['summary']['medium_risk']} files → {folders['MEDIUM']}\n")
            f.write(f"Low Risk: {batch_results_summary['summary']['low_risk']} files → {folders['LOW']}\n")
            f.write(f"Safe to Proceed: {batch_results_summary['summary']['minimal_risk']} files → {folders['MINIMAL']}\n")

        return jsonify({
            'success': True,
            'organized_count': organized_count,
            'output_directory': output_dir,
            'folders': folders,
            'results': results,
            'summary': batch_results_summary['summary']
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calculate_risk_score(results):
    """Calculate risk score based on verification results"""
    score = 0

    # AI detection (0-30 points)
    if results['ai_detection'].get('is_ai_generated'):
        score += results['ai_detection'].get('confidence', 0) * 30

    # Red flags (0-40 points)
    red_flags = results['red_flags']
    score += len(red_flags.get('critical', [])) * 10
    score += len(red_flags.get('warning', [])) * 5
    score += len(red_flags.get('minor', [])) * 2

    # Consistency issues (0-30 points)
    consistency = results['consistency_check']
    if not consistency.get('dates_valid'):
        score += 15
    if not consistency.get('career_progression_valid'):
        score += 15

    return min(score, 100)

def calculate_comprehensive_risk(results):
    """Calculate comprehensive risk score"""
    score = 0
    weights = {
        'resume': 0.4,
        'linkedin': 0.3,
        'online_presence': 0.3
    }

    # Resume score
    resume_score = 0
    resume_data = results['resume_verification']

    if resume_data['ai_detection'].get('is_ai_generated'):
        resume_score += resume_data['ai_detection'].get('confidence', 0) * 30

    red_flags = resume_data['red_flags']
    resume_score += len(red_flags.get('critical', [])) * 10
    resume_score += len(red_flags.get('warning', [])) * 5

    score += resume_score * weights['resume']

    # LinkedIn score
    linkedin_data = results['online_verification'].get('linkedin')
    if linkedin_data:
        linkedin_score = 0
        if linkedin_data.get('recently_created'):
            linkedin_score += 30
        if not linkedin_data.get('has_verification_badge'):
            linkedin_score += 20
        if linkedin_data.get('low_connections'):
            linkedin_score += 25
        if linkedin_data.get('vague_experience'):
            linkedin_score += 25
        score += linkedin_score * weights['linkedin']

    # Online presence score
    presence_data = results['online_verification'].get('presence', {})
    presence_score = 0
    if not presence_data.get('has_linkedin'):
        presence_score += 30
    if not presence_data.get('has_github'):
        presence_score += 20
    if not presence_data.get('has_google_presence'):
        presence_score += 30
    if presence_data.get('email_suspicious'):
        presence_score += 20

    score += presence_score * weights['online_presence']

    return min(score, 100)

def get_risk_level(score):
    """Convert risk score to risk level"""
    if score >= 70:
        return 'CRITICAL'
    elif score >= 50:
        return 'HIGH'
    elif score >= 30:
        return 'MEDIUM'
    elif score >= 15:
        return 'LOW'
    else:
        return 'MINIMAL'

def get_recommendation(score, results):
    """Generate recommendation based on risk score"""
    if score >= 70:
        return 'REJECT - Multiple critical fraud indicators detected. Do not proceed with this candidate.'
    elif score >= 50:
        return 'CAUTION - Significant red flags present. Conduct thorough additional verification before proceeding.'
    elif score >= 30:
        return 'INVESTIGATE - Some concerning patterns detected. Additional screening recommended.'
    elif score >= 15:
        return 'PROCEED WITH NORMAL SCREENING - Minor concerns noted. Standard interview process recommended.'
    else:
        return 'PROCEED - No significant fraud indicators detected. Continue with normal hiring process.'

if __name__ == '__main__':
    # Use port 5001 to avoid conflicts with macOS ControlCenter (port 5000)
    import os
    port = int(os.environ.get('FLASK_RUN_PORT', 5001))
    app.run(debug=True, port=port, host='127.0.0.1')
