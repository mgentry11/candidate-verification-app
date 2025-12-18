// Candidate Verification System - Frontend JavaScript

const API_BASE_URL = 'http://localhost:5001/api';

// Tab switching
document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
        const tabName = button.dataset.tab;

        // Remove active class from all tabs and buttons
        document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

        // Add active class to clicked button and corresponding content
        button.classList.add('active');
        document.getElementById(tabName).classList.add('active');
    });
});

// File upload handling
document.querySelectorAll('input[type="file"]:not(#batch-files)').forEach(input => {
    input.addEventListener('change', (e) => {
        const fileName = e.target.files[0]?.name || 'No file selected';
        const fileNameSpan = e.target.parentElement.querySelector('.file-name');
        if (fileNameSpan) {
            fileNameSpan.textContent = fileName;
        }
    });
});

// Batch file upload handling
const batchFilesInput = document.getElementById('batch-files');
if (batchFilesInput) {
    batchFilesInput.addEventListener('change', (e) => {
        const fileCount = e.target.files.length;
        const fileCountSpan = document.getElementById('batch-file-count');
        if (fileCountSpan) {
            fileCountSpan.textContent = fileCount > 0 ?
                `${fileCount} file${fileCount > 1 ? 's' : ''} selected` :
                'No files selected';
        }
    });
}

// Comprehensive Form Submission
document.getElementById('comprehensive-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);
    const button = e.target.querySelector('button[type="submit"]');
    const btnText = button.querySelector('.btn-text');
    const loader = button.querySelector('.loader');

    // Show loading state
    button.disabled = true;
    btnText.style.display = 'none';
    loader.style.display = 'block';

    try {
        const response = await fetch(`${API_BASE_URL}/verify/comprehensive`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            displayComprehensiveResults(data);
        } else {
            displayError(data.error || 'Verification failed');
        }
    } catch (error) {
        displayError('Network error: ' + error.message);
    } finally {
        button.disabled = false;
        btnText.style.display = 'inline';
        loader.style.display = 'none';
    }
});

// Resume Only Form Submission
document.getElementById('resume-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);
    const button = e.target.querySelector('button[type="submit"]');
    const btnText = button.querySelector('.btn-text');
    const loader = button.querySelector('.loader');

    button.disabled = true;
    btnText.style.display = 'none';
    loader.style.display = 'block';

    try {
        const response = await fetch(`${API_BASE_URL}/verify/resume`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            displayResumeResults(data);
        } else {
            displayError(data.error || 'Analysis failed', 'resume-results');
        }
    } catch (error) {
        displayError('Network error: ' + error.message, 'resume-results');
    } finally {
        button.disabled = false;
        btnText.style.display = 'inline';
        loader.style.display = 'none';
    }
});

// LinkedIn Form Submission
document.getElementById('linkedin-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const profileUrl = document.getElementById('linkedin-profile-url').value;
    const button = e.target.querySelector('button[type="submit"]');
    const btnText = button.querySelector('.btn-text');
    const loader = button.querySelector('.loader');

    button.disabled = true;
    btnText.style.display = 'none';
    loader.style.display = 'block';

    try {
        const response = await fetch(`${API_BASE_URL}/verify/linkedin`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ profile_url: profileUrl })
        });

        const data = await response.json();

        if (response.ok) {
            displayLinkedInResults(data);
        } else {
            displayError(data.error || 'Verification failed', 'linkedin-results');
        }
    } catch (error) {
        displayError('Network error: ' + error.message, 'linkedin-results');
    } finally {
        button.disabled = false;
        btnText.style.display = 'inline';
        loader.style.display = 'none';
    }
});

// Display Functions

