"""
AI Agent/Skill Generator - Generates custom agents and skills using Claude API.

This module implements intelligent decision-making for when to use library templates
vs AI-generated custom content. It includes domain uniqueness scoring, token budget
management, and smart caching to minimize API costs.
"""

import json
import logging
import os
import re
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path
from anthropic import Anthropic, APIError, APIConnectionError, RateLimitError
from datetime import datetime

from .constants import CLAUDE_MODEL, API_TEMPERATURE

logger = logging.getLogger(__name__)


# ==================== AI Generation Constants ====================

# Domain uniqueness thresholds
UNIQUENESS_THRESHOLD_LOW = 30  # Below this: Use library only
UNIQUENESS_THRESHOLD_MEDIUM = 70  # Above this: Always generate custom

# Token budgets
DEFAULT_TOKEN_BUDGET = 5000  # Hard cap per generation session
AGENT_GENERATION_TOKENS = 2000  # Max tokens per agent
SKILL_GENERATION_TOKENS = 1500  # Max tokens per skill

# Cache settings
CACHE_EXPIRY_DAYS = 30

# Domain keywords that increase uniqueness score
HIGH_UNIQUENESS_KEYWORDS = {
    # Industry-specific (high scores)
    'healthcare': 30,
    'medical': 30,
    'clinical': 30,
    'hospital': 25,
    'patient': 20,
    'fintech': 25,
    'financial': 25,
    'banking': 25,
    'trading': 25,
    'cryptocurrency': 30,
    'blockchain': 25,
    'aerospace': 35,
    'aviation': 30,
    'space': 35,
    'satellite': 30,
    'defense': 30,
    'military': 30,
    'automotive': 25,
    'manufacturing': 20,
    'robotics': 30,
    'biotech': 35,
    'pharmaceutical': 30,
    'legal': 25,
    'compliance': 20,
    'regulatory': 20,
    'insurance': 20,
    'telecommunications': 20,
    'energy': 20,

    # Novel protocol/tech combinations
    'iot': 15,
    'embedded': 20,
    'edge-computing': 25,
    'real-time-systems': 25,
    'distributed-systems': 20,
    'quantum': 40,
    'neural-network': 20,
    'computer-vision': 25,
    'nlp': 20,
    'speech-recognition': 25,

    # Compliance/regulatory
    'hipaa': 20,
    'gdpr': 15,
    'pci-dss': 15,
    'sox': 15,
    'fda': 20,
    'iso-27001': 15,
    'fhir': 15,
    'hl7': 15,
    'dicom': 15,

    # Novel combinations (bonus points)
    'blockchain+iot': 20,
    'ai+embedded': 20,
    'ml+edge': 20,
    'quantum+optimization': 25,
}

# Generic keywords that decrease uniqueness (library likely sufficient)
LOW_UNIQUENESS_KEYWORDS = {
    'crud': -15,
    'rest-api': -10,
    'admin-dashboard': -10,
    'auth': -5,
    'login': -5,
    'blog': -10,
    'cms': -10,
    'e-commerce': -5,
    'todo': -15,
    'chat': -5,
    'forum': -10,
}


class AIGenerationConfig:
    """Configuration for AI generation session."""

    def __init__(
        self,
        enabled: bool = False,
        threshold: int = UNIQUENESS_THRESHOLD_LOW,
        token_budget: int = DEFAULT_TOKEN_BUDGET,
        use_cache: bool = True,
        show_stats: bool = False,
        api_key: Optional[str] = None
    ):
        """
        Initialize AI generation configuration.

        Args:
            enabled: Whether AI generation is enabled (--with-ai-agents flag)
            threshold: Minimum uniqueness score to trigger AI generation (0-100)
            token_budget: Maximum tokens to use in this session
            use_cache: Whether to use cached AI-generated content
            show_stats: Whether to display AI generation statistics
            api_key: Anthropic API key (if None, reads from env)
        """
        self.enabled = enabled
        self.threshold = threshold
        self.token_budget = token_budget
        self.use_cache = use_cache
        self.show_stats = show_stats
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.tokens_used = 0  # Track usage


