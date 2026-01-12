"""Style analysis utility for matching writing styles to job descriptions."""

import re
from typing import Dict, List, Optional, Any
from enum import Enum


class SeniorityLevel(str, Enum):
    """Experience levels for job analysis."""
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"
    EXECUTIVE = "executive"


class IndustryType(str, Enum):
    """Industry categories for job analysis."""
    TECH = "tech"
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    TRADITIONAL = "traditional"
    STARTUP = "startup"
    CREATIVE = "creative"


class StyleAnalyzer:
    """
    Analyze job descriptions and recommend appropriate writing styles.

    This utility helps match resume writing styles (Professional, Executive,
    Technical, Creative, Concise) to job requirements by analyzing job
    characteristics like seniority level, industry type, technical depth,
    and leadership focus.
    """

    # Seniority detection patterns
    SENIORITY_PATTERNS = {
        "executive": [
            r"\b(C-?level|CEO|CTO|CFO|CIO|COO|CMO|CPO)\b",
            r"\b(VP|Vice President|SVP|EVP)\b",
            r"\b(10\+|15\+|20\+)\s*years",
            r"\b(P&L|budget responsibility|board)\b",
            r"\bExecutive\s+(Director|Leadership|Management)\b",
        ],
        "senior": [
            r"\b(Senior|Sr\.|Lead|Principal|Staff|Distinguished)\b",
            r"\b(7\+|8\+|9\+)\s*years",
            r"\b(architect|lead|principal)\s+(engineer|developer)\b",
        ],
        "mid": [
            r"\b(Mid-?level|Intermediate)\b",
            r"\b(3-5|4-6|5-7)\s*years",
        ],
        "entry": [
            r"\b(Entry-?level|Junior|Associate|Jr\.)\b",
            r"\b(0-2|1-3|0-3)\s*years",
            r"\b(new grad|recent graduate|college hire)\b",
        ],
    }

    # Industry detection patterns
    INDUSTRY_PATTERNS = {
        "tech": [
            r"\b(software|developer|engineer|programmer|devops|cloud|SaaS)\b",
            r"\b(tech|technology|IT|information technology)\b",
            r"\b(startup|scale-?up)\b",
        ],
        "finance": [
            r"\b(finance|financial|banking|investment|trading)\b",
            r"\b(CPA|CFA|chartered|accountant)\b",
            r"\b(Wall Street|hedge fund|private equity)\b",
        ],
        "healthcare": [
            r"\b(healthcare|medical|hospital|clinical|pharma)\b",
            r"\b(HIPAA|FDA|patient|doctor|nurse)\b",
        ],
        "traditional": [
            r"\b(traditional|established|enterprise|fortune 500)\b",
            r"\b(regulated|compliance|conservative|corporate)\b",
            r"\b(government|public sector)\b",
        ],
        "startup": [
            r"\b(startup|start-?up|early-?stage|series [ABC])\b",
            r"\b(fast-?paced|agile|innovative|disruptive)\b",
            r"\b(venture-?backed|VC-?backed)\b",
        ],
        "creative": [
            r"\b(creative|design|marketing|advertising|agency)\b",
            r"\b(UX|UI|product design|brand)\b",
        ],
    }

    # Technical skills patterns
    TECHNICAL_KEYWORDS = [
        # Programming languages
        "python", "java", "javascript", "typescript", "go", "rust", "c++", "c#",
        "ruby", "php", "swift", "kotlin", "scala", "r", "matlab",
        # Frameworks
        "react", "angular", "vue", "node.js", "django", "flask", "spring",
        "fastapi", ".net", "rails", "express", "next.js",
        # Databases
        "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
        "dynamodb", "cassandra", "oracle",
        # Cloud & Infrastructure
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible",
        "jenkins", "ci/cd", "devops",
        # Tools & Technologies
        "git", "github", "gitlab", "jira", "agile", "scrum", "microservices",
        "api", "rest", "graphql", "kafka", "spark",
    ]

    # Leadership keywords
    LEADERSHIP_KEYWORDS = [
        "lead", "manage", "mentor", "coach", "supervise", "oversee",
        "direct", "guide", "team", "reports", "p&l", "budget",
        "hiring", "building team", "cross-functional",
    ]

    # Innovation keywords (for creative/startup)
    INNOVATION_KEYWORDS = [
        "innovative", "disruptive", "cutting-edge", "pioneering",
        "groundbreaking", "revolutionary", "next-generation",
        "user-centric", "product-led", "design-thinking",
    ]

    def analyze_job_style_match(
        self,
        job_description: str,
        current_style: str,
        job_title: str = "",
        company: str = "",
    ) -> Dict[str, Any]:
        """
        Analyze if the current writing style fits the job description.

        Args:
            job_description: Full job description text
            current_style: Currently selected style (professional, executive, etc.)
            job_title: Job title (optional, helps with analysis)
            company: Company name (optional)

        Returns:
            Dictionary containing:
            - is_appropriate: bool or "questionable"
            - recommended_style: str or None
            - confidence_gap: int (0-100)
            - reasoning: List[str]
            - job_signals: Dict with extracted job characteristics
        """
        # Extract job signals
        signals = self.extract_job_signals(job_description, job_title)

        # Calculate scores for all styles
        style_scores = {
            "professional": self._calculate_professional_score(signals),
            "executive": self._calculate_executive_score(signals),
            "technical": self._calculate_technical_score(signals),
            "creative": self._calculate_creative_score(signals),
            "concise": self._calculate_concise_score(signals),
        }

        # Find best fit
        best_style = max(style_scores, key=style_scores.get)
        best_score = style_scores[best_style]
        current_score = style_scores.get(current_style.lower(), 0)
        confidence_gap = best_score - current_score

        # Generate reasoning
        reasoning = self._generate_reasoning(signals, current_style.lower(), best_style, confidence_gap)

        # Determine appropriateness (user wants 10%+ threshold)
        if confidence_gap >= 10:
            is_appropriate = False
            recommended_style = best_style
        else:
            is_appropriate = True
            recommended_style = None

        return {
            "is_appropriate": is_appropriate,
            "recommended_style": recommended_style,
            "confidence_gap": confidence_gap,
            "current_score": current_score,
            "recommended_score": best_score,
            "reasoning": reasoning,
            "job_signals": signals,
            "style_scores": style_scores,
        }

    def extract_job_signals(self, job_description: str, job_title: str = "") -> Dict[str, Any]:
        """
        Extract key signals from job description.

        Args:
            job_description: Job description text
            job_title: Job title

        Returns:
            Dictionary with job characteristics
        """
        combined_text = f"{job_title} {job_description}".lower()

        return {
            "seniority_level": self._detect_seniority(combined_text),
            "industry_type": self._detect_industry(combined_text),
            "technical_depth": self._count_technical_keywords(combined_text),
            "leadership_focus": self._calculate_leadership_score(combined_text),
            "innovation_focus": self._calculate_innovation_score(combined_text),
            "word_count": len(job_description.split()),
            "has_compliance_keywords": self._has_compliance_keywords(combined_text),
        }

    def _detect_seniority(self, text: str) -> str:
        """Detect seniority level from text."""
        # Check in order: executive, senior, mid, entry
        for level, patterns in self.SENIORITY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return level

        # Default to mid if can't determine
        return "mid"

    def _detect_industry(self, text: str) -> str:
        """Detect industry type from text."""
        industry_scores = {}

        for industry, patterns in self.INDUSTRY_PATTERNS.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                score += matches
            industry_scores[industry] = score

        # Return industry with highest score, or "traditional" as default
        if max(industry_scores.values()) > 0:
            return max(industry_scores, key=industry_scores.get)
        return "traditional"

    def _count_technical_keywords(self, text: str) -> int:
        """Count technical keywords in text."""
        count = 0
        for keyword in self.TECHNICAL_KEYWORDS:
            if keyword in text.lower():
                count += 1
        return count

    def _calculate_leadership_score(self, text: str) -> int:
        """Calculate leadership focus (0-10 scale)."""
        count = 0
        for keyword in self.LEADERSHIP_KEYWORDS:
            if keyword in text.lower():
                count += 1
        return min(10, count)

    def _calculate_innovation_score(self, text: str) -> int:
        """Calculate innovation focus (0-10 scale)."""
        count = 0
        for keyword in self.INNOVATION_KEYWORDS:
            if keyword in text.lower():
                count += 1
        return min(10, count)

    def _has_compliance_keywords(self, text: str) -> bool:
        """Check for compliance/regulated environment keywords."""
        compliance_keywords = [
            "compliance", "regulated", "regulation", "audit", "sox",
            "hipaa", "gdpr", "iso", "certified", "governance",
        ]
        for keyword in compliance_keywords:
            if keyword in text.lower():
                return True
        return False

    def _calculate_professional_score(self, signals: Dict) -> int:
        """Calculate score for Professional style (0-100)."""
        score = 60  # Base score

        # Traditional industries favor professional
        if signals["industry_type"] in ["traditional", "finance", "healthcare"]:
            score += 20

        # Entry-mid level favor professional
        if signals["seniority_level"] in ["entry", "mid"]:
            score += 15

        # Compliance/regulated environments favor professional
        if signals["has_compliance_keywords"]:
            score += 10

        # Startups disfavor professional
        if signals["industry_type"] == "startup":
            score -= 15

        # High innovation disfavors professional
        if signals["innovation_focus"] >= 5:
            score -= 10

        return max(0, min(100, score))

    def _calculate_executive_score(self, signals: Dict) -> int:
        """Calculate score for Executive style (0-100)."""
        score = 30  # Low base - executive is niche

        # Executive level strongly favors executive style
        if signals["seniority_level"] == "executive":
            score += 50
        elif signals["seniority_level"] == "senior":
            score += 20
        elif signals["seniority_level"] == "entry":
            score -= 20

        # Leadership focus favors executive
        if signals["leadership_focus"] >= 7:
            score += 25
        elif signals["leadership_focus"] >= 4:
            score += 15

        # Traditional industries favor executive
        if signals["industry_type"] == "traditional":
            score += 10

        # High technical depth disfavors executive (too in the weeds)
        if signals["technical_depth"] >= 15:
            score -= 15

        return max(0, min(100, score))

    def _calculate_technical_score(self, signals: Dict) -> int:
        """Calculate score for Technical style (0-100)."""
        score = 50  # Base score

        # Technical depth strongly favors technical style
        if signals["technical_depth"] >= 15:
            score += 30
        elif signals["technical_depth"] >= 10:
            score += 20
        elif signals["technical_depth"] >= 5:
            score += 10

        # Tech industry favors technical
        if signals["industry_type"] == "tech":
            score += 15

        # Mid-senior levels favor technical
        if signals["seniority_level"] in ["mid", "senior"]:
            score += 10

        # Executive level disfavors technical (too detailed)
        if signals["seniority_level"] == "executive":
            score -= 15

        # High leadership focus disfavors technical
        if signals["leadership_focus"] >= 7:
            score -= 10

        return max(0, min(100, score))

    def _calculate_creative_score(self, signals: Dict) -> int:
        """Calculate score for Creative style (0-100)."""
        score = 45  # Base score

        # Innovation focus strongly favors creative
        if signals["innovation_focus"] >= 7:
            score += 25
        elif signals["innovation_focus"] >= 4:
            score += 15

        # Creative industry favors creative
        if signals["industry_type"] == "creative":
            score += 20

        # Startup favors creative
        if signals["industry_type"] == "startup":
            score += 20

        # Tech industry moderately favors creative (product focus)
        if signals["industry_type"] == "tech":
            score += 10

        # Traditional/regulated industries disfavor creative
        if signals["industry_type"] in ["traditional", "finance"]:
            score -= 20
        if signals["has_compliance_keywords"]:
            score -= 15

        # Executive level disfavors creative (too informal)
        if signals["seniority_level"] == "executive":
            score -= 10

        return max(0, min(100, score))

    def _calculate_concise_score(self, signals: Dict) -> int:
        """Calculate score for Concise style (0-100)."""
        score = 50  # Base score

        # Brief job descriptions favor concise
        if signals["word_count"] < 300:
            score += 20
        elif signals["word_count"] < 500:
            score += 10

        # Operations/efficiency keywords favor concise
        # (Could add more specific pattern matching here)

        # Entry-mid levels favor concise
        if signals["seniority_level"] in ["entry", "mid"]:
            score += 10

        # High leadership focus disfavors concise (need detail)
        if signals["leadership_focus"] >= 7:
            score -= 15

        # Very high technical depth disfavors concise (need detail)
        if signals["technical_depth"] >= 15:
            score -= 10

        return max(0, min(100, score))

    def _generate_reasoning(
        self,
        signals: Dict,
        current_style: str,
        recommended_style: str,
        confidence_gap: int,
    ) -> List[str]:
        """Generate human-readable reasoning for recommendation."""
        reasons = []

        if confidence_gap < 10:
            # Style is appropriate
            reasons.append(f"Your {current_style} style is well-suited for this position")
            return reasons

        # Explain why recommended style fits better
        if recommended_style == "professional":
            if signals["industry_type"] in ["traditional", "finance", "healthcare"]:
                reasons.append(f"Traditional {signals['industry_type']} industry favors Professional tone")
            if signals["has_compliance_keywords"]:
                reasons.append("Regulated environment requires formal Professional approach")
            if signals["seniority_level"] in ["entry", "mid"]:
                reasons.append("Entry-mid level positions benefit from Professional style")

        elif recommended_style == "executive":
            if signals["seniority_level"] == "executive":
                reasons.append("Executive-level position requires Executive writing style")
            if signals["leadership_focus"] >= 7:
                reasons.append("High leadership focus (P&L, team management) suits Executive style")
            reasons.append("Executive style emphasizes strategic impact and high-level leadership")

        elif recommended_style == "technical":
            if signals["technical_depth"] >= 10:
                reasons.append(f"High technical depth ({signals['technical_depth']} keywords) favors Technical style")
            if signals["industry_type"] == "tech":
                reasons.append("Tech industry role benefits from detailed Technical approach")
            reasons.append("Technical style showcases specific tools, technologies, and metrics")

        elif recommended_style == "creative":
            if signals["innovation_focus"] >= 5:
                reasons.append(f"Innovation-focused role (score: {signals['innovation_focus']}/10) suits Creative style")
            if signals["industry_type"] == "startup":
                reasons.append("Startup environment favors dynamic Creative tone")
            if signals["industry_type"] == "creative":
                reasons.append("Creative industry role benefits from engaging Creative style")

        elif recommended_style == "concise":
            if signals["word_count"] < 300:
                reasons.append("Brief job description indicates preference for Concise style")
            reasons.append("Concise style maximizes scannability for high-volume ATS systems")

        # Add contrast with current style
        if current_style != recommended_style:
            reasons.append(f"{recommended_style.title()} style better matches this specific job profile")

        return reasons[:3]  # Return top 3 reasons
