"""
LinkedIn Profile Verification Module
Detects fake or compromised LinkedIn profiles based on the assessment document.
"""

import re
import requests
from datetime import datetime
from bs4 import BeautifulSoup

class LinkedInChecker:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def verify_profile(self, profile_url):
        """Verify LinkedIn profile authenticity"""
        if not profile_url:
            return {'error': 'No profile URL provided'}

        # Extract username from URL
        username_match = re.search(r'linkedin\.com/in/([^/]+)', profile_url)
        if not username_match:
            return {'error': 'Invalid LinkedIn URL format'}

        username = username_match.group(1)

        results = {
            'profile_url': profile_url,
            'username': username,
            'checks_performed': [],
            'red_flags': [],
            'warnings': [],
            'risk_score': 0
        }

        # Note: Due to LinkedIn's anti-scraping measures, we'll provide a checklist
        # of manual verification steps and automated checks where possible

        results['manual_checks_required'] = [
            {
                'check': 'Profile Age',
                'instructions': 'Go to More → About this profile → Joined',
                'red_flag': 'Profile created within 1-2 months, especially if created same month as job posting',
                'warning': 'Profile less than 6 months old'
            },
            {
                'check': 'Verification Badge',
                'instructions': 'Check if profile has LinkedIn verification badge',
                'red_flag': 'No verification badge despite being available to legitimate users'
            },
            {
                'check': 'Experience Details',
                'instructions': 'Review work experience entries',
                'red_flag': 'Only company, title, and dates listed with no role descriptions',
                'warning': 'Vague or generic descriptions'
            },
            {
                'check': 'Connections',
                'instructions': 'Check connection count and mutual connections',
                'red_flag': 'Less than 10 connections',
                'warning': 'Less than 50 connections or no mutual connections in same region/field'
            },
            {
                'check': 'Engagement',
                'instructions': 'Review posts, comments, and activity',
                'red_flag': 'No posts or only generic engagement',
                'warning': 'Very limited activity history'
            },
            {
                'check': 'Profile Photo',
                'instructions': 'Examine profile photo',
                'red_flag': 'No photo or AI-generated looking photo',
                'tools': 'Use reverse image search or AI detection tools'
            },
            {
                'check': 'Account Rotation',
                'instructions': 'Check Wayback Machine (web.archive.org) for historical data',
                'red_flag': 'Profile shows different name/person in archived versions',
                'url': f'https://web.archive.org/web/*/{profile_url}'
            }
        ]

        # Automated checks
        results['automated_checks'] = self._perform_automated_checks(profile_url, username)

        # Calculate risk score based on automated findings
        results['risk_score'] = self._calculate_linkedin_risk(results['automated_checks'])
        results['risk_level'] = self._get_risk_level(results['risk_score'])

        return results

    def _perform_automated_checks(self, profile_url, username):
        """Perform automated checks that don't require authentication"""
        checks = {
            'url_format_valid': False,
            'profile_accessible': False,
            'suspicious_username_pattern': False,
            'wayback_machine_check': None
        }

        # 1. Validate URL format
        if re.match(r'^https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9-]+/?$', profile_url):
            checks['url_format_valid'] = True

        # 2. Check for suspicious username patterns
        # Fake profiles often have random strings or patterns
        suspicious_patterns = [
            r'^\d{5,}',  # Starts with many digits
            r'^[a-z]{1,2}\d{5,}',  # One or two letters followed by many digits
            r'[a-z]{20,}',  # Extremely long random string
            r'^(test|fake|demo)',  # Obvious test accounts
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, username, re.IGNORECASE):
                checks['suspicious_username_pattern'] = True
                checks['username_pattern_matched'] = pattern
                break

        # 3. Check Wayback Machine for profile history
        wayback_data = self._check_wayback_machine(profile_url)
        checks['wayback_machine_check'] = wayback_data

        # 4. Check for common fake profile indicators in URL
        # Some fake profiles use very new or generic URLs
        if len(username) < 5:
            checks['username_too_short'] = True

        return checks

    def _check_wayback_machine(self, profile_url):
        """Check Wayback Machine for historical profile data"""
        try:
            # Wayback Machine API
            api_url = f'http://archive.org/wayback/available?url={profile_url}'
            response = requests.get(api_url, timeout=5)

            if response.status_code == 200:
                data = response.json()

                if 'archived_snapshots' in data and data['archived_snapshots']:
                    closest = data['archived_snapshots'].get('closest')
                    if closest:
                        return {
                            'has_archive': True,
                            'archive_url': closest.get('url'),
                            'archive_date': closest.get('timestamp'),
                            'recommendation': 'Check archive to see if profile belonged to different person'
                        }

            return {
                'has_archive': False,
                'note': 'No archived versions found - could indicate new profile'
            }

        except Exception as e:
            return {
                'has_archive': False,
                'error': str(e)
            }

    def _calculate_linkedin_risk(self, automated_checks):
        """Calculate risk score from automated checks"""
        risk = 0

        if not automated_checks.get('url_format_valid'):
            risk += 20

        if automated_checks.get('suspicious_username_pattern'):
            risk += 30

        if automated_checks.get('username_too_short'):
            risk += 15

        wayback = automated_checks.get('wayback_machine_check', {})
        if wayback.get('has_archive'):
            # Having archive is actually good - shows longer history
            risk -= 10
        else:
            # No archive might indicate new profile
            risk += 10

        return max(0, min(risk, 100))

    def _get_risk_level(self, score):
        """Convert risk score to level"""
        if score >= 70:
            return 'CRITICAL'
        elif score >= 50:
            return 'HIGH'
        elif score >= 30:
            return 'MEDIUM'
        else:
            return 'LOW'

    def check_profile_impersonation(self, resume_data, linkedin_data):
        """
        Check if resume and LinkedIn profile match
        Used to detect impersonation cases
        """
        mismatches = []

        # Compare names
        if resume_data.get('name') and linkedin_data.get('name'):
            if resume_data['name'].lower() != linkedin_data['name'].lower():
                mismatches.append({
                    'field': 'name',
                    'resume': resume_data['name'],
                    'linkedin': linkedin_data['name'],
                    'severity': 'CRITICAL'
                })

        # Compare education
        if resume_data.get('education') and linkedin_data.get('education'):
            # This would require more sophisticated matching
            pass

        # Compare work history
        if resume_data.get('experience') and linkedin_data.get('experience'):
            # This would require more sophisticated matching
            pass

        return {
            'is_potential_impersonation': len(mismatches) > 0,
            'mismatches': mismatches,
            'recommendation': 'REJECT - Profile may belong to different person' if mismatches else 'No obvious impersonation detected'
        }

    def generate_verification_checklist(self, profile_url):
        """Generate a checklist for manual LinkedIn verification"""
        username_match = re.search(r'linkedin\.com/in/([^/]+)', profile_url)
        username = username_match.group(1) if username_match else 'unknown'

        return {
            'profile_url': profile_url,
            'username': username,
            'checklist': [
                {
                    'step': 1,
                    'title': 'Check Profile Age',
                    'action': 'Click More → About this profile → Joined',
                    'critical_flags': [
                        'Profile created within 1-2 months of job posting',
                        'Profile created very recently (< 3 months)'
                    ],
                    'warning_flags': [
                        'Profile less than 6 months old'
                    ]
                },
                {
                    'step': 2,
                    'title': 'Verify Identity Badge',
                    'action': 'Look for blue verification checkmark on profile',
                    'critical_flags': [
                        'No verification badge (especially for US-based profiles)'
                    ]
                },
                {
                    'step': 3,
                    'title': 'Examine Experience Entries',
                    'action': 'Click on each work experience to see details',
                    'critical_flags': [
                        'Only company name, title, dates - no description',
                        'All entries lack specific details'
                    ],
                    'warning_flags': [
                        'Vague or generic descriptions',
                        'Descriptions that exactly match resume'
                    ]
                },
                {
                    'step': 4,
                    'title': 'Check Connections',
                    'action': 'Review connection count and mutual connections',
                    'critical_flags': [
                        'Less than 10 connections',
                        'No mutual connections in same region/industry'
                    ],
                    'warning_flags': [
                        'Less than 50 connections',
                        'Connections seem random or unrelated'
                    ]
                },
                {
                    'step': 5,
                    'title': 'Review Activity',
                    'action': 'Scroll through posts and comments',
                    'critical_flags': [
                        'Zero posts or activity',
                        'Only generic "Congratulations!" comments'
                    ],
                    'warning_flags': [
                        'Very limited engagement',
                        'No posts in last 6 months'
                    ]
                },
                {
                    'step': 6,
                    'title': 'Verify Profile Photo',
                    'action': 'Download profile photo and check with reverse image search',
                    'tools': [
                        'Google Reverse Image Search',
                        'TinEye',
                        'AI photo detector (thispersondoesnotexist detector)'
                    ],
                    'critical_flags': [
                        'No profile photo',
                        'AI-generated photo (unnatural features)',
                        'Stock photo or image found elsewhere'
                    ]
                },
                {
                    'step': 7,
                    'title': 'Check Account History (Wayback Machine)',
                    'action': f'Visit: https://web.archive.org/web/*/{profile_url}',
                    'critical_flags': [
                        'Profile shows different name in archived versions',
                        'Profile URL was used by different person before'
                    ],
                    'note': 'Look for evidence of account rotation/hijacking'
                },
                {
                    'step': 8,
                    'title': 'Search for Profile Reuse',
                    'action': 'Search for the username on Google',
                    'search_query': f'"{username}" site:linkedin.com',
                    'critical_flags': [
                        'Search results show cached pages with different name',
                        'Evidence of recent name change'
                    ]
                }
            ],
            'scoring_guide': {
                'critical_flags_found': 'REJECT - Do not proceed with candidate',
                '2-3_warning_flags': 'HIGH RISK - Extensive additional verification required',
                '1_warning_flag': 'MEDIUM RISK - Additional screening recommended',
                'no_flags': 'Proceed with normal interview process'
            }
        }