class AIAgentGenerator:
    """Generate custom agents and skills using Claude API with intelligent decision-making."""

    def __init__(self, config: AIGenerationConfig, cache_manager=None):
        """
        Initialize AI agent generator.

        Args:
            config: AI generation configuration
            cache_manager: Optional cache manager instance
        """
        self.config = config
        self.cache_manager = cache_manager

        # Initialize Claude client if API key available
        if self.config.api_key:
            self.client = Anthropic(api_key=self.config.api_key)
        else:
            self.client = None
            if self.config.enabled:
                logger.warning(
                    "AI generation enabled but no API key found. "
                    "Will fall back to library templates."
                )

    def should_generate_custom_agent(
        self,
        agent_name: str,
        project_context: Dict[str, Any],
        library_match_score: float
    ) -> Tuple[bool, str, int]:
        """
        Decide whether to generate custom agent or use library template.

        Args:
            agent_name: Name of the agent to generate
            project_context: Project configuration and description
            library_match_score: How well library template matches (0-100)

        Returns:
            Tuple of (should_generate, reason, uniqueness_score)
        """
        # If AI generation not enabled, use library
        if not self.config.enabled:
            return False, "AI generation not enabled", 0

        # If no API key, use library
        if not self.client:
            return False, "No API key available", 0

        # If token budget exhausted, use library
        if self.config.tokens_used >= self.config.token_budget:
            return False, f"Token budget exhausted ({self.config.tokens_used}/{self.config.token_budget})", 0

        # Calculate domain uniqueness score
        uniqueness_score = self._calculate_domain_uniqueness(project_context)

        # Decision logic based on uniqueness score and library match
        if uniqueness_score < self.config.threshold:
            return False, f"Domain too generic (score: {uniqueness_score} < {self.config.threshold})", uniqueness_score

        # If library match is very high (>90), prefer library even if domain is unique
        if library_match_score > 90:
            return False, f"Library match excellent ({library_match_score}%), using library", uniqueness_score

        # Check token budget headroom
        estimated_tokens = AGENT_GENERATION_TOKENS
        if self.config.tokens_used + estimated_tokens > self.config.token_budget:
            return False, f"Insufficient token budget (need {estimated_tokens}, have {self.config.token_budget - self.config.tokens_used})", uniqueness_score

        # Generate custom agent
        return True, f"Novel domain (score: {uniqueness_score}) warrants custom agent", uniqueness_score

    def _calculate_domain_uniqueness(self, project_context: Dict[str, Any]) -> int:
        """
        Calculate domain uniqueness score (0-100).

        Higher scores indicate novel/specialized domains that benefit from custom agents.
        Lower scores indicate generic domains where library templates are sufficient.

        Args:
            project_context: Project configuration with description, type, tech stack

        Returns:
            Uniqueness score (0-100)
        """
        score = 50  # Start at neutral

        description = project_context.get('description', '').lower()
        project_type = project_context.get('project_type', '').lower()

        # Check for high uniqueness keywords
        for keyword, points in HIGH_UNIQUENESS_KEYWORDS.items():
            if keyword in description or keyword in project_type:
                score += points
                logger.debug(f"Found '{keyword}': +{points} points")

        # Check for low uniqueness keywords (generic patterns)
        for keyword, points in LOW_UNIQUENESS_KEYWORDS.items():
            if keyword in description or keyword in project_type:
                score += points  # Note: points are negative
                logger.debug(f"Found '{keyword}': {points} points")

        # Check for novel tech stack combinations
        tech_stack_novelty = self._assess_tech_stack_novelty(project_context)
        score += tech_stack_novelty

        # Check for multiple specialized domains (combo bonus)
        domain_count = sum(
            1 for keyword in HIGH_UNIQUENESS_KEYWORDS
            if HIGH_UNIQUENESS_KEYWORDS[keyword] >= 25 and keyword in description
        )
        if domain_count >= 2:
            combo_bonus = domain_count * 10
            score += combo_bonus
            logger.debug(f"Multiple specialized domains: +{combo_bonus} points")

        # Clamp to 0-100 range
        return max(0, min(100, score))

    def _assess_tech_stack_novelty(self, project_context: Dict[str, Any]) -> int:
        """
        Assess novelty of tech stack combination.

        Args:
            project_context: Project configuration

        Returns:
            Novelty score adjustment (-10 to +20)
        """
        score = 0

        backend = (project_context.get('backend_framework') or '').lower()
        frontend = (project_context.get('frontend_framework') or '').lower()
        database = (project_context.get('database') or '').lower()
        platform = (project_context.get('platform') or '').lower()

        # Standard combinations (reduce score)
        standard_combos = [
            ('react', 'fastapi', 'postgresql'),
            ('vue', 'django', 'postgresql'),
            ('react', 'express', 'mongodb'),
        ]

        current_combo = (frontend, backend, database)
        if any(all(tech in str(current_combo) for tech in combo) for combo in standard_combos):
            score -= 10
            logger.debug("Standard tech stack: -10 points")

        # Novel combinations (increase score)
        if platform and backend:  # IoT + backend unusual
            score += 15
            logger.debug("IoT + backend combination: +15 points")

        if 'micropython' in backend or 'circuitpython' in backend:
            score += 10
            logger.debug("Embedded firmware: +10 points")

        return score

    def _calculate_library_match(
        self,
        agent_name: str,
        project_context: Dict[str, Any],
        library_templates: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate how well library templates match the project needs.

        Args:
            agent_name: Name of agent to match
            project_context: Project configuration
            library_templates: List of available library templates

        Returns:
            Match score (0-100)
        """
        project_type = project_context.get('project_type', '')

        # Find matching library templates
        matching_templates = []
        for template in library_templates:
            # Check if agent name matches
            if agent_name in template.get('name', ''):
                matching_templates.append(template)
            # Check if project type matches selection conditions
            elif project_type in template.get('selection_conditions', {}).get('project_types', []):
                matching_templates.append(template)

        if not matching_templates:
            return 0.0

        # If we have exact name match, high score
        exact_matches = [t for t in matching_templates if agent_name == t.get('name', '')]
        if exact_matches:
            return 95.0

        # If we have project type match, medium score
        type_matches = [
            t for t in matching_templates
            if project_type in t.get('selection_conditions', {}).get('project_types', [])
        ]
        if type_matches:
            return 70.0

        # Generic match
        return 40.0

    def generate_agent(
        self,
        agent_type: str,
        agent_purpose: str,
        project_context: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate custom agent using Claude API.

        Args:
            agent_type: Type of agent (e.g., "api-development", "testing")
            agent_purpose: Specific purpose description
            project_context: Full project configuration

        Returns:
            Tuple of (generated_content, metadata)

        Raises:
            APIError: If API call fails
            ValueError: If generation fails
        """
        if not self.client:
            raise ValueError("Cannot generate agent: No API key available")

        # Build generation prompt
        prompt = self._build_agent_generation_prompt(agent_type, agent_purpose, project_context)

        try:
            # Call Claude API
            logger.info(f"Generating custom agent: {agent_type}")
            response = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=AGENT_GENERATION_TOKENS,
                temperature=API_TEMPERATURE,
                messages=[{"role": "user", "content": prompt}]
            )

            # Extract content
            content = response.content[0].text

            # Track token usage
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            self.config.tokens_used += tokens_used

            # Calculate uniqueness score for metadata
            uniqueness_score = self._calculate_domain_uniqueness(project_context)

            # Generate metadata
            metadata = {
                "type": "ai-generated",
                "generator": "claude-code-generator-v0.2.0",
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "model": CLAUDE_MODEL,
                "domain": project_context.get('project_type', 'unknown'),
                "uniqueness_score": uniqueness_score,
                "tokens_used": tokens_used,
                "agent_type": agent_type,
                "purpose": agent_purpose,
            }

            # Add frontmatter to content
            content_with_metadata = self._add_frontmatter(content, metadata)

            logger.info(f"Generated agent ({tokens_used} tokens)")

            return content_with_metadata, metadata

        except (APIError, APIConnectionError, RateLimitError) as e:
            logger.error(f"API error during generation: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during generation: {e}")
            raise ValueError(f"Failed to generate agent: {e}")

    def generate_skill(
        self,
        skill_name: str,
        skill_purpose: str,
        project_context: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate custom skill using Claude API.

        Args:
            skill_name: Name of skill
            skill_purpose: Specific purpose description
            project_context: Full project configuration

        Returns:
            Tuple of (generated_content, metadata)

        Raises:
            APIError: If API call fails
            ValueError: If generation fails
        """
        if not self.client:
            raise ValueError("Cannot generate skill: No API key available")

        # Build generation prompt
        prompt = self._build_skill_generation_prompt(skill_name, skill_purpose, project_context)

        try:
            # Call Claude API
            logger.info(f"Generating custom skill: {skill_name}")
            response = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=SKILL_GENERATION_TOKENS,
                temperature=API_TEMPERATURE,
                messages=[{"role": "user", "content": prompt}]
            )

            # Extract content
            content = response.content[0].text

            # Track token usage
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            self.config.tokens_used += tokens_used

            # Calculate uniqueness score
            uniqueness_score = self._calculate_domain_uniqueness(project_context)

            # Generate metadata
            metadata = {
                "type": "ai-generated",
                "generator": "claude-code-generator-v0.2.0",
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "model": CLAUDE_MODEL,
                "domain": project_context.get('project_type', 'unknown'),
                "uniqueness_score": uniqueness_score,
                "tokens_used": tokens_used,
                "skill_name": skill_name,
                "purpose": skill_purpose,
            }

            # Add frontmatter to content
            content_with_metadata = self._add_frontmatter(content, metadata)

            logger.info(f"Generated skill ({tokens_used} tokens)")

            return content_with_metadata, metadata

        except (APIError, APIConnectionError, RateLimitError) as e:
            logger.error(f"API error during generation: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during generation: {e}")
            raise ValueError(f"Failed to generate skill: {e}")

    def _build_agent_generation_prompt(
        self,
        agent_type: str,
        agent_purpose: str,
        project_context: Dict[str, Any]
    ) -> str:
        """
        Build comprehensive prompt for agent generation.

        Args:
            agent_type: Type of agent
            agent_purpose: Specific purpose
            project_context: Full project configuration

        Returns:
            Formatted prompt string
        """
        project_name = project_context.get('project_name', 'Project')
        project_type = project_context.get('project_type', 'application')
        description = project_context.get('description', '')
        backend = project_context.get('backend_framework', 'N/A')
        frontend = project_context.get('frontend_framework', 'N/A')
        database = project_context.get('database', 'N/A')
        features = project_context.get('features', [])

        return f"""You are an expert technical writing assistant creating a comprehensive Claude Code agent file.

**Project Context:**
- Name: {project_name}
- Type: {project_type}
- Description: {description}
- Backend: {backend}
- Frontend: {frontend}
- Database: {database}
- Features: {', '.join(features) if features else 'Standard features'}

**Agent Requirements:**
- Type: {agent_type}
- Purpose: {agent_purpose}
- Target Length: 1,000-1,500 lines (comprehensive like library agents)

**Your Task:**
Create a detailed, production-ready agent file that provides domain-specific guidance for this exact project. The agent should be as comprehensive as the library agents (1,000-1,500 lines) with deep, actionable content.

**Structure Requirements:**

1. **YAML Frontmatter:**
```yaml
---
name: {agent_type}-agent
description: {agent_purpose}
model: sonnet
tools: Read, Write, Edit, Bash, Grep, Glob
---
```

2. **Main Content Sections:**

# {agent_type.replace('-', ' ').title()} Agent

## Overview
[Comprehensive introduction specific to {project_name}]

## Project-Specific Context
[Deep dive into {project_type} architecture, patterns, and best practices for this exact stack]

## Core Responsibilities
[Detailed list of agent responsibilities tailored to {description}]

## Development Workflow
[Step-by-step workflows specific to this project's tech stack]

## Code Patterns & Examples
[Multiple code examples using {backend}, {frontend}, {database}]

## Testing Strategy
[Testing approaches specific to this stack]

## Common Tasks & Solutions
[20+ common scenarios with detailed solutions]

## Troubleshooting Guide
[Domain-specific issues and resolutions]

## Best Practices
[Industry-specific best practices relevant to {project_type}]

## Reference
[Quick reference tailored to this project]

**Critical Requirements:**
- Be extremely specific to {project_type} and {description}
- Include code examples in the actual languages/frameworks used
- Cover domain-specific concerns (e.g., HIPAA for healthcare, PCI-DSS for fintech)
- Provide 1,000-1,500 lines of actionable, detailed content
- Use concrete examples from this project's tech stack
- Avoid generic advice - everything should be tailored to THIS project

Generate the complete agent file now:"""

    def _build_skill_generation_prompt(
        self,
        skill_name: str,
        skill_purpose: str,
        project_context: Dict[str, Any]
    ) -> str:
        """
        Build comprehensive prompt for skill generation.

        Args:
            skill_name: Name of skill
            skill_purpose: Specific purpose
            project_context: Full project configuration

        Returns:
            Formatted prompt string
        """
        project_name = project_context.get('project_name', 'Project')
        project_type = project_context.get('project_type', 'application')
        description = project_context.get('description', '')

        return f"""You are an expert technical writing assistant creating a Claude Code skill file.

**Project Context:**
- Name: {project_name}
- Type: {project_type}
- Description: {description}

**Skill Requirements:**
- Name: {skill_name}
- Purpose: {skill_purpose}
- Target Length: 500-800 lines (comprehensive, actionable)

**Your Task:**
Create a detailed, project-specific skill file that provides deep domain expertise.

**Structure:**

```yaml
---
name: {skill_name}
description: {skill_purpose}
---
```

# {skill_name.replace('-', ' ').title()}

## Purpose
[Why this skill exists for {project_name}]

## When to Use
[Specific scenarios in {project_type} projects]

## Prerequisites
[What you need to know for this project type]

## Step-by-Step Guide
[Detailed workflow specific to {description}]

## Code Examples
[Multiple examples relevant to this project]

## Best Practices
[Domain-specific best practices]

## Common Pitfalls
[Issues specific to {project_type}]

## Tips & Tricks
[Expert-level insights]

Generate the complete skill file (500-800 lines):"""

    def _add_frontmatter(self, content: str, metadata: Dict[str, Any]) -> str:
        """
        Add YAML frontmatter with generation metadata to content.

        Args:
            content: Generated content
            metadata: Generation metadata

        Returns:
            Content with frontmatter
        """
        # Check if content already has frontmatter
        if content.strip().startswith('---'):
            # Extract existing frontmatter
            parts = content.split('---', 2)
            if len(parts) >= 3:
                existing_yaml = parts[1].strip()
                body = parts[2].strip()

                # Add generation metadata to existing frontmatter
                enhanced_yaml = f"""{existing_yaml}
generation:
  type: {metadata['type']}
  generator: {metadata['generator']}
  generated_at: {metadata['generated_at']}
  model: {metadata['model']}
  domain: {metadata['domain']}
  uniqueness_score: {metadata['uniqueness_score']}
  tokens_used: {metadata['tokens_used']}"""

                return f"---\n{enhanced_yaml}\n---\n\n{body}"

        # No existing frontmatter, add minimal version
        frontmatter = f"""---
generation:
  type: {metadata['type']}
  generator: {metadata['generator']}
  generated_at: {metadata['generated_at']}
  model: {metadata['model']}
  domain: {metadata['domain']}
  uniqueness_score: {metadata['uniqueness_score']}
  tokens_used: {metadata['tokens_used']}
---
"""
        return frontmatter + "\n" + content.strip()

    def get_generation_stats(self) -> Dict[str, Any]:
        """
        Get statistics about AI generation session.

        Returns:
            Dictionary with statistics
        """
        return {
            "enabled": self.config.enabled,
            "tokens_used": self.config.tokens_used,
            "token_budget": self.config.token_budget,
            "tokens_remaining": self.config.token_budget - self.config.tokens_used,
            "percentage_used": round((self.config.tokens_used / self.config.token_budget) * 100, 1) if self.config.token_budget > 0 else 0,
            "api_key_available": self.client is not None,
        }
