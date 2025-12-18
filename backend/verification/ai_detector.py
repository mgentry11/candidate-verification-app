"""
AI Content Detector Module
Detects AI-generated resume content using multiple heuristics and patterns.
"""

import re
from collections import Counter

class AIContentDetector:
    def __init__(self):
        # Common AI-generated patterns
        self.ai_patterns = [
            r'as an? (?:experienced|seasoned|dedicated|passionate)',  # Common AI opening
            r'results?-driven',
            r'proven track record',
            r'extensive experience in',
            r'highly motivated',
            r'team player',
            r'detail-oriented',
            r'excellent (?:communication|problem-solving) skills',
            r'throughout my career',
            r'leveraged? (?:cutting-edge|state-of-the-art)',
            r'spearheaded',
            r'championed',
            r'orchestrated',
            r'comprehensive understanding of',
            r'adept at',
            r'proficient in',
        ]

        # AI sycophancy indicators - overly formal, perfect grammar
        self.ai_sentence_starters = [
            'furthermore', 'moreover', 'additionally', 'in addition',
            'consequently', 'therefore', 'thus', 'hence'
        ]

        # Repetitive structure indicators
        self.action_verbs = [
            'developed', 'implemented', 'created', 'designed', 'built',
            'managed', 'led', 'orchestrated', 'spearheaded', 'championed',
            'optimized', 'streamlined', 'enhanced', 'improved'
        ]

    def detect_ai_content(self, text):
        """Main detection method combining multiple heuristics"""

        results = {
            'is_ai_generated': False,
            'confidence': 0.0,
            'indicators': [],
            'pattern_matches': 0,
            'sentence_uniformity': 0,
            'vocabulary_diversity': 0
        }

        # 1. Pattern matching
        pattern_score = self._check_ai_patterns(text)
        results['pattern_matches'] = pattern_score['match_count']

        if pattern_score['match_count'] > 5:
            results['indicators'].append({
                'type': 'COMMON_AI_PHRASES',
                'description': f"Found {pattern_score['match_count']} common AI-generated phrases",
                'examples': pattern_score['examples'][:3]
            })

        # 2. Sentence structure uniformity
        uniformity_score = self._check_sentence_uniformity(text)
        results['sentence_uniformity'] = uniformity_score['score']

        if uniformity_score['score'] > 0.7:
            results['indicators'].append({
                'type': 'UNIFORM_SENTENCE_STRUCTURE',
                'description': 'Sentences have suspiciously uniform structure (typical of AI)',
                'score': uniformity_score['score']
            })

        # 3. Vocabulary diversity (AI tends to be too diverse or too repetitive)
        vocab_score = self._check_vocabulary_diversity(text)
        results['vocabulary_diversity'] = vocab_score['score']

        if vocab_score['score'] > 0.8:
            results['indicators'].append({
                'type': 'EXCESSIVE_VOCABULARY',
                'description': 'Unnaturally high vocabulary diversity',
                'score': vocab_score['score']
            })
        elif vocab_score['score'] < 0.3:
            results['indicators'].append({
                'type': 'REPETITIVE_VOCABULARY',
                'description': 'Extremely repetitive word usage',
                'score': vocab_score['score']
            })

        # 4. Perfect grammar indicators
        grammar_score = self._check_perfect_grammar(text)
        if grammar_score['is_perfect']:
            results['indicators'].append({
                'type': 'OVERLY_PERFECT_GRAMMAR',
                'description': 'Grammar is suspiciously perfect (no common human errors)',
                'details': grammar_score['details']
            })

        # 5. Repetitive action verb patterns
        verb_pattern = self._check_repetitive_patterns(text)
        if verb_pattern['is_repetitive']:
            results['indicators'].append({
                'type': 'REPETITIVE_STRUCTURE',
                'description': f"Bullet points follow identical structure ({verb_pattern['pattern_type']})",
                'details': verb_pattern['details']
            })

        # 6. Check for lack of personal anecdotes
        personal_score = self._check_personal_content(text)
        if personal_score['lacks_personality']:
            results['indicators'].append({
                'type': 'LACKS_PERSONALITY',
                'description': 'Resume lacks personal voice and specific anecdotes',
                'score': personal_score['score']
            })

        # Calculate overall confidence
        confidence = self._calculate_confidence(
            pattern_score,
            uniformity_score,
            vocab_score,
            grammar_score,
            verb_pattern,
            personal_score
        )

        results['confidence'] = round(confidence, 2)
        results['is_ai_generated'] = confidence > 0.6

        return results

    def _check_ai_patterns(self, text):
        """Check for common AI-generated patterns"""
        text_lower = text.lower()
        matches = []
        examples = []

        for pattern in self.ai_patterns:
            found = re.findall(pattern, text_lower, re.IGNORECASE)
            if found:
                matches.extend(found)
                examples.extend(found)

        return {
            'match_count': len(matches),
            'examples': examples
        }

    def _check_sentence_uniformity(self, text):
        """Check if sentences have uniform structure"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

        if len(sentences) < 5:
            return {'score': 0}

        # Check sentence lengths
        lengths = [len(s.split()) for s in sentences]
        avg_length = sum(lengths) / len(lengths)

        # Calculate variance
        variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
        std_dev = variance ** 0.5

        # Low variance = high uniformity (suspicious)
        # Normalize: if std_dev < 3, it's very uniform
        uniformity = max(0, 1 - (std_dev / 10))

        # Check if bullets all start with action verbs
        bullet_pattern = r'^\s*[•\-\*]\s*(\w+)'
        bullets = re.findall(bullet_pattern, text, re.MULTILINE)

        if bullets:
            action_verb_starts = sum(1 for b in bullets if b.lower() in self.action_verbs)
            if len(bullets) > 3 and action_verb_starts / len(bullets) > 0.9:
                uniformity = max(uniformity, 0.8)

        return {'score': round(uniformity, 2)}

    def _check_vocabulary_diversity(self, text):
        """Check vocabulary diversity using type-token ratio"""
        words = re.findall(r'\b\w+\b', text.lower())

        if len(words) < 50:
            return {'score': 0}

        unique_words = set(words)
        ttr = len(unique_words) / len(words)

        return {'score': round(ttr, 2)}

    def _check_perfect_grammar(self, text):
        """Check for suspiciously perfect grammar"""
        # AI-generated content tends to have:
        # 1. No sentence fragments
        # 2. Perfect punctuation
        # 3. Consistent Oxford commas
        # 4. No colloquialisms

        indicators = []

        # Check for colloquialisms (lack of = AI)
        colloquialisms = ['got', 'gonna', 'wanna', 'kinda', 'sorta', '&', 'etc.', 'i.e.', 'e.g.']
        has_colloquialisms = any(word in text.lower() for word in colloquialisms)

        if not has_colloquialisms and len(text) > 200:
            indicators.append('No informal language or colloquialisms')

        # Check for overly formal sentence starters
        formal_starts = sum(1 for starter in self.ai_sentence_starters
                          if starter in text.lower())

        if formal_starts > 3:
            indicators.append(f'Uses {formal_starts} overly formal sentence starters')

        # Check for excessive use of semicolons (AI loves them)
        semicolon_count = text.count(';')
        sentence_count = len(re.split(r'[.!?]+', text))

        if semicolon_count > sentence_count * 0.1:
            indicators.append('Excessive use of semicolons')

        return {
            'is_perfect': len(indicators) >= 2,
            'details': indicators
        }

    def _check_repetitive_patterns(self, text):
        """Check for repetitive bullet point patterns"""
        # Extract bullet points
        bullet_pattern = r'^\s*[•\-\*]\s*(.+)$'
        bullets = re.findall(bullet_pattern, text, re.MULTILINE)

        if len(bullets) < 5:
            return {'is_repetitive': False}

        # Check if they all start with action verbs
        starts = [b.split()[0].lower() for b in bullets if b.split()]
        action_starts = [s for s in starts if s in self.action_verbs]

        is_repetitive = len(action_starts) / len(starts) > 0.85 if starts else False

        # Check if they all follow same format (verb + noun + "to" + outcome)
        to_pattern = r'^\s*\w+\s+\w+.*\s+to\s+'
        to_matches = sum(1 for b in bullets if re.match(to_pattern, b, re.IGNORECASE))

        if to_matches / len(bullets) > 0.7:
            is_repetitive = True
            pattern_type = 'verb-noun-to-outcome'
        else:
            pattern_type = 'action-verb-start'

        return {
            'is_repetitive': is_repetitive,
            'pattern_type': pattern_type if is_repetitive else None,
            'details': f"{len(action_starts)}/{len(starts)} bullets start with action verbs"
        }

    def _check_personal_content(self, text):
        """Check for personal voice and specific anecdotes"""
        # Real resumes often have:
        # - First person pronouns (sometimes)
        # - Specific project names
        # - Informal touches
        # - Inconsistent formatting (human error)

        personal_indicators = 0
        text_lower = text.lower()

        # Check for first person (some people use it)
        if re.search(r'\b(i|my|me)\b', text_lower):
            personal_indicators += 1

        # Check for specific project names (usually capitalized, unique)
        project_pattern = r'\b[A-Z][a-z]+[A-Z]\w*\b'  # CamelCase
        projects = re.findall(project_pattern, text)
        if len(projects) > 2:
            personal_indicators += 1

        # Check for numbers/metrics (real people like to show off)
        metrics = re.findall(r'\d+%|\$\d+|\d+x', text)
        if len(metrics) > 3:
            personal_indicators += 1

        # Check for informal elements
        if '&' in text or 'etc' in text_lower:
            personal_indicators += 1

        # Score: higher = more personal
        score = personal_indicators / 4

        return {
            'lacks_personality': score < 0.25,
            'score': round(score, 2)
        }

    def _calculate_confidence(self, pattern_score, uniformity_score, vocab_score,
                            grammar_score, verb_pattern, personal_score):
        """Calculate overall confidence that content is AI-generated"""
        confidence = 0

        # Pattern matches (0-30 points)
        if pattern_score['match_count'] > 8:
            confidence += 30
        elif pattern_score['match_count'] > 5:
            confidence += 20
        elif pattern_score['match_count'] > 3:
            confidence += 10

        # Sentence uniformity (0-20 points)
        confidence += uniformity_score['score'] * 20

        # Vocabulary diversity extremes (0-15 points)
        if vocab_score['score'] > 0.75 or vocab_score['score'] < 0.35:
            confidence += 15

        # Perfect grammar (0-15 points)
        if grammar_score['is_perfect']:
            confidence += 15

        # Repetitive patterns (0-10 points)
        if verb_pattern['is_repetitive']:
            confidence += 10

        # Lacks personality (0-10 points)
        if personal_score['lacks_personality']:
            confidence += 10

        return min(confidence / 100, 1.0)