function displayComprehensiveResults(data) {
    const resultsSection = document.getElementById('results-section');
    const resultsContent = document.getElementById('results-content');

    let html = `
        <!-- Overall Risk Score -->
        <div class="risk-score">
            <h3>Overall Risk Assessment</h3>
            <div class="risk-score-value" style="color: ${getRiskColor(data.overall_risk_level)}">
                ${data.overall_risk_score.toFixed(0)}
            </div>
            <div class="risk-score-label risk-${data.overall_risk_level}">
                ${data.overall_risk_level} RISK
            </div>
            <p style="margin-top: 15px; text-align: center; max-width: 600px;">
                <strong>Recommendation:</strong> ${data.recommendation}
            </p>
        </div>

        <!-- Resume Verification -->
        <div class="data-section">
            <h3>📄 Resume Analysis</h3>
            ${renderResumeAnalysis(data.resume_verification)}
        </div>

        <!-- AI Detection -->
        <div class="data-section">
            <h3>🤖 AI Content Detection</h3>
            ${renderAIDetection(data.resume_verification.ai_detection)}
        </div>

        <!-- Red Flags -->
        ${renderRedFlags(data.resume_verification.red_flags)}

        <!-- Online Verification -->
        ${renderOnlineVerification(data.online_verification)}
    `;

    resultsContent.innerHTML = html;
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function displayResumeResults(data) {
    const resultsSection = document.getElementById('resume-results');
    const resultsContent = document.getElementById('resume-results-content');

    let html = `
        <!-- Risk Score -->
        <div class="risk-score">
            <h3>Resume Risk Score</h3>
            <div class="risk-score-value" style="color: ${getRiskColor(data.risk_level)}">
                ${data.risk_score.toFixed(0)}
            </div>
            <div class="risk-score-label risk-${data.risk_level}">
                ${data.risk_level} RISK
            </div>
        </div>

        <!-- Resume Analysis -->
        <div class="data-section">
            <h3>Resume Analysis</h3>
            ${renderResumeAnalysis(data.resume_analysis)}
        </div>

        <!-- AI Detection -->
        <div class="data-section">
            <h3>AI Content Detection</h3>
            ${renderAIDetection(data.ai_detection)}
        </div>

        <!-- Red Flags -->
        ${renderRedFlags(data.red_flags)}

        <!-- Consistency Check -->
        <div class="data-section">
            <h3>Consistency Check</h3>
            ${renderConsistencyCheck(data.consistency_check)}
        </div>
    `;

    resultsContent.innerHTML = html;
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function displayLinkedInResults(data) {
    const resultsSection = document.getElementById('linkedin-results');
    const resultsContent = document.getElementById('linkedin-results-content');

    let html = `
        <!-- Automated Checks -->
        ${data.automated_checks ? `
        <div class="data-section">
            <h3>Automated Checks</h3>
            <div class="risk-score">
                <div class="risk-score-value" style="color: ${getRiskColor(data.risk_level)}">
                    ${data.risk_score}
                </div>
                <div class="risk-score-label risk-${data.risk_level}">
                    ${data.risk_level} RISK
                </div>
            </div>
            ${renderAutomatedChecks(data.automated_checks)}
        </div>
        ` : ''}

        <!-- Manual Verification Checklist -->
        <div class="data-section">
            <h3>📋 Manual Verification Checklist</h3>
            <p style="color: var(--text-secondary); margin-bottom: 20px;">
                Due to LinkedIn's anti-scraping measures, please perform these manual checks:
            </p>
            ${renderManualChecks(data.manual_checks_required)}
        </div>

        <!-- Wayback Machine -->
        ${data.automated_checks?.wayback_machine_check?.has_archive ? `
        <div class="data-section">
            <h3>🕒 Historical Profile Data</h3>
            <p style="color: var(--accent-success); margin-bottom: 10px;">
                ✓ Archive found! Check for account rotation:
            </p>
            <a href="${data.automated_checks.wayback_machine_check.archive_url}"
               target="_blank"
               style="color: var(--accent-info); text-decoration: underline;">
                View Archived Profile →
            </a>
            <p style="color: var(--text-secondary); margin-top: 10px;">
                ${data.automated_checks.wayback_machine_check.recommendation}
            </p>
        </div>
        ` : ''}
    `;

    resultsContent.innerHTML = html;
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Render Helper Functions

function renderResumeAnalysis(analysis) {
    if (!analysis || !analysis.authenticity) return '<p>No data available</p>';

    const auth = analysis.authenticity;
    return `
        <div class="data-row">
            <span class="data-label">Generic Content Match:</span>
            <span class="data-value">
                ${auth.generic_content?.match_percentage || 0}%
                ${auth.generic_content?.warning ? '<span class="badge badge-warning">WARNING</span>' : ''}
            </span>
        </div>
        <div class="data-row">
            <span class="data-label">Buzzword Density:</span>
            <span class="data-value">
                ${auth.buzzword_density?.density || 0}%
                ${auth.buzzword_density?.is_excessive ? '<span class="badge badge-warning">EXCESSIVE</span>' : ''}
            </span>
        </div>
        <div class="data-row">
            <span class="data-label">Specificity Score:</span>
            <span class="data-value">
                ${auth.specificity_score?.score || 0}/100
                ${auth.specificity_score?.is_vague ? '<span class="badge badge-warning">VAGUE</span>' : '<span class="badge badge-success">GOOD</span>'}
            </span>
        </div>
        <div class="data-row">
            <span class="data-label">Trap Terms:</span>
            <span class="data-value">
                ${auth.trap_terms_found?.has_trap_terms ?
                    `<span class="badge badge-danger">FOUND: ${auth.trap_terms_found.terms_found.join(', ')}</span>` :
                    '<span class="badge badge-success">NONE</span>'
                }
            </span>
        </div>
    `;
}

function renderAIDetection(aiData) {
    if (!aiData) return '<p>No data available</p>';

    return `
        <div class="data-row">
            <span class="data-label">AI Generated:</span>
            <span class="data-value">
                ${aiData.is_ai_generated ?
                    '<span class="badge badge-danger">YES</span>' :
                    '<span class="badge badge-success">NO</span>'
                }
            </span>
        </div>
        <div class="data-row">
            <span class="data-label">Confidence:</span>
            <span class="data-value">${(aiData.confidence * 100).toFixed(1)}%</span>
        </div>
        <div class="data-row">
            <span class="data-label">Pattern Matches:</span>
            <span class="data-value">${aiData.pattern_matches || 0}</span>
        </div>
        ${aiData.indicators && aiData.indicators.length > 0 ? `
        <div style="margin-top: 15px;">
            <strong>Indicators:</strong>
            <ul style="margin-left: 20px; margin-top: 10px;">
                ${aiData.indicators.map(ind => `<li>${ind.type}: ${ind.description}</li>`).join('')}
            </ul>
        </div>
        ` : ''}
    `;
}

function renderRedFlags(redFlags) {
    if (!redFlags || redFlags.total_count === 0) {
        return `
        <div class="data-section">
            <h3>✅ Red Flags</h3>
            <p style="color: var(--accent-success);">No red flags detected!</p>
        </div>
        `;
    }

    let html = '<div class="red-flags"><h3>🚩 Red Flags Detected</h3>';

    if (redFlags.critical && redFlags.critical.length > 0) {
        html += '<h4 style="color: var(--accent-danger); margin-top: 20px;">Critical Issues</h4>';
        redFlags.critical.forEach(flag => {
            html += `
            <div class="flag-item critical">
                <h4>${flag.type}</h4>
                <p>${flag.description}</p>
                ${flag.recommendation ? `<p class="recommendation">→ ${flag.recommendation}</p>` : ''}
            </div>
            `;
        });
    }

    if (redFlags.warning && redFlags.warning.length > 0) {
        html += '<h4 style="color: var(--accent-warning); margin-top: 20px;">Warnings</h4>';
        redFlags.warning.forEach(flag => {
            html += `
            <div class="flag-item warning">
                <h4>${flag.type}</h4>
                <p>${flag.description}</p>
                ${flag.recommendation ? `<p class="recommendation">→ ${flag.recommendation}</p>` : ''}
            </div>
            `;
        });
    }

    if (redFlags.minor && redFlags.minor.length > 0) {
        html += '<h4 style="color: var(--accent-info); margin-top: 20px;">Minor Concerns</h4>';
        redFlags.minor.forEach(flag => {
            html += `
            <div class="flag-item minor">
                <h4>${flag.type}</h4>
                <p>${flag.description}</p>
                ${flag.recommendation ? `<p class="recommendation">→ ${flag.recommendation}</p>` : ''}
            </div>
            `;
        });
    }

    html += '</div>';
    return html;
}

function renderConsistencyCheck(consistency) {
    if (!consistency) return '<p>No data available</p>';

    return `
        <div class="data-row">
            <span class="data-label">Dates Valid:</span>
            <span class="data-value">
                ${consistency.dates_valid ?
                    '<span class="badge badge-success">YES</span>' :
                    '<span class="badge badge-danger">NO</span>'
                }
            </span>
        </div>
        <div class="data-row">
            <span class="data-label">Has Overlaps:</span>
            <span class="data-value">
                ${consistency.has_overlaps ?
                    '<span class="badge badge-warning">YES</span>' :
                    '<span class="badge badge-success">NO</span>'
                }
            </span>
        </div>
        <div class="data-row">
            <span class="data-label">Total Experience:</span>
            <span class="data-value">${consistency.total_experience_years} years</span>
        </div>
        ${consistency.date_errors && consistency.date_errors.length > 0 ? `
        <div style="margin-top: 15px;">
            <strong style="color: var(--accent-danger);">Date Errors:</strong>
            <ul style="margin-left: 20px; margin-top: 10px; color: var(--text-secondary);">
                ${consistency.date_errors.map(err => `<li>${err}</li>`).join('')}
            </ul>
        </div>
        ` : ''}
    `;
}

function renderOnlineVerification(onlineData) {
    if (!onlineData) return '';

    let html = '<div class="data-section"><h3>🌐 Online Presence Verification</h3>';

    // Email
    if (onlineData.presence?.checks?.email) {
        const email = onlineData.presence.checks.email;
        html += `
        <div style="margin-bottom: 20px;">
            <h4>Email Verification</h4>
            <div class="data-row">
                <span class="data-label">Valid:</span>
                <span class="data-value">
                    ${email.valid ?
                        '<span class="badge badge-success">YES</span>' :
                        '<span class="badge badge-danger">NO</span>'
                    }
                </span>
            </div>
            ${email.is_disposable ? '<p style="color: var(--accent-danger);">⚠️ Disposable email detected!</p>' : ''}
            ${email.is_suspicious ? '<p style="color: var(--accent-warning);">⚠️ Suspicious patterns detected</p>' : ''}
        </div>
        `;
    }

    // GitHub
    if (onlineData.presence?.checks?.github) {
        const github = onlineData.presence.checks.github;
        html += `
        <div style="margin-bottom: 20px;">
            <h4>GitHub Presence</h4>
            <div class="data-row">
                <span class="data-label">Profile Found:</span>
                <span class="data-value">
                    ${github.exists ?
                        '<span class="badge badge-success">YES</span>' :
                        '<span class="badge badge-warning">NO</span>'
                    }
                </span>
            </div>
            ${github.profiles_found && github.profiles_found.length > 0 ? `
                ${github.profiles_found.map(profile => `
                    <p style="margin-top: 10px;">
                        <a href="${profile.profile_url}" target="_blank" style="color: var(--accent-info);">
                            ${profile.username}
                        </a> - ${profile.public_repos} repos, ${profile.followers} followers
                    </p>
                `).join('')}
            ` : ''}
        </div>
        `;
    }

    // OSINT Recommendations
    if (onlineData.presence?.osint_recommendations) {
        html += `
        <div style="margin-top: 25px;">
            <h4>🔎 Recommended OSINT Checks</h4>
            ${onlineData.presence.osint_recommendations.map(tool => `
                <div style="background: var(--bg-primary); padding: 15px; border-radius: 6px; margin-bottom: 12px;">
                    <strong>${tool.tool}:</strong> ${tool.purpose}<br>
                    <a href="${tool.url}" target="_blank" style="color: var(--accent-info);">
                        ${tool.url}
                    </a><br>
                    <span style="color: var(--text-secondary); font-size: 0.9rem;">${tool.action}</span>
                </div>
            `).join('')}
        </div>
        `;
    }

    html += '</div>';
    return html;
}

function renderAutomatedChecks(checks) {
    return `
        <div class="data-row">
            <span class="data-label">URL Format Valid:</span>
            <span class="data-value">
                ${checks.url_format_valid ?
                    '<span class="badge badge-success">YES</span>' :
                    '<span class="badge badge-danger">NO</span>'
                }
            </span>
        </div>
        <div class="data-row">
            <span class="data-label">Suspicious Username:</span>
            <span class="data-value">
                ${checks.suspicious_username_pattern ?
                    '<span class="badge badge-warning">YES</span>' :
                    '<span class="badge badge-success">NO</span>'
                }
            </span>
        </div>
        ${checks.username_too_short ? `
        <p style="color: var(--accent-warning); margin-top: 10px;">
            ⚠️ Username is suspiciously short
        </p>
        ` : ''}
    `;
}

function renderManualChecks(checks) {
    if (!checks) return '';

    return checks.map((check, index) => `
        <div style="background: var(--bg-primary); padding: 20px; border-radius: 6px; margin-bottom: 15px; border-left: 4px solid var(--accent-info);">
            <h4 style="color: var(--accent-info); margin-bottom: 10px;">
                ${index + 1}. ${check.check}
            </h4>
            <p style="margin-bottom: 10px;">
                <strong>Instructions:</strong> ${check.instructions}
            </p>
            ${check.red_flag ? `
                <p style="color: var(--accent-danger); margin-bottom: 5px;">
                    🚩 <strong>Red Flag:</strong> ${check.red_flag}
                </p>
            ` : ''}
            ${check.warning ? `
                <p style="color: var(--accent-warning);">
                    ⚠️ <strong>Warning:</strong> ${check.warning}
                </p>
            ` : ''}
        </div>
    `).join('');
}

// Utility Functions

function getRiskColor(level) {
    const colors = {
        'CRITICAL': 'var(--accent-danger)',
        'HIGH': 'var(--accent-warning)',
        'MEDIUM': 'var(--accent-info)',
        'LOW': 'var(--accent-success)',
        'MINIMAL': 'var(--accent-success)'
    };
    return colors[level] || 'var(--text-primary)';
}

function displayError(message, sectionId = 'results-section') {
    const resultsSection = document.getElementById(sectionId);
    const resultsContent = sectionId === 'results-section' ?
        document.getElementById('results-content') :
        document.getElementById(sectionId + '-content');

    resultsContent.innerHTML = `
        <div style="background: rgba(255, 71, 87, 0.1); border: 2px solid var(--accent-danger); border-radius: 8px; padding: 20px; text-align: center;">
            <h3 style="color: var(--accent-danger); margin-bottom: 10px;">Error</h3>
            <p>${message}</p>
        </div>
    `;

    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// ============================================================================
// BATCH PROCESSING FUNCTIONALITY
// ============================================================================

let batchResults = null;
let filteredBatchResults = [];

// Batch Form Submission
document.getElementById('batch-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const filesInput = document.getElementById('batch-files');
    const files = filesInput.files;

    if (!files || files.length === 0) {
        alert('Please select files to process');
        return;
    }

    const formData = new FormData();
    const jobDescription = document.getElementById('job-desc-batch').value;

    // Add all files
    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }

    if (jobDescription) {
        formData.append('job_description', jobDescription);
    }

    const button = document.getElementById('batch-verify-btn');
    const btnText = button.querySelector('.btn-text');
    const loader = button.querySelector('.loader');
    const progressDiv = document.getElementById('batch-progress');

    // Show loading state
    button.disabled = true;
    btnText.style.display = 'none';
    loader.style.display = 'block';
    progressDiv.style.display = 'block';

    try {
        const response = await fetch(`${API_BASE_URL}/verify/batch`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            batchResults = data;
            displayBatchResults(data);
        } else {
            alert('Error: ' + (data.error || 'Batch processing failed'));
        }
    } catch (error) {
        alert('Network error: ' + error.message);
    } finally {
        button.disabled = false;
        btnText.style.display = 'inline';
        loader.style.display = 'none';
        progressDiv.style.display = 'none';
    }
});

function displayBatchResults(data) {
    const resultsSection = document.getElementById('batch-results-section');
    const summaryDiv = document.getElementById('batch-summary');
    const tableDiv = document.getElementById('batch-results-table');

    // Display summary stats
    summaryDiv.innerHTML = `
        <div class="batch-stats-card" style="border-left-color: var(--accent-primary);">
            <h4>Total Processed</h4>
            <div class="stat-value">${data.processed}</div>
        </div>
        <div class="batch-stats-card" style="border-left-color: var(--accent-danger);">
            <h4>Critical Risk</h4>
            <div class="stat-value" style="color: var(--accent-danger);">${data.summary.critical_risk}</div>
        </div>
        <div class="batch-stats-card" style="border-left-color: var(--accent-warning);">
            <h4>High Risk</h4>
            <div class="stat-value" style="color: var(--accent-warning);">${data.summary.high_risk}</div>
        </div>
        <div class="batch-stats-card" style="border-left-color: var(--accent-info);">
            <h4>Medium Risk</h4>
            <div class="stat-value" style="color: var(--accent-info);">${data.summary.medium_risk}</div>
        </div>
        <div class="batch-stats-card" style="border-left-color: var(--accent-success);">
            <h4>Low/Minimal</h4>
            <div class="stat-value" style="color: var(--accent-success);">${data.summary.low_risk + data.summary.minimal_risk}</div>
        </div>
        <div class="batch-stats-card" style="border-left-color: var(--accent-danger);">
            <h4>AI Generated</h4>
            <div class="stat-value">${data.summary.ai_generated_count}</div>
        </div>
        <div class="batch-stats-card" style="border-left-color: var(--accent-danger);">
            <h4>Trap Terms Found</h4>
            <div class="stat-value">${data.summary.trap_terms_count}</div>
        </div>
    `;

    // Set filtered results to all results initially
    filteredBatchResults = [...data.results];

    // Render table
    renderBatchTable(filteredBatchResults);

    // Show results section
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function renderBatchTable(results) {
    const tableDiv = document.getElementById('batch-results-table');

    if (results.length === 0) {
        tableDiv.innerHTML = '<p style="text-align: center; padding: 40px; color: var(--text-secondary);">No results match the current filters</p>';
        return;
    }

    let tableHTML = `
        <table class="batch-table">
            <thead>
                <tr>
                    <th style="width: 40px;">#</th>
                    <th>Candidate Name</th>
                    <th>Risk Score</th>
                    <th>Risk Level</th>
                    <th>AI Generated</th>
                    <th>Red Flags</th>
                    <th>Specificity</th>
                    <th>Experience</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
    `;

    results.forEach((result, index) => {
        const riskColor = getRiskColor(result.risk_level);
        const rowId = `batch-row-${index}`;
        const detailsId = `batch-details-${index}`;

        tableHTML += `
            <tr id="${rowId}" class="result-row">
                <td style="color: var(--text-secondary);">${index + 1}</td>
                <td class="candidate-name">${escapeHtml(result.candidate_name)}</td>
                <td class="risk-score" style="color: ${riskColor};">${result.risk_score.toFixed(0)}</td>
                <td>
                    <span class="badge badge-${result.risk_level === 'CRITICAL' ? 'danger' : result.risk_level === 'HIGH' ? 'warning' : result.risk_level === 'MEDIUM' ? 'info' : 'success'}">
                        ${result.risk_level}
                    </span>
                </td>
                <td>
                    ${result.ai_generated ?
                        `<span class="badge badge-danger">YES (${(result.ai_confidence * 100).toFixed(0)}%)</span>` :
                        `<span class="badge badge-success">NO</span>`
                    }
                </td>
                <td>
                    ${result.critical_flags > 0 ? `<span style="color: var(--accent-danger);">🚩 ${result.critical_flags}</span>` : ''}
                    ${result.warning_flags > 0 ? `<span style="color: var(--accent-warning);"> ⚠️ ${result.warning_flags}</span>` : ''}
                    ${result.minor_flags > 0 ? `<span style="color: var(--accent-info);"> ℹ️ ${result.minor_flags}</span>` : ''}
                    ${result.critical_flags === 0 && result.warning_flags === 0 && result.minor_flags === 0 ? '✅' : ''}
                </td>
                <td>${result.specificity_score}/100</td>
                <td>${result.total_experience_years} yrs</td>
                <td>
                    <button class="expand-btn" onclick="toggleDetails('${detailsId}', '${rowId}')">
                        📋 Details
                    </button>
                </td>
            </tr>
            <tr id="${detailsId}" class="details-row" style="display: none;">
                <td colspan="9" class="details-cell">
                    ${renderCandidateDetails(result)}
                </td>
            </tr>
        `;
    });

    tableHTML += `
            </tbody>
        </table>
    `;

    tableDiv.innerHTML = tableHTML;
}

function renderCandidateDetails(result) {
    const details = result.detailed_results;

    return `
        <div class="details-grid">
            <div class="detail-item">
                <strong>Filename</strong>
                <span>${escapeHtml(result.filename)}</span>
            </div>
            <div class="detail-item">
                <strong>Recommendation</strong>
                <span style="color: ${getRiskColor(result.risk_level)};">${result.recommendation}</span>
            </div>
            <div class="detail-item">
                <strong>Buzzword Density</strong>
                <span>${result.buzzword_density}%</span>
            </div>
            <div class="detail-item">
                <strong>Trap Terms</strong>
                <span>${result.trap_terms_found ? '⚠️ FOUND' : '✅ None'}</span>
            </div>
            <div class="detail-item">
                <strong>Dates Valid</strong>
                <span>${result.dates_valid ? '✅ Yes' : '❌ No'}</span>
            </div>
            <div class="detail-item">
                <strong>AI Confidence</strong>
                <span>${(result.ai_confidence * 100).toFixed(1)}%</span>
            </div>
        </div>

        ${details.red_flags.critical.length > 0 || details.red_flags.warning.length > 0 ? `
        <div style="margin-top: 20px;">
            <h4 style="color: var(--text-primary); margin-bottom: 15px;">Red Flags</h4>
            ${details.red_flags.critical.map(flag => `
                <div style="background: rgba(255, 71, 87, 0.1); border-left: 4px solid var(--accent-danger); padding: 12px; margin-bottom: 10px; border-radius: 4px;">
                    <strong style="color: var(--accent-danger);">${flag.type}</strong>
                    <p style="margin: 5px 0; color: var(--text-secondary);">${flag.description}</p>
                    ${flag.recommendation ? `<p style="margin-top: 5px; color: var(--accent-primary); font-size: 0.9rem;">→ ${flag.recommendation}</p>` : ''}
                </div>
            `).join('')}
            ${details.red_flags.warning.map(flag => `
                <div style="background: rgba(255, 165, 0, 0.1); border-left: 4px solid var(--accent-warning); padding: 12px; margin-bottom: 10px; border-radius: 4px;">
                    <strong style="color: var(--accent-warning);">${flag.type}</strong>
                    <p style="margin: 5px 0; color: var(--text-secondary);">${flag.description}</p>
                    ${flag.recommendation ? `<p style="margin-top: 5px; color: var(--accent-primary); font-size: 0.9rem;">→ ${flag.recommendation}</p>` : ''}
                </div>
            `).join('')}
        </div>
        ` : ''}
    `;
}

function toggleDetails(detailsId, rowId) {
    const detailsRow = document.getElementById(detailsId);
    const mainRow = document.getElementById(rowId);

    if (detailsRow.style.display === 'none') {
        detailsRow.style.display = 'table-row';
        mainRow.classList.add('selected');
    } else {
        detailsRow.style.display = 'none';
        mainRow.classList.remove('selected');
    }
}

// Filtering and Sorting
document.getElementById('risk-filter')?.addEventListener('change', applyFilters);
document.getElementById('sort-order')?.addEventListener('change', applyFilters);
document.getElementById('ai-only-filter')?.addEventListener('change', applyFilters);

function applyFilters() {
    if (!batchResults) return;

    const riskFilter = document.getElementById('risk-filter').value;
    const sortOrder = document.getElementById('sort-order').value;
    const aiOnly = document.getElementById('ai-only-filter').checked;

    // Filter
    let filtered = [...batchResults.results];

    if (riskFilter !== 'all') {
        filtered = filtered.filter(r => r.risk_level === riskFilter);
    }

    if (aiOnly) {
        filtered = filtered.filter(r => r.ai_generated);
    }

    // Sort
    filtered.sort((a, b) => {
        switch (sortOrder) {
            case 'risk-desc':
                return b.risk_score - a.risk_score;
            case 'risk-asc':
                return a.risk_score - b.risk_score;
            case 'name-asc':
                return a.candidate_name.localeCompare(b.candidate_name);
            case 'name-desc':
                return b.candidate_name.localeCompare(a.candidate_name);
            default:
                return 0;
        }
    });

    filteredBatchResults = filtered;
    renderBatchTable(filtered);
}

// CSV Export
document.getElementById('export-csv-btn')?.addEventListener('click', exportToCSV);

// HTML Report Export
document.getElementById('export-html-report-btn')?.addEventListener('click', exportHTMLReport);

// Organize Files
document.getElementById('organize-files-btn')?.addEventListener('click', organizeFilesByRisk);

function exportToCSV() {
    if (!batchResults || !filteredBatchResults) {
        alert('No results to export');
        return;
    }

    // CSV Headers
    const headers = [
        'Candidate Name',
        'Filename',
        'Risk Score',
        'Risk Level',
        'AI Generated',
        'AI Confidence (%)',
        'Critical Flags',
        'Warning Flags',
        'Minor Flags',
        'Trap Terms Found',
        'Buzzword Density (%)',
        'Specificity Score',
        'Dates Valid',
        'Total Experience (years)',
        'Recommendation'
    ];

    // CSV Rows
    const rows = filteredBatchResults.map(result => [
        result.candidate_name,
        result.filename,
        result.risk_score.toFixed(2),
        result.risk_level,
        result.ai_generated ? 'Yes' : 'No',
        (result.ai_confidence * 100).toFixed(1),
        result.critical_flags,
        result.warning_flags,
        result.minor_flags,
        result.trap_terms_found ? 'Yes' : 'No',
        result.buzzword_density.toFixed(2),
        result.specificity_score,
        result.dates_valid ? 'Yes' : 'No',
        result.total_experience_years,
        result.recommendation
    ]);

    // Build CSV content
    let csvContent = headers.map(h => `"${h}"`).join(',') + '\n';
    rows.forEach(row => {
        csvContent += row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(',') + '\n';
    });

    // Download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);

    const timestamp = new Date().toISOString().split('T')[0];
    link.setAttribute('href', url);
    link.setAttribute('download', `candidate_verification_results_${timestamp}.csv`);
    link.style.visibility = 'hidden';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function exportHTMLReport() {
    if (!batchResults) {
        alert('No results to export');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/generate-report`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                results: batchResults,
                format: 'html'
            })
        });

        const data = await response.json();

        if (response.ok) {
            // Create blob and download
            const blob = new Blob([data.content], { type: 'text/html' });
            const link = document.createElement('a');
            const url = URL.createObjectURL(blob);

            const timestamp = new Date().toISOString().split('T')[0];
            link.setAttribute('href', url);
            link.setAttribute('download', `candidate_verification_report_${timestamp}.html`);
            link.style.visibility = 'hidden';

            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            alert('✅ HTML report downloaded successfully!\\n\\nOpen the HTML file in your browser to view the detailed report with all red flags.');
        } else {
            alert('Error generating report: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        alert('Network error: ' + error.message);
    }
}

async function organizeFilesByRisk() {
    if (!batchResults) {
        alert('No results available. Please process resumes first.');
        return;
    }

    // Prompt user for output directory
    const outputDir = prompt(
        '📁 Enter the directory path where you want to organize the resumes:\\n\\n' +
        'Resumes will be organized into folders:\\n' +
        '  • 1_CRITICAL_RISK\\n' +
        '  • 2_HIGH_RISK\\n' +
        '  • 3_MEDIUM_RISK\\n' +
        '  • 4_LOW_RISK\\n' +
        '  • 5_SAFE_TO_PROCEED\\n\\n' +
        'Example: /Users/yourname/Desktop/Sorted_Resumes',
        '/Users/' + (navigator.platform.includes('Mac') ? (document.location.hostname || 'yourname') : 'yourname') + '/Desktop/Sorted_Resumes'
    );

    if (!outputDir) {
        return; // User cancelled
    }

    // Show loading message
    const originalResults = batchResults;

    if (!confirm(
        `This will:\\n\\n` +
        `1. Re-upload and re-analyze all ${batchResults.total_files} resumes\\n` +
        `2. Sort them into risk-level folders in:\\n   ${outputDir}\\n` +
        `3. Generate a summary report\\n\\n` +
        `This may take a few minutes. Continue?`
    )) {
        return;
    }

    // Get the original files
    const filesInput = document.getElementById('batch-files');
    const files = filesInput.files;

    if (!files || files.length === 0) {
        alert('⚠️ Original files are no longer available. Please re-select your resume folder and run batch processing again.');
        return;
    }

    const formData = new FormData();
    formData.append('output_directory', outputDir);

    // Add all files
    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }

    // Add job description if exists
    const jobDescription = document.getElementById('job-desc-batch').value;
    if (jobDescription) {
        formData.append('job_description', jobDescription);
    }

    // Show progress
    const progressMessage = document.createElement('div');
    progressMessage.style.cssText = 'position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: var(--bg-card); padding: 30px; border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.5); z-index: 10000; text-align: center; min-width: 300px;';
    progressMessage.innerHTML = `
        <h3 style="color: var(--accent-primary); margin-bottom: 15px;">📁 Organizing Files...</h3>
        <p style="color: var(--text-secondary); margin-bottom: 20px;">Processing ${files.length} resumes</p>
        <div style="background: var(--bg-secondary); height: 8px; border-radius: 4px; overflow: hidden;">
            <div id="organize-progress" style="background: var(--accent-primary); height: 100%; width: 30%; transition: width 0.3s ease;"></div>
        </div>
        <p style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 15px;">Please wait...</p>
    `;
    document.body.appendChild(progressMessage);

    try {
        const response = await fetch(`${API_BASE_URL}/organize-files`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        document.body.removeChild(progressMessage);

        if (response.ok) {
            const summary = data.summary;
            alert(
                `✅ Files organized successfully!\\n\\n` +
                `Output Directory: ${outputDir}\\n\\n` +
                `Files organized:\\n` +
                `  🚨 Critical Risk: ${summary.critical_risk}\\n` +
                `  ⚠️  High Risk: ${summary.high_risk}\\n` +
                `  🔍 Medium Risk: ${summary.medium_risk}\\n` +
                `  ℹ️  Low Risk: ${summary.low_risk}\\n` +
                `  ✅ Safe to Proceed: ${summary.minimal_risk}\\n\\n` +
                `A summary file has been created in the output directory.`
            );

            // Ask if they want to open the folder (macOS only)
            if (navigator.platform.includes('Mac')) {
                if (confirm('Open the output folder in Finder?')) {
                    // This won't work from browser, show instructions instead
                    alert(`To open the folder:\\n\\n1. Open Finder\\n2. Press Cmd+Shift+G\\n3. Paste: ${outputDir}\\n4. Press Enter`);
                }
            }
        } else {
            alert('Error organizing files: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        document.body.removeChild(progressMessage);
        alert('Network error: ' + error.message);
    }
}

// Make toggleDetails available globally
window.toggleDetails = toggleDetails;
