"""
Report Generator Module
Generates detailed HTML and text reports for batch verification results.
"""

from datetime import datetime

class ReportGenerator:
    def __init__(self):
        pass

    def generate_html_report(self, batch_results, output_path=None):
        """Generate detailed HTML report"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Candidate Verification Report - {timestamp}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1a1a2e;
            color: #eaeaea;
            padding: 40px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: #16213e;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}
        h1 {{
            color: #e94560;
            border-bottom: 3px solid #e94560;
            padding-bottom: 15px;
            margin-bottom: 30px;
        }}
        h2 {{
            color: #4dabf7;
            margin-top: 40px;
            margin-bottom: 20px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .stat-card {{
            background: #0f3460;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid #e94560;
        }}
        .stat-card h3 {{
            color: #a0a0a0;
            font-size: 0.9rem;
            margin-bottom: 10px;
            text-transform: uppercase;
        }}
        .stat-value {{
            font-size: 2.5rem;
            font-weight: bold;
            color: #eaeaea;
        }}
        .critical {{ color: #ff4757; }}
        .high {{ color: #ffa500; }}
        .medium {{ color: #4dabf7; }}
        .low {{ color: #00d9a3; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: #0f3460;
            border-radius: 8px;
            overflow: hidden;
        }}
        th {{
            background: #0f3460;
            padding: 15px;
            text-align: left;
            color: #eaeaea;
            font-weight: bold;
            border-bottom: 2px solid #2c3e50;
        }}
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #2c3e50;
            color: #a0a0a0;
        }}
        tr:hover {{
            background: #16213e;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85rem;
            font-weight: bold;
            text-transform: uppercase;
        }}
        .badge-critical {{ background: rgba(255, 71, 87, 0.2); color: #ff4757; }}
        .badge-high {{ background: rgba(255, 165, 0, 0.2); color: #ffa500; }}
        .badge-medium {{ background: rgba(77, 171, 247, 0.2); color: #4dabf7; }}
        .badge-low {{ background: rgba(0, 217, 163, 0.2); color: #00d9a3; }}
        .red-flags {{
            background: #0f3460;
            padding: 15px;
            border-radius: 6px;
            margin-top: 10px;
            border-left: 4px solid #ff4757;
        }}
        .red-flags ul {{
            margin: 10px 0 0 20px;
            padding: 0;
        }}
        .red-flags li {{
            margin-bottom: 8px;
        }}
        .footer {{
            margin-top: 60px;
            padding-top: 20px;
            border-top: 2px solid #2c3e50;
            text-align: center;
            color: #a0a0a0;
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Candidate Verification Report</h1>
        <p style="color: #a0a0a0;">Generated: {timestamp}</p>

        <h2>📊 Summary Statistics</h2>
        <div class="summary">
            <div class="stat-card">
                <h3>Total Processed</h3>
                <div class="stat-value">{batch_results['processed']}</div>
            </div>
            <div class="stat-card" style="border-left-color: #ff4757;">
                <h3>Critical Risk</h3>
                <div class="stat-value critical">{batch_results['summary']['critical_risk']}</div>
            </div>
            <div class="stat-card" style="border-left-color: #ffa500;">
                <h3>High Risk</h3>
                <div class="stat-value high">{batch_results['summary']['high_risk']}</div>
            </div>
            <div class="stat-card" style="border-left-color: #4dabf7;">
                <h3>Medium Risk</h3>
                <div class="stat-value medium">{batch_results['summary']['medium_risk']}</div>
            </div>
            <div class="stat-card" style="border-left-color: #00d9a3;">
                <h3>Low/Minimal</h3>
                <div class="stat-value low">{batch_results['summary']['low_risk'] + batch_results['summary']['minimal_risk']}</div>
            </div>
            <div class="stat-card" style="border-left-color: #ff4757;">
                <h3>AI Generated</h3>
                <div class="stat-value">{batch_results['summary']['ai_generated_count']}</div>
            </div>
            <div class="stat-card" style="border-left-color: #ff4757;">
                <h3>Trap Terms</h3>
                <div class="stat-value">{batch_results['summary']['trap_terms_count']}</div>
            </div>
        </div>

        <h2>⚠️ High Priority Candidates (Critical & High Risk)</h2>
"""

        # Add critical and high risk candidates
        high_priority = [r for r in batch_results['results']
                        if r.get('risk_level') in ['CRITICAL', 'HIGH']]

        if high_priority:
            html += self._generate_detailed_table(high_priority, show_red_flags=True)
        else:
            html += "<p style='color: #00d9a3;'>✅ No high-priority fraud indicators detected!</p>"

        html += """
        <h2>📋 All Candidates</h2>
"""
        html += self._generate_detailed_table(batch_results['results'], show_red_flags=False)

        html += f"""
        <div class="footer">
            <p><strong>Candidate Verification System v1.0</strong></p>
            <p>Based on DevOps Candidate Authenticity Assessment Framework</p>
            <p>⚠️ This report assists in fraud detection but should not be the sole basis for hiring decisions.</p>
        </div>
    </div>
</body>
</html>
"""

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)

        return html

    def _generate_detailed_table(self, results, show_red_flags=False):
        """Generate HTML table with candidate details"""
        if not results:
            return "<p style='color: #a0a0a0;'>No candidates in this category.</p>"

        html = """
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Candidate Name</th>
                    <th>Risk Score</th>
                    <th>Risk Level</th>
                    <th>AI Generated</th>
                    <th>Red Flags</th>
                    <th>Recommendation</th>
                </tr>
            </thead>
            <tbody>
"""

        for idx, result in enumerate(results, 1):
            risk_class = result.get('risk_level', '').lower()
            badge_class = f"badge-{risk_class if risk_class in ['critical', 'high', 'medium'] else 'low'}"

            ai_badge = "YES" if result.get('ai_generated') else "NO"
            ai_class = "badge-critical" if result.get('ai_generated') else "badge-low"

            red_flag_summary = f"🚩 {result.get('critical_flags', 0)} ⚠️ {result.get('warning_flags', 0)} ℹ️ {result.get('minor_flags', 0)}"

            html += f"""
                <tr>
                    <td>{idx}</td>
                    <td><strong>{self._escape_html(result.get('candidate_name', 'Unknown'))}</strong></td>
                    <td><strong class="{risk_class}">{result.get('risk_score', 0):.0f}</strong></td>
                    <td><span class="badge {badge_class}">{result.get('risk_level', 'UNKNOWN')}</span></td>
                    <td><span class="badge {ai_class}">{ai_badge}</span></td>
                    <td>{red_flag_summary}</td>
                    <td style="font-size: 0.9rem;">{self._escape_html(result.get('recommendation', ''))}</td>
                </tr>
"""

            # Add red flags details if requested
            if show_red_flags and result.get('detailed_results'):
                red_flags = result['detailed_results'].get('red_flags', {})
                if red_flags.get('critical') or red_flags.get('warning'):
                    html += f"""
                <tr>
                    <td colspan="7">
                        <div class="red-flags">
                            <strong>🚩 Detailed Red Flags for {self._escape_html(result.get('candidate_name', ''))}:</strong>
"""
                    if red_flags.get('critical'):
                        html += "<ul><strong style='color: #ff4757;'>CRITICAL:</strong>"
                        for flag in red_flags['critical']:
                            html += f"<li><strong>{flag.get('type', '')}</strong>: {self._escape_html(flag.get('description', ''))}"
                            if flag.get('recommendation'):
                                html += f"<br><em style='color: #e94560;'>→ {self._escape_html(flag.get('recommendation', ''))}</em>"
                            html += "</li>"
                        html += "</ul>"

                    if red_flags.get('warning'):
                        html += "<ul><strong style='color: #ffa500;'>WARNINGS:</strong>"
                        for flag in red_flags['warning']:
                            html += f"<li><strong>{flag.get('type', '')}</strong>: {self._escape_html(flag.get('description', ''))}</li>"
                        html += "</ul>"

                    html += """
                        </div>
                    </td>
                </tr>
"""

        html += """
            </tbody>
        </table>
"""
        return html

    def _escape_html(self, text):
        """Escape HTML special characters"""
        if text is None:
            return ''
        return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

    def generate_text_report(self, batch_results):
        """Generate plain text report"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report = f"""
