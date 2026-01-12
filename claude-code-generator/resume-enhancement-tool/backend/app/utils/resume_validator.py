"""Resume length and formatting validation utility."""

import re
from typing import Dict, List


class ResumeValidator:
    """Validates resume length and formatting standards."""

    # Word count targets by experience level
    PAGE_LIMITS = {
        "entry": (450, 550),      # 0-5 years: 1 page
        "mid": (550, 750),         # 5-10 years: 1-2 pages
        "senior": (750, 850)       # 10+ years: 2 pages max
    }

    def __init__(self):
        """Initialize validator."""
        pass

    def count_words(self, markdown_text: str) -> int:
        """Count words in markdown text, excluding formatting.

        Args:
            markdown_text: Markdown-formatted resume text

        Returns:
            Word count (excluding markdown syntax)
        """
        # Remove markdown headers (#, ##, ###)
        text = re.sub(r'^#{1,6}\s+', '', markdown_text, flags=re.MULTILINE)

        # Remove markdown bold/italic (* and **)
        text = re.sub(r'\*\*?([^*]+)\*\*?', r'\1', text)

        # Remove markdown links [text](url) - keep text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

        # Remove bullet points (-, *, +)
        text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)

        # Remove horizontal rules (---, ===)
        text = re.sub(r'^[-=]{3,}$', '', text, flags=re.MULTILINE)

        # Remove extra whitespace
        text = ' '.join(text.split())

        # Count words
        words = text.split()
        return len(words)

    def estimate_pages(self, word_count: int) -> float:
        """Estimate number of pages based on word count.

        Args:
            word_count: Number of words in resume

        Returns:
            Estimated page count (550 words = 1 page)
        """
        WORDS_PER_PAGE = 550
        return round(word_count / WORDS_PER_PAGE, 1)

    def determine_experience_level(self, experience_years: int) -> str:
        """Determine experience level category.

        Args:
            experience_years: Years of professional experience

        Returns:
            Experience level: "entry", "mid", or "senior"
        """
        if experience_years < 5:
            return "entry"
        elif experience_years < 10:
            return "mid"
        else:
            return "senior"

    def validate_resume_length(
        self,
        markdown_text: str,
        experience_years: int
    ) -> Dict[str, any]:
        """Validate resume meets length requirements.

        Args:
            markdown_text: Markdown-formatted resume text
            experience_years: Years of professional experience

        Returns:
            Dictionary containing:
            - is_valid: bool (True if within target range)
            - word_count: int (actual word count)
            - target_range: tuple (min, max words)
            - page_estimate: float (estimated pages)
            - experience_level: str (entry/mid/senior)
            - issues: list of validation issues
            - recommendations: list of improvement suggestions
        """
        word_count = self.count_words(markdown_text)
        page_estimate = self.estimate_pages(word_count)
        experience_level = self.determine_experience_level(experience_years)
        target_range = self.PAGE_LIMITS[experience_level]

        issues = []
        recommendations = []

        # Check word count
        min_words, max_words = target_range
        is_valid = min_words <= word_count <= max_words

        if word_count < min_words:
            issues.append(f"Resume is too short ({word_count} words, target: {min_words}-{max_words})")
            recommendations.append("Add more quantified achievements and relevant details")
            recommendations.append("Expand bullet points with metrics and impact")
        elif word_count > max_words:
            issues.append(f"Resume is too long ({word_count} words, target: {min_words}-{max_words})")
            recommendations.append("Remove less relevant positions or experiences")
            recommendations.append("Condense bullet points to 1-2 lines each")
            recommendations.append("Eliminate verbose descriptions and redundant information")

        # Check page estimate
        max_pages = 1 if experience_level == "entry" else 2
        if page_estimate > max_pages:
            issues.append(f"Resume exceeds {max_pages} page limit (estimated: {page_estimate} pages)")
            recommendations.append(f"Target {max_words} words maximum for {max_pages} pages")

        # Check for formatting issues
        formatting_issues = self.check_formatting(markdown_text)
        issues.extend(formatting_issues)

        return {
            "is_valid": is_valid and page_estimate <= max_pages,
            "word_count": word_count,
            "target_range": target_range,
            "page_estimate": page_estimate,
            "experience_level": experience_level,
            "max_pages": max_pages,
            "issues": issues,
            "recommendations": recommendations
        }

    def check_formatting(self, markdown_text: str) -> List[str]:
        """Check for common formatting issues.

        Args:
            markdown_text: Markdown-formatted resume text

        Returns:
            List of formatting issues found
        """
        issues = []

        # Check for decorative dividers
        if re.search(r'^[-=]{3,}$', markdown_text, flags=re.MULTILINE):
            issues.append("Contains decorative dividers (--- or ===) - remove for ATS compatibility")

        # Check for emojis (basic check)
        emoji_pattern = r'[\U0001F300-\U0001F9FF]'
        if re.search(emoji_pattern, markdown_text):
            issues.append("Contains emojis - remove for ATS compatibility")

        # Check for excessive blank lines
        consecutive_newlines = re.findall(r'\n{3,}', markdown_text)
        if consecutive_newlines:
            issues.append(f"Contains {len(consecutive_newlines)} instances of excessive blank lines (3+)")

        # Count total blank lines
        total_lines = len(markdown_text.split('\n'))
        blank_lines = len([line for line in markdown_text.split('\n') if line.strip() == ''])
        blank_line_ratio = blank_lines / total_lines if total_lines > 0 else 0

        if blank_line_ratio > 0.20:
            issues.append(f"Excessive whitespace ({int(blank_line_ratio*100)}% blank lines) - aim for <15%")

        return issues

    def get_summary(self, validation_result: Dict) -> str:
        """Generate human-readable validation summary.

        Args:
            validation_result: Result from validate_resume_length()

        Returns:
            Formatted summary string
        """
        result = validation_result
        status = "VALID" if result["is_valid"] else "INVALID"

        summary = f"""
Resume Validation Report
========================
Status: {status}
Word Count: {result["word_count"]} words
Target Range: {result["target_range"][0]}-{result["target_range"][1]} words
Page Estimate: {result["page_estimate"]} pages (max: {result["max_pages"]})
Experience Level: {result["experience_level"]}

"""

        if result["issues"]:
            summary += "Issues Found:\n"
            for i, issue in enumerate(result["issues"], 1):
                summary += f"  {i}. {issue}\n"
            summary += "\n"

        if result["recommendations"]:
            summary += "Recommendations:\n"
            for i, rec in enumerate(result["recommendations"], 1):
                summary += f"  {i}. {rec}\n"

        return summary
