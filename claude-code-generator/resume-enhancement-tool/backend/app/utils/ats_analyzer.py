"""ATS keyword analysis using rule-based extraction."""

from typing import Dict, List, Set
import re


class ATSAnalyzer:
    """Rule-based ATS keyword extraction and matching."""

    # Common ATS keyword categories
    TECHNICAL_SKILLS = {
        'programming': [
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby',
            'go', 'rust', 'php', 'swift', 'kotlin', 'scala', 'r', 'matlab'
        ],
        'frameworks': [
            'react', 'angular', 'vue', 'django', 'flask', 'fastapi', 'spring',
            'node.js', 'express', '.net', 'laravel', 'rails', 'next.js', 'svelte'
        ],
        'databases': [
            'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'sql',
            'nosql', 'oracle', 'cassandra', 'dynamodb', 'sqlite', 'mariadb'
        ],
        'cloud': [
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'ansible',
            'jenkins', 'gitlab', 'github actions', 'circleci', 'helm'
        ],
        'tools': [
            'git', 'jira', 'confluence', 'linux', 'bash', 'ci/cd', 'agile',
            'scrum', 'kanban', 'slack', 'teams', 'visual studio', 'vscode'
        ]
    }

    SOFT_SKILLS = [
        'leadership', 'communication', 'teamwork', 'problem solving', 'analytical',
        'management', 'agile', 'scrum', 'collaboration', 'mentoring', 'training',
        'presentation', 'negotiation', 'strategic thinking', 'decision making'
    ]

    ACTION_VERBS = [
        'developed', 'designed', 'implemented', 'led', 'managed', 'created', 'built',
        'improved', 'optimized', 'increased', 'reduced', 'achieved', 'delivered',
        'coordinated', 'established', 'launched', 'streamlined', 'automated',
        'architected', 'engineered', 'maintained', 'deployed', 'integrated'
    ]

    def extract_keywords(self, text: str) -> Dict[str, List[str]]:
        """Extract keywords from text using regex patterns.

        Args:
            text: Text to analyze (job description or resume)

        Returns:
            Dictionary with categorized keywords:
            - technical_skills: programming, frameworks, databases, cloud, tools
            - soft_skills: leadership, communication, etc.
            - action_verbs: developed, managed, etc.
            - certifications: AWS Certified, PMP, etc.
        """
        text_lower = text.lower()

        keywords = {
            'technical_skills': [],
            'soft_skills': [],
            'action_verbs': [],
            'certifications': [],
            'tools': []
        }

        # Extract technical skills (all categories combined)
        for category, skills in self.TECHNICAL_SKILLS.items():
            for skill in skills:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, text_lower):
                    keywords['technical_skills'].append(skill)

        # Extract soft skills
        for skill in self.SOFT_SKILLS:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                keywords['soft_skills'].append(skill)

        # Extract action verbs
        for verb in self.ACTION_VERBS:
            pattern = r'\b' + re.escape(verb) + r'\b'
            if re.search(pattern, text_lower):
                keywords['action_verbs'].append(verb)

        # Extract certifications (pattern: AWS Certified, PMP, CISSP, etc.)
        cert_patterns = [
            r'\b(?:aws|azure|gcp|google cloud)\s+certified\b',
            r'\b(?:pmp|cissp|ccna|ccnp|mcse|cisa|cism|ceh)\b',
            r'\bcertified\s+\w+\s+(?:professional|specialist|engineer|administrator)\b',
            r'\b(?:comptia|cisco|microsoft|oracle|salesforce)\s+certified\b'
        ]

        for pattern in cert_patterns:
            matches = re.findall(pattern, text_lower)
            keywords['certifications'].extend(matches)

        # Remove duplicates while preserving order
        for key in keywords:
            keywords[key] = list(dict.fromkeys(keywords[key]))

        return keywords

    def calculate_match_score(self, resume_keywords: Dict, job_keywords: Dict) -> Dict[str, any]:
        """Calculate match score between resume and job keywords.

        Args:
            resume_keywords: Keywords extracted from resume
            job_keywords: Keywords extracted from job description

        Returns:
            Dictionary with match analysis:
            - match_score: 0-100 percentage
            - keywords_found: List of matching keywords
            - keywords_missing: List of job keywords not in resume
            - resume_keyword_count: Total keywords in resume
            - job_keyword_count: Total keywords in job
            - match_count: Number of matches
        """

        # Flatten keywords for comparison (excluding action verbs - they're less critical)
        resume_all = set(
            resume_keywords.get('technical_skills', []) +
            resume_keywords.get('soft_skills', []) +
            resume_keywords.get('certifications', [])
        )

        job_all = set(
            job_keywords.get('technical_skills', []) +
            job_keywords.get('soft_skills', []) +
            job_keywords.get('certifications', [])
        )

        # Calculate matches
        matched = resume_all.intersection(job_all)
        missing = job_all - resume_all

        # Calculate score (0-100)
        if len(job_all) == 0:
            match_score = 100  # No requirements = perfect match
        else:
            match_score = int((len(matched) / len(job_all)) * 100)

        return {
            'match_score': match_score,
            'keywords_found': sorted(list(matched)),
            'keywords_missing': sorted(list(missing)),
            'resume_keyword_count': len(resume_all),
            'job_keyword_count': len(job_all),
            'match_count': len(matched)
        }

    def analyze_resume_vs_job(self, resume_text: str, job_text: str) -> Dict[str, any]:
        """Full analysis of resume against job description.

        Args:
            resume_text: Resume content as text
            job_text: Job description text

        Returns:
            Complete analysis with:
            - resume_keywords: Keywords from resume
            - job_keywords: Keywords from job
            - match_analysis: Match score and details
            - recommendations: List of actionable recommendations
        """

        resume_keywords = self.extract_keywords(resume_text)
        job_keywords = self.extract_keywords(job_text)
        match_analysis = self.calculate_match_score(resume_keywords, job_keywords)

        return {
            'resume_keywords': resume_keywords,
            'job_keywords': job_keywords,
            'match_analysis': match_analysis,
            'recommendations': self._generate_recommendations(match_analysis, job_keywords)
        }

    def _generate_recommendations(self, match_analysis: Dict, job_keywords: Dict) -> List[str]:
        """Generate recommendations based on match analysis.

        Args:
            match_analysis: Match score and details
            job_keywords: Keywords from job description

        Returns:
            List of actionable recommendations
        """
        recommendations = []

        score = match_analysis['match_score']
        missing = match_analysis['keywords_missing']

        # Overall score feedback
        if score < 50:
            recommendations.append(
                "Low match score - consider adding more relevant keywords from the job description"
            )
        elif score < 70:
            recommendations.append(
                "Moderate match - add key missing skills to improve ATS ranking"
            )
        else:
            recommendations.append(
                "Good match score - resume is well-aligned with job requirements"
            )

        # Specific missing keywords
        if len(missing) > 0:
            # Prioritize technical skills
            missing_tech = [k for k in missing if k in job_keywords.get('technical_skills', [])]
            missing_soft = [k for k in missing if k in job_keywords.get('soft_skills', [])]
            missing_certs = [k for k in missing if k in job_keywords.get('certifications', [])]

            if missing_tech:
                top_missing_tech = missing_tech[:5]
                recommendations.append(
                    f"Add these technical skills if applicable: {', '.join(top_missing_tech)}"
                )

            if missing_soft:
                top_missing_soft = missing_soft[:3]
                recommendations.append(
                    f"Consider highlighting these soft skills: {', '.join(top_missing_soft)}"
                )

            if missing_certs:
                recommendations.append(
                    f"Job mentions certifications: {', '.join(missing_certs[:3])}"
                )
        else:
            recommendations.append(
                "All job keywords are present in your resume - excellent coverage!"
            )

        # ATS optimization tips
        recommendations.append(
            "Use exact keyword matches from the job description where possible"
        )
        recommendations.append(
            "Include keywords naturally in your experience bullets and skills section"
        )

        return recommendations
