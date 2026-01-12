"""Detect achievements and suggest quantification."""

from typing import Dict, List
import re


class AchievementDetector:
    """Detect achievements and suggest metrics for quantification."""

    # Patterns for unquantified achievements
    ACHIEVEMENT_PATTERNS = [
        (r'(improved|increased|enhanced|optimized|boosted|elevated)\s+([^.]+?)(?:\.|$)', 'improvement'),
        (r'(reduced|decreased|minimized|lowered|cut)\s+([^.]+?)(?:\.|$)', 'reduction'),
        (r'(led|managed|coordinated|supervised|directed|oversaw)\s+([^.]+?)(?:\.|$)', 'leadership'),
        (r'(developed|created|built|designed|implemented|launched|established)\s+([^.]+?)(?:\.|$)', 'creation'),
        (r'(achieved|accomplished|delivered|completed|executed)\s+([^.]+?)(?:\.|$)', 'achievement'),
        (r'(streamlined|automated|modernized|upgraded|transformed)\s+([^.]+?)(?:\.|$)', 'process'),
    ]

    # Metric suggestions based on achievement type
    METRIC_SUGGESTIONS = {
        'improvement': [
            'by X%',
            'resulting in X improvement',
            'saving X hours/dollars per week',
            'increasing efficiency by X%'
        ],
        'reduction': [
            'by X%',
            'from X to Y',
            'saving $X annually',
            'reducing costs by X%',
            'cutting time by X hours'
        ],
        'leadership': [
            'team of X people',
            'X direct reports',
            'X projects',
            'over X month/year period',
            'across X departments'
        ],
        'creation': [
            'used by X users',
            'processing X transactions daily',
            'reducing time by X%',
            'serving X customers',
            'generating $X revenue'
        ],
        'achievement': [
            'ahead of schedule by X weeks',
            'under budget by X%',
            'exceeding targets by X%',
            'with X team members'
        ],
        'process': [
            'reducing processing time by X%',
            'eliminating X manual steps',
            'saving X hours per week',
            'across X systems/teams'
        ]
    }

    def detect_achievements(self, text: str) -> List[Dict[str, any]]:
        """Detect achievements that could be quantified.

        Args:
            text: Resume or accomplishment text to analyze

        Returns:
            List of achievements with suggested metrics:
            - achievement: Full text of the achievement
            - verb: Action verb used
            - location: Line number where found
            - suggested_metrics: List of metric suggestions
            - already_quantified: Whether metrics are already present
            - achievement_type: Type of achievement (improvement, leadership, etc.)
        """

        achievements = []
        lines = text.split('\n')

        for line_num, line in enumerate(lines):
            line = line.strip()

            # Skip empty lines and very short lines
            if len(line) < 10:
                continue

            # Skip lines that are likely section headers
            if line.endswith(':') or line.isupper():
                continue

            for pattern, achievement_type in self.ACHIEVEMENT_PATTERNS:
                matches = re.finditer(pattern, line, re.IGNORECASE)

                for match in matches:
                    verb = match.group(1).lower()
                    achievement_text = match.group(2).strip()

                    # Check if already has numbers (already quantified)
                    # Look for patterns like: 20%, $500, 5 years, 100 users, etc.
                    has_numbers = bool(re.search(r'\d+\s*(?:%|\$|years?|months?|weeks?|days?|hours?|users?|people|team members?|projects?|dollars?)', achievement_text, re.IGNORECASE))

                    # Also check the full line for metrics
                    full_line_has_numbers = bool(re.search(r'\d+\s*(?:%|\$|years?|months?|weeks?|days?|hours?|users?|people|team members?|projects?|dollars?)', line, re.IGNORECASE))

                    if not full_line_has_numbers:
                        achievements.append({
                            'achievement': line,
                            'verb': verb,
                            'location': f'line {line_num + 1}',
                            'suggested_metrics': self.METRIC_SUGGESTIONS.get(achievement_type, ['with specific numbers/metrics']),
                            'already_quantified': False,
                            'achievement_type': achievement_type
                        })
                        break  # Only match once per line

        return achievements

    def generate_suggestions(self, achievements: List[Dict]) -> Dict[str, any]:
        """Generate suggestions report for achievements.

        Args:
            achievements: List of detected achievements

        Returns:
            Dictionary with:
            - total_achievements: Total number found
            - unquantified_count: Number without metrics
            - suggestions: Top 10 suggestions
            - summary: Text summary
            - breakdown_by_type: Count by achievement type
        """

        total = len(achievements)
        unquantified = [a for a in achievements if not a['already_quantified']]

        # Count by type
        breakdown = {}
        for achievement in unquantified:
            achievement_type = achievement.get('achievement_type', 'other')
            breakdown[achievement_type] = breakdown.get(achievement_type, 0) + 1

        # Create detailed suggestions (limit to top 10)
        top_suggestions = unquantified[:10]

        # Generate summary message
        if len(unquantified) == 0:
            summary = "Great! All achievements are quantified with metrics."
        elif len(unquantified) < 3:
            summary = f"Found {len(unquantified)} achievements that could benefit from metrics."
        elif len(unquantified) < 10:
            summary = f"Found {len(unquantified)} achievements that could be enhanced with specific metrics."
        else:
            summary = f"Found {len(unquantified)} achievements that could be strengthened with quantifiable results. Showing top 10 priorities."

        return {
            'total_achievements': total,
            'unquantified_count': len(unquantified),
            'suggestions': top_suggestions,
            'summary': summary,
            'breakdown_by_type': breakdown
        }

    def suggest_metric_examples(self, achievement_type: str, verb: str) -> List[str]:
        """Get specific metric suggestions for an achievement.

        Args:
            achievement_type: Type of achievement (improvement, leadership, etc.)
            verb: Action verb used

        Returns:
            List of example metrics to add
        """

        # Get base suggestions for this type
        base_suggestions = self.METRIC_SUGGESTIONS.get(achievement_type, [])

        # Add verb-specific suggestions
        verb_suggestions = {
            'improved': ['by 25%', 'resulting in 30% better performance'],
            'increased': ['by 40%', 'from 50 to 100'],
            'reduced': ['by 35%', 'from $100K to $65K'],
            'led': ['team of 5', '3 major projects'],
            'managed': ['10 direct reports', '$2M budget'],
            'developed': ['used by 1000+ users', 'processing 5K transactions daily'],
            'created': ['serving 500 customers', 'generating $200K revenue'],
            'implemented': ['across 3 departments', 'saving 20 hours/week'],
            'automated': ['eliminating 50 manual steps', 'saving 15 hours/week']
        }

        specific = verb_suggestions.get(verb, [])

        # Combine and deduplicate
        all_suggestions = base_suggestions + specific
        return list(dict.fromkeys(all_suggestions))  # Remove duplicates while preserving order
