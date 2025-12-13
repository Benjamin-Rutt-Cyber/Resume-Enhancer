"""
AI Generation Cache Manager - Manages caching of AI-generated agents and skills.

This module implements smart caching to minimize API costs by reusing AI-generated
content across similar projects. Cache keys are based on domain similarity rather
than per-project, allowing fintech projects to share fintech-specific agents.
"""

import json
import hashlib
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)


class AICacheManager:
    """Manage cache for AI-generated agents and skills."""

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize cache manager.

        Args:
            cache_dir: Directory to store cache files. If None, uses default.
        """
        # Default cache location: .claude-generator-cache in user's home directory
        if cache_dir is None:
            cache_dir = Path.home() / '.claude-generator-cache'

        self.cache_dir = cache_dir
        self.agents_dir = cache_dir / 'agents'
        self.skills_dir = cache_dir / 'skills'
        self.metadata_file = cache_dir / 'metadata.json'

        # Create directories if they don't exist
        self._initialize_cache()

        # Load metadata
        self.metadata = self._load_metadata()

    def _initialize_cache(self) -> None:
        """Create cache directories if they don't exist."""
        try:
            self.agents_dir.mkdir(parents=True, exist_ok=True)
            self.skills_dir.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Initialized cache at {self.cache_dir}")
        except Exception as e:
            logger.warning(f"Could not create cache directory: {e}")

    def _load_metadata(self) -> Dict[str, Any]:
        """
        Load cache metadata from disk.

        Returns:
            Metadata dictionary with cache statistics
        """
        if not self.metadata_file.exists():
            return {
                "created_at": datetime.utcnow().isoformat(),
                "cache_version": "1.0",
                "total_agents_cached": 0,
                "total_skills_cached": 0,
                "total_tokens_saved": 0,
                "cache_hits": 0,
                "cache_misses": 0,
                "entries": {}
            }

        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load cache metadata: {e}")
            return {
                "created_at": datetime.utcnow().isoformat(),
                "cache_version": "1.0",
                "total_agents_cached": 0,
                "total_skills_cached": 0,
                "total_tokens_saved": 0,
                "cache_hits": 0,
                "cache_misses": 0,
                "entries": {}
            }

    def _save_metadata(self) -> None:
        """Save cache metadata to disk."""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save cache metadata: {e}")

    def generate_cache_key(
        self,
        content_type: str,
        domain: str,
        purpose: str,
        project_context: Dict[str, Any]
    ) -> str:
        """
        Generate smart cache key based on domain similarity.

        Cache keys are domain-based, not project-specific, allowing reuse across
        similar projects (e.g., all fintech projects share fintech agents).

        Args:
            content_type: "agent" or "skill"
            domain: Domain/project type (e.g., "fintech", "healthcare")
            purpose: Purpose of the agent/skill
            project_context: Project configuration

        Returns:
            Cache key (hash string)
        """
        # Extract key characteristics that define domain similarity
        tech_stack = self._normalize_tech_stack(project_context)

        # Build cache key components
        key_components = [
            content_type,
            domain.lower(),
            purpose.lower(),
            tech_stack,
        ]

        # Add specialized keywords from description if present
        description = project_context.get('description', '').lower()
        specialized_keywords = self._extract_specialized_keywords(description)
        if specialized_keywords:
            key_components.append(','.join(sorted(specialized_keywords)))

        # Generate hash
        key_string = '|'.join(key_components)
        cache_key = hashlib.sha256(key_string.encode()).hexdigest()[:16]

        logger.debug(f"Generated cache key: {cache_key} from {key_string}")
        return cache_key

    def _normalize_tech_stack(self, project_context: Dict[str, Any]) -> str:
        """
        Normalize tech stack to a consistent string for caching.

        Args:
            project_context: Project configuration

        Returns:
            Normalized tech stack string
        """
        backend = project_context.get('backend_framework', 'none')
        frontend = project_context.get('frontend_framework', 'none')
        database = project_context.get('database', 'none')

        # Sort to ensure consistent ordering
        stack = sorted([backend, frontend, database])
        return '-'.join(stack)

    def _extract_specialized_keywords(self, description: str) -> list:
        """
        Extract specialized domain keywords from description.

        Args:
            description: Project description

        Returns:
            List of specialized keywords found
        """
        # Key domain-specific terms that affect caching
        specialized_terms = {
            'hipaa', 'gdpr', 'pci-dss', 'sox', 'fda',
            'blockchain', 'cryptocurrency', 'trading',
            'patient', 'clinical', 'medical',
            'aerospace', 'aviation', 'defense',
            'real-time', 'embedded', 'iot',
            'ml', 'ai', 'neural-network',
        }

        found = []
        for term in specialized_terms:
            if term in description.lower():
                found.append(term)

        return found

    def get_cached_content(
        self,
        cache_key: str,
        content_type: str,
        max_age_days: int = 30
    ) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Retrieve cached content if available and not expired.

        Args:
            cache_key: Cache key to lookup
            content_type: "agent" or "skill"
            max_age_days: Maximum age of cache entry in days

        Returns:
            Tuple of (content, metadata) if cache hit, None if miss
        """
        # Determine cache directory
        cache_dir = self.agents_dir if content_type == "agent" else self.skills_dir
        cache_file = cache_dir / f"{cache_key}.md"

        # Check if file exists
        if not cache_file.exists():
            logger.debug(f"Cache miss: {cache_key} (file not found)")
            self.metadata['cache_misses'] = self.metadata.get('cache_misses', 0) + 1
            self._save_metadata()
            return None

        # Check metadata for this entry
        entry_meta = self.metadata.get('entries', {}).get(cache_key)
        if not entry_meta:
            logger.debug(f"Cache miss: {cache_key} (no metadata)")
            self.metadata['cache_misses'] = self.metadata.get('cache_misses', 0) + 1
            self._save_metadata()
            return None

        # Check expiry
        cached_at = datetime.fromisoformat(entry_meta['cached_at'].replace('Z', '+00:00'))
        age = datetime.now(cached_at.tzinfo) - cached_at
        if age.days > max_age_days:
            logger.debug(f"Cache expired: {cache_key} (age: {age.days} days)")
            self.metadata['cache_misses'] = self.metadata.get('cache_misses', 0) + 1
            self._save_metadata()
            return None

        # Read cached content
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Update statistics
            self.metadata['cache_hits'] = self.metadata.get('cache_hits', 0) + 1
            tokens_saved = entry_meta.get('tokens_used', 0)
            self.metadata['total_tokens_saved'] = self.metadata.get('total_tokens_saved', 0) + tokens_saved

            # Update hit count for this entry
            entry_meta['hit_count'] = entry_meta.get('hit_count', 0) + 1
            entry_meta['last_hit_at'] = datetime.utcnow().isoformat() + 'Z'
            self.metadata['entries'][cache_key] = entry_meta

            self._save_metadata()

            logger.info(f"Cache hit: {cache_key} (saved {tokens_saved} tokens)")
            return content, entry_meta

        except Exception as e:
            logger.warning(f"Error reading cache file {cache_key}: {e}")
            self.metadata['cache_misses'] = self.metadata.get('cache_misses', 0) + 1
            self._save_metadata()
            return None

    def store_content(
        self,
        cache_key: str,
        content_type: str,
        content: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Store generated content in cache.

        Args:
            cache_key: Cache key
            content_type: "agent" or "skill"
            content: Generated content to cache
            metadata: Generation metadata

        Returns:
            True if successfully cached, False otherwise
        """
        # Determine cache directory
        cache_dir = self.agents_dir if content_type == "agent" else self.skills_dir
        cache_file = cache_dir / f"{cache_key}.md"

        try:
            # Write content to file
            with open(cache_file, 'w', encoding='utf-8') as f:
                f.write(content)

            # Update metadata
            entry_meta = {
                "cache_key": cache_key,
                "content_type": content_type,
                "cached_at": datetime.utcnow().isoformat() + 'Z',
                "tokens_used": metadata.get('tokens_used', 0),
                "domain": metadata.get('domain', 'unknown'),
                "uniqueness_score": metadata.get('uniqueness_score', 0),
                "model": metadata.get('model', 'unknown'),
                "hit_count": 0,
                "last_hit_at": None,
            }

            self.metadata['entries'][cache_key] = entry_meta

            # Update totals
            if content_type == "agent":
                self.metadata['total_agents_cached'] = self.metadata.get('total_agents_cached', 0) + 1
            else:
                self.metadata['total_skills_cached'] = self.metadata.get('total_skills_cached', 0) + 1

            self._save_metadata()

            logger.info(f"Cached {content_type}: {cache_key}")
            return True

        except Exception as e:
            logger.error(f"Error caching content {cache_key}: {e}")
            return False

    def clear_expired(self, max_age_days: int = 30) -> int:
        """
        Remove expired cache entries.

        Args:
            max_age_days: Maximum age in days

        Returns:
            Number of entries removed
        """
        removed_count = 0
        entries_to_remove = []

        for cache_key, entry_meta in self.metadata.get('entries', {}).items():
            # Check expiry
            cached_at = datetime.fromisoformat(entry_meta['cached_at'].replace('Z', '+00:00'))
            age = datetime.now(cached_at.tzinfo) - cached_at

            if age.days > max_age_days:
                entries_to_remove.append(cache_key)

                # Remove file
                content_type = entry_meta['content_type']
                cache_dir = self.agents_dir if content_type == "agent" else self.skills_dir
                cache_file = cache_dir / f"{cache_key}.md"

                try:
                    if cache_file.exists():
                        cache_file.unlink()
                        removed_count += 1
                except Exception as e:
                    logger.warning(f"Could not remove expired cache file {cache_key}: {e}")

        # Remove metadata entries
        for cache_key in entries_to_remove:
            del self.metadata['entries'][cache_key]

        if removed_count > 0:
            self._save_metadata()
            logger.info(f"Removed {removed_count} expired cache entries")

        return removed_count

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        total_entries = len(self.metadata.get('entries', {}))
        cache_hits = self.metadata.get('cache_hits', 0)
        cache_misses = self.metadata.get('cache_misses', 0)
        total_requests = cache_hits + cache_misses

        hit_rate = (cache_hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "cache_directory": str(self.cache_dir),
            "total_agents_cached": self.metadata.get('total_agents_cached', 0),
            "total_skills_cached": self.metadata.get('total_skills_cached', 0),
            "total_entries": total_entries,
            "cache_hits": cache_hits,
            "cache_misses": cache_misses,
            "hit_rate_percentage": round(hit_rate, 1),
            "total_tokens_saved": self.metadata.get('total_tokens_saved', 0),
            "created_at": self.metadata.get('created_at', 'unknown'),
        }

    def clear_all(self) -> bool:
        """
        Clear all cache entries.

        Returns:
            True if successful
        """
        try:
            # Remove all cached files
            for cache_file in self.agents_dir.glob('*.md'):
                cache_file.unlink()
            for cache_file in self.skills_dir.glob('*.md'):
                cache_file.unlink()

            # Reset metadata
            self.metadata = {
                "created_at": datetime.utcnow().isoformat(),
                "cache_version": "1.0",
                "total_agents_cached": 0,
                "total_skills_cached": 0,
                "total_tokens_saved": 0,
                "cache_hits": 0,
                "cache_misses": 0,
                "entries": {}
            }
            self._save_metadata()

            logger.info("Cleared all cache entries")
            return True

        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
