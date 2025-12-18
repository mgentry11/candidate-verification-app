"""
Online Presence Verification Module
Checks candidate's digital footprint using OSINT techniques from the assessment document.
"""

import re
import requests
import validators
from email_validator import validate_email, EmailNotValidError
import phonenumbers

class OnlinePresenceChecker:
    def __init__(self):
        self.osint_tools = {
            'thatsthem': 'https://thatsthem.com/',
            'haveibeenpwned': 'https://haveibeenpwned.com/api/v3/breachedaccount/',
            'whatsmyname': 'https://whatsmyname.app/',
            'intelx': 'https://intelx.io/',
            'familytreenow': 'https://www.familytreenow.com/'
        }

    def verify_presence(self, candidate_info):
        """
        Verify candidate's online presence across multiple platforms
        Returns risk score and findings
        """
        results = {
            'candidate_info': candidate_info,
            'checks': {
                'email': self._check_email(candidate_info.get('email')),
                'phone': self._check_phone(candidate_info.get('phone')),
                'linkedin': self._check_linkedin_presence(candidate_info.get('name')),
                'github': self._check_github_presence(candidate_info.get('name')),
                'google': self._check_google_presence(candidate_info),
                'data_breaches': self._check_data_breaches(candidate_info.get('email'))
            },
            'red_flags': [],
            'warnings': [],
            'osint_recommendations': []
        }

        # Analyze results
        results = self._analyze_presence_results(results)

        return results

    def _check_email(self, email):
        """Validate and check email address"""
        if not email:
            return {'valid': False, 'error': 'No email provided'}

        try:
            # Validate email format
            validation = validate_email(email, check_deliverability=False)
            email_address = validation.email

            result = {
                'valid': True,
                'email': email_address,
                'domain': email_address.split('@')[1],
                'is_disposable': False,
                'is_suspicious': False,
                'flags': []
            }

            # Check for disposable email domains
            disposable_domains = [
                'tempmail', 'guerrillamail', '10minutemail', 'throwaway',
                'mailinator', 'yopmail', 'temp-mail', 'fakeinbox'
            ]

            domain = result['domain'].lower()
            if any(disp in domain for disp in disposable_domains):
                result['is_disposable'] = True
                result['flags'].append('Disposable email domain')

            # Check for suspicious patterns
            suspicious_patterns = [
                r'^\d+@',  # Starts with numbers
                r'@\d+\.',  # Domain starts with numbers
                r'[a-z]{20,}@',  # Very long random string
            ]

            for pattern in suspicious_patterns:
                if re.search(pattern, email_address):
                    result['is_suspicious'] = True
                    result['flags'].append(f'Suspicious pattern: {pattern}')

            # Check if it's a free email provider
            free_providers = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com']
            result['is_free_provider'] = domain in free_providers

            return result

        except EmailNotValidError as e:
            return {
                'valid': False,
                'error': str(e),
                'is_suspicious': True
            }

    def _check_phone(self, phone):
        """Validate phone number"""
        if not phone:
            return {'valid': False, 'error': 'No phone number provided'}

        try:
            # Parse phone number (default to US if no country code)
            if not phone.startswith('+'):
                phone = '+1' + re.sub(r'[^\d]', '', phone)

            parsed = phonenumbers.parse(phone, None)

            result = {
                'valid': phonenumbers.is_valid_number(parsed),
                'formatted': phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
                'country': phonenumbers.region_code_for_number(parsed),
                'carrier': phonenumbers.carrier.name_for_number(parsed, 'en'),
                'is_mobile': phonenumbers.number_type(parsed) == phonenumbers.PhoneNumberType.MOBILE,
                'flags': []
            }

            # Check for VOIP numbers (often used in fraud)
            if phonenumbers.number_type(parsed) == phonenumbers.PhoneNumberType.VOIP:
                result['flags'].append('VOIP number - commonly used in fraud schemes')

            return result

        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'is_suspicious': True
            }

    def _check_linkedin_presence(self, name):
        """Check if LinkedIn profile exists for the name"""
        if not name:
            return {'exists': False, 'error': 'No name provided'}

        # Note: Actual LinkedIn search requires authentication
        # This provides guidance for manual checking

        return {
            'requires_manual_check': True,
            'instructions': f'Search LinkedIn for: "{name}"',
            'search_url': f'https://www.linkedin.com/search/results/people/?keywords={name.replace(" ", "%20")}',
            'red_flags_to_check': [
                'No profile found at all',
                'Multiple profiles with exact same name and location',
                'Profile exists but created very recently'
            ]
        }

    def _check_github_presence(self, name):
        """Check if GitHub profile exists"""
        if not name:
            return {'exists': False, 'error': 'No name provided'}

        # Try to search GitHub API
        try:
            # Convert name to potential username formats
            potential_usernames = [
                name.lower().replace(' ', ''),
                name.lower().replace(' ', '-'),
                name.lower().replace(' ', '_'),
                name.split()[0].lower() + name.split()[-1].lower() if len(name.split()) > 1 else name.lower()
            ]

            found_profiles = []

            for username in potential_usernames:
                try:
                    response = requests.get(f'https://api.github.com/users/{username}', timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        found_profiles.append({
                            'username': username,
                            'profile_url': data.get('html_url'),
                            'name': data.get('name'),
                            'public_repos': data.get('public_repos'),
                            'followers': data.get('followers'),
                            'created_at': data.get('created_at')
                        })
                except:
                    continue

            return {
                'exists': len(found_profiles) > 0,
                'profiles_found': found_profiles,
                'note': 'For DevOps candidates, lack of GitHub presence is a warning sign'
            }

        except Exception as e:
            return {
                'exists': False,
                'error': str(e),
                'requires_manual_check': True
            }

    def _check_google_presence(self, candidate_info):
        """Check for Google search presence"""
        name = candidate_info.get('name', '')
        location = candidate_info.get('location', '')

        if not name:
            return {'has_presence': False, 'error': 'No name provided'}

        # Construct search queries
        search_queries = [
            f'"{name}"',
            f'"{name}" {location}' if location else None,
            f'"{name}" DevOps engineer',
            f'"{name}" LinkedIn',
        ]

        search_queries = [q for q in search_queries if q]

        return {
            'requires_manual_check': True,
            'search_queries': search_queries,
            'instructions': 'Perform these Google searches and check for legitimate results',
            'red_flags': [
                'Absolutely no search results',
                'Only fake or spam websites',
                'Results don\'t match candidate\'s claimed location/experience'
            ],
            'expected_results': [
                'LinkedIn profile',
                'GitHub profile',
                'Professional blog or portfolio',
                'Conference presentations or talks',
                'Technical articles or contributions',
                'Company employee directory mentions'
            ]
        }

    def _check_data_breaches(self, email):
        """Check if email appears in known data breaches using HaveIBeenPwned"""
        if not email:
            return {'checked': False, 'error': 'No email provided'}

        try:
            # Note: HIBP API requires API key for automated checks
            # Providing manual checking instructions

            return {
                'requires_manual_check': True,
                'check_url': f'https://haveibeenpwned.com/',
                'instructions': f'Enter email "{email}" on HaveIBeenPwned.com',
                'interpretation': {
                    'found_in_breaches': 'Normal - many legitimate emails appear in breaches',
                    'not_found': 'Could indicate new/fake email OR just lucky',
                    'disposable_detected': 'RED FLAG - Likely fraudulent'
                },
                'note': 'Real people usually have some breach history. Complete absence might indicate fake email.'
            }

        except Exception as e:
            return {'checked': False, 'error': str(e)}

    def _analyze_presence_results(self, results):
        """Analyze all presence checks and flag concerns"""
        checks = results['checks']

        # Email checks
        email_check = checks.get('email', {})
        if email_check.get('is_disposable'):
            results['red_flags'].append({
                'type': 'DISPOSABLE_EMAIL',
                'severity': 'CRITICAL',
                'description': 'Candidate is using a disposable email address',
                'recommendation': 'REJECT - Clear fraud indicator'
            })
        elif email_check.get('is_suspicious'):
            results['warnings'].append({
                'type': 'SUSPICIOUS_EMAIL',
                'severity': 'WARNING',
                'description': 'Email address has suspicious patterns',
                'flags': email_check.get('flags', [])
            })

        # Phone checks
        phone_check = checks.get('phone', {})
        if phone_check.get('flags'):
            results['warnings'].append({
                'type': 'SUSPICIOUS_PHONE',
                'severity': 'WARNING',
                'description': 'Phone number has suspicious characteristics',
                'flags': phone_check.get('flags', [])
            })

        # GitHub check (important for DevOps)
        github_check = checks.get('github', {})
        if not github_check.get('exists'):
            results['warnings'].append({
                'type': 'NO_GITHUB_PRESENCE',
                'severity': 'WARNING',
                'description': 'No GitHub profile found - unusual for DevOps candidate',
                'recommendation': 'Ask candidate about their open source contributions or personal projects'
            })

        # OSINT recommendations
        results['osint_recommendations'] = [
            {
                'tool': 'ThatsThem',
                'url': self.osint_tools['thatsthem'],
                'purpose': 'Search for name, phone, address, email',
                'action': f'Search for: {results["candidate_info"].get("name")}, {results["candidate_info"].get("email")}'
            },
            {
                'tool': 'HaveIBeenPwned',
                'url': self.osint_tools['haveibeenpwned'],
                'purpose': 'Check if email appears in data breaches',
                'action': f'Check email: {results["candidate_info"].get("email")}'
            },
            {
                'tool': 'WhatsMyName',
                'url': self.osint_tools['whatsmyname'],
                'purpose': 'Search for username across 400+ platforms',
                'action': 'Extract potential usernames from email/LinkedIn and search'
            },
            {
                'tool': 'Intelligence X',
                'url': self.osint_tools['intelx'],
                'purpose': 'Deep web search for email, domain, name',
                'action': 'Search for email and name in dark web databases'
            },
            {
                'tool': 'FamilyTreeNow',
                'url': self.osint_tools['familytreenow'],
                'purpose': 'Verify US-based candidates (public records)',
                'action': 'Search for name and location to verify identity'
            }
        ]

        # Calculate presence score
        results['presence_score'] = self._calculate_presence_score(results)
        results['presence_level'] = self._get_presence_level(results['presence_score'])

        return results

    def _calculate_presence_score(self, results):
        """Calculate online presence score (higher = more legitimate)"""
        score = 0

        checks = results['checks']

        # Email valid (+20)
        if checks.get('email', {}).get('valid'):
            score += 20
        # But penalize disposable (-30)
        if checks.get('email', {}).get('is_disposable'):
            score -= 30

        # Phone valid (+15)
        if checks.get('phone', {}).get('valid'):
            score += 15

        # GitHub presence (+25)
        github = checks.get('github', {})
        if github.get('exists') and github.get('profiles_found'):
            profiles = github['profiles_found']
            if any(p.get('public_repos', 0) > 0 for p in profiles):
                score += 25  # Has actual repositories
            else:
                score += 10  # Profile exists but no repos

        # LinkedIn presence (+20)
        # This requires manual check, so we don't auto-score

        # Google presence (+20)
        # This requires manual check, so we don't auto-score

        return max(0, min(score, 100))

    def _get_presence_level(self, score):
        """Convert presence score to level"""
        if score >= 70:
            return 'STRONG'
        elif score >= 50:
            return 'MODERATE'
        elif score >= 30:
            return 'WEAK'
        else:
            return 'MINIMAL/SUSPICIOUS'
