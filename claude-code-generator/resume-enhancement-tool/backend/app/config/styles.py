"""Resume writing style configurations.

This module defines the 5 available writing styles for resume enhancement.
Each style has a unique tone and approach while maintaining the same visual template.
"""

from typing import Dict, Any


STYLES: Dict[str, Dict[str, Any]] = {
    "professional": {
        "name": "Professional",
        "description": "Traditional corporate tone with formal language",
        "tone": "formal, corporate, traditional",
        "prompt_guidance": """Use formal business language with a traditional corporate tone.
- Employ passive voice where appropriate ("was responsible for", "tasked with")
- Use conventional business terminology
- Maintain a conservative, professional demeanor
- Focus on responsibility and accountability
- Emphasize stability, reliability, and proven track record
- Use measured, diplomatic language
Example: "Responsible for managing a team of 10 software developers and overseeing project delivery across multiple concurrent initiatives."
"""
    },

    "executive": {
        "name": "Executive",
        "description": "Senior leadership language with strategic focus",
        "tone": "authoritative, strategic, refined",
        "prompt_guidance": """Use executive-level language that emphasizes strategic impact and leadership.
- Focus on high-level organizational outcomes and business value
- Emphasize leadership, vision, and strategic decision-making
- Use terms like "orchestrated", "spearheaded", "championed"
- Highlight influence on company direction and bottom-line results
- Show scope of authority and cross-functional impact
- Use confident, authoritative tone
Example: "Spearheaded digital transformation initiative that drove $2.5M in cost savings and positioned the organization for scalable growth."
"""
    },

    "technical": {
        "name": "Technical",
        "description": "Detailed technical terminology with specific metrics",
        "tone": "precise, technical, data-driven",
        "prompt_guidance": """Use precise technical language with specific tools, technologies, and quantifiable metrics.
- Include specific technology names, versions, and frameworks
- Emphasize technical implementations and methodologies
- Use metrics, percentages, and concrete numbers
- Highlight technical complexity and problem-solving
- Focus on "how" things were built, not just "what"
- Use technical verbs: "architected", "engineered", "optimized", "refactored"
Example: "Engineered microservices architecture using Docker and Kubernetes, reducing deployment time from 2 hours to 15 minutes and improving system uptime to 99.95%."
"""
    },

    "creative": {
        "name": "Creative",
        "description": "Dynamic personality-focused with engaging language",
        "tone": "engaging, personality-driven, dynamic",
        "prompt_guidance": """Use dynamic, engaging language that shows personality and innovation.
- Strong active voice with vivid action verbs
- Show enthusiasm and passion for work
- Emphasize creativity, innovation, and fresh approaches
- Use engaging storytelling elements
- Highlight unique contributions and outside-the-box thinking
- Convey energy and forward-thinking mindset
- Use dynamic verbs: "transformed", "revolutionized", "pioneered", "ignited"
Example: "Transformed the customer experience by pioneering an AI-driven chatbot solution that delighted users and slashed response times by 80%."
"""
    },

    "concise": {
        "name": "Concise",
        "description": "Brief impactful statements in scannable format",
        "tone": "brief, impactful, scannable",
        "prompt_guidance": """Use extremely concise language optimized for quick scanning.
- Maximum 10 words per bullet point
- Start with strong action verb, follow with outcome
- Eliminate all unnecessary words and articles
- Use abbreviated phrases and impact-first structure
- Focus on results and numbers
- No elaboration or explanation - just facts and impact
- Heavily favor metrics and percentages
Example: "Led 10-person team. Delivered 5 projects. Saved $200K annually."
"""
    }
}


def get_style_names() -> list[str]:
    """Get list of all available style names."""
    return list(STYLES.keys())


def get_style_config(style: str) -> Dict[str, Any]:
    """Get configuration for a specific style.

    Args:
        style: Style name

    Returns:
        Style configuration dictionary

    Raises:
        ValueError: If style is not found
    """
    if style not in STYLES:
        raise ValueError(f"Unknown style: {style}. Valid styles: {get_style_names()}")
    return STYLES[style]


def validate_style(style: str) -> bool:
    """Validate if a style name is valid.

    Args:
        style: Style name to validate

    Returns:
        True if valid, False otherwise
    """
    return style in STYLES
