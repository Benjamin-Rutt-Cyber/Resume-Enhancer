"""Anthropic Claude API service for generating style previews."""

import asyncio
import logging
from typing import Dict
from anthropic import Anthropic

from ..config.styles import STYLES, get_style_names

logger = logging.getLogger(__name__)


class AnthropicService:
    """Service for interacting with Anthropic Claude API."""

    def __init__(self, api_key: str):
        """Initialize Anthropic service.

        Args:
            api_key: Anthropic API key
        """
        if not api_key:
            raise ValueError("Anthropic API key is required")

        self.client = Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"
        logger.info(f"Anthropic service initialized with model: {self.model}")

    async def generate_style_preview(
        self, resume_text: str, style: str
    ) -> str:
        """Generate professional summary preview for a specific style.

        Args:
            resume_text: Full resume text
            style: Style name (professional, executive, technical, creative, concise)

        Returns:
            Generated professional summary in the specified style

        Raises:
            ValueError: If style is invalid
        """
        if style not in STYLES:
            raise ValueError(f"Invalid style: {style}. Valid styles: {get_style_names()}")

        style_config = STYLES[style]

        prompt = f"""Given this resume, write a 2-3 sentence professional summary in the {style_config['name']} style.

Style Guidelines:
- Tone: {style_config['tone']}
- Approach: {style_config['prompt_guidance']}

Resume (first 2000 characters):
{resume_text[:2000]}

Write ONLY the professional summary, nothing else. Do not include a heading or label - just the 2-3 sentence summary."""

        try:
            logger.info(f"Generating {style} style preview")

            # Run synchronous API call in executor
            loop = asyncio.get_event_loop()
            message = await loop.run_in_executor(
                None,
                lambda: self.client.messages.create(
                    model=self.model,
                    max_tokens=300,
                    messages=[{"role": "user", "content": prompt}]
                )
            )

            preview_text = message.content[0].text.strip()
            logger.info(f"Successfully generated {style} preview ({len(preview_text)} chars)")

            return preview_text

        except Exception as e:
            logger.error(f"Error generating {style} preview: {str(e)}")
            raise

    async def generate_all_style_previews(
        self, resume_text: str
    ) -> Dict[str, str]:
        """Generate previews for all 5 styles in parallel.

        Args:
            resume_text: Full resume text

        Returns:
            Dictionary mapping style names to preview text
        """
        logger.info("Generating all style previews in parallel")

        # Create tasks for all styles
        tasks = [
            self.generate_style_preview(resume_text, style)
            for style in get_style_names()
        ]

        # Execute in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Build result dictionary
        previews = {}
        for style, result in zip(get_style_names(), results):
            if isinstance(result, Exception):
                logger.error(f"Failed to generate {style} preview: {str(result)}")
                previews[style] = f"Error generating preview: {str(result)}"
            else:
                previews[style] = result

        successful_count = sum(1 for r in results if not isinstance(r, Exception))
        logger.info(f"Generated {successful_count}/{len(results)} style previews successfully")

        return previews