================================================================================
        CANDIDATE VERIFICATION REPORT
================================================================================
Generated: {timestamp}

SUMMARY STATISTICS
--------------------------------------------------------------------------------
Total Processed:        {batch_results['processed']}
Critical Risk:          {batch_results['summary']['critical_risk']}
High Risk:              {batch_results['summary']['high_risk']}
Medium Risk:            {batch_results['summary']['medium_risk']}
Low/Minimal Risk:       {batch_results['summary']['low_risk'] + batch_results['summary']['minimal_risk']}
AI Generated:           {batch_results['summary']['ai_generated_count']}
Trap Terms Found:       {batch_results['summary']['trap_terms_count']}

HIGH PRIORITY CANDIDATES (CRITICAL & HIGH RISK)
--------------------------------------------------------------------------------
"""

        high_priority = [r for r in batch_results['results']
                        if r.get('risk_level') in ['CRITICAL', 'HIGH']]

        if high_priority:
            for idx, result in enumerate(high_priority, 1):
                report += f"""
{idx}. {result.get('candidate_name', 'Unknown')}
   File: {result.get('filename', '')}
   Risk Score: {result.get('risk_score', 0):.0f}/100
   Risk Level: {result.get('risk_level', 'UNKNOWN')}
   AI Generated: {"YES" if result.get('ai_generated') else "NO"}
   Red Flags: Critical={result.get('critical_flags', 0)}, Warning={result.get('warning_flags', 0)}, Minor={result.get('minor_flags', 0)}
   Recommendation: {result.get('recommendation', '')}
"""

                # Add critical red flags
                if result.get('detailed_results'):
                    red_flags = result['detailed_results'].get('red_flags', {})
                    if red_flags.get('critical'):
                        report += "   CRITICAL RED FLAGS:\n"
                        for flag in red_flags['critical']:
                            report += f"   - {flag.get('type', '')}: {flag.get('description', '')}\n"
                report += "\n"
        else:
            report += "No high-priority fraud indicators detected.\n"

        report += """
ALL CANDIDATES SUMMARY
--------------------------------------------------------------------------------
"""
        for idx, result in enumerate(batch_results['results'], 1):
            report += f"{idx}. {result.get('candidate_name', 'Unknown'):40s} Risk: {result.get('risk_score', 0):3.0f} [{result.get('risk_level', 'UNKNOWN'):8s}]\n"

        report += f"""
================================================================================
Report generated by Candidate Verification System v1.0
Based on DevOps Candidate Authenticity Assessment Framework
================================================================================
"""
        return report
