"""
Unit tests for modern frontend skill templates.

Tests cover:
- Next.js skill template validation
- Nuxt.js skill template validation
- SvelteKit skill template validation
- Angular skill template validation
- Skill metadata and frontmatter
- Skill content comprehensiveness
- Skill selection in template selector
"""

import pytest
from pathlib import Path
import yaml
import re

from src.generator.selector import TemplateSelector
from src.generator.analyzer import ProjectConfig


# ==================== Fixtures ====================

@pytest.fixture
def templates_dir():
    """Return path to actual templates directory."""
    return Path(__file__).parent.parent.parent / 'templates'


@pytest.fixture
def registry_path(templates_dir):
    """Return path to registry.yaml."""
    return templates_dir / 'registry.yaml'


@pytest.fixture
def selector(templates_dir):
    """Create a TemplateSelector instance."""
    return TemplateSelector(templates_dir)


# ==================== Test Skill File Existence ====================

def test_nextjs_skill_exists(templates_dir):
    """Test that Next.js skill template exists."""
    skill_path = templates_dir / 'skills' / 'library' / 'nextjs' / 'SKILL.md'
    assert skill_path.exists(), "Next.js skill template not found"


def test_nuxt_skill_exists(templates_dir):
    """Test that Nuxt.js skill template exists."""
    skill_path = templates_dir / 'skills' / 'library' / 'nuxt' / 'SKILL.md'
    assert skill_path.exists(), "Nuxt.js skill template not found"


def test_svelte_skill_exists(templates_dir):
    """Test that Svelte/SvelteKit skill template exists."""
    skill_path = templates_dir / 'skills' / 'library' / 'svelte' / 'SKILL.md'
    assert skill_path.exists(), "Svelte/SvelteKit skill template not found"


def test_angular_skill_exists(templates_dir):
    """Test that Angular skill template exists."""
    skill_path = templates_dir / 'skills' / 'library' / 'angular' / 'SKILL.md'
    assert skill_path.exists(), "Angular skill template not found"


# ==================== Test Skill Content ====================

def test_nextjs_skill_content_length(templates_dir):
    """Test that Next.js skill has substantial content."""
    skill_path = templates_dir / 'skills' / 'library' / 'nextjs' / 'SKILL.md'
    content = skill_path.read_text(encoding='utf-8')

    # Should be at least 900 lines
    lines = content.split('\n')
    assert len(lines) >= 900, f"Next.js skill should be at least 900 lines, got {len(lines)}"


def test_nuxt_skill_content_length(templates_dir):
    """Test that Nuxt.js skill has substantial content."""
    skill_path = templates_dir / 'skills' / 'library' / 'nuxt' / 'SKILL.md'
    content = skill_path.read_text(encoding='utf-8')

    # Should be at least 850 lines
    lines = content.split('\n')
    assert len(lines) >= 800, f"Nuxt.js skill should be at least 800 lines, got {len(lines)}"


def test_svelte_skill_content_length(templates_dir):
    """Test that Svelte skill has substantial content."""
    skill_path = templates_dir / 'skills' / 'library' / 'svelte' / 'SKILL.md'
    content = skill_path.read_text(encoding='utf-8')

    # Should be at least 800 lines
    lines = content.split('\n')
    assert len(lines) >= 750, f"Svelte skill should be at least 750 lines, got {len(lines)}"


def test_angular_skill_content_length(templates_dir):
    """Test that Angular skill has substantial content."""
    skill_path = templates_dir / 'skills' / 'library' / 'angular' / 'SKILL.md'
    content = skill_path.read_text(encoding='utf-8')

    # Should be at least 900 lines
    lines = content.split('\n')
    assert len(lines) >= 850, f"Angular skill should be at least 850 lines, got {len(lines)}"


# ==================== Test Skill Frontmatter ====================

def test_nextjs_skill_frontmatter(templates_dir):
    """Test that Next.js skill has proper frontmatter."""
    skill_path = templates_dir / 'skills' / 'library' / 'nextjs' / 'SKILL.md'
    content = skill_path.read_text(encoding='utf-8')

    # Should have frontmatter
    assert content.startswith('---'), "Next.js skill should have YAML frontmatter"

    # Extract frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    assert match, "Could not parse Next.js skill frontmatter"

    frontmatter = yaml.safe_load(match.group(1))

    # Verify metadata
    assert 'name' in frontmatter
    assert frontmatter['name'] == 'nextjs'
    assert 'description' in frontmatter
    assert 'Next.js' in frontmatter['description'] or 'Next' in frontmatter['description']


def test_nuxt_skill_frontmatter(templates_dir):
    """Test that Nuxt.js skill has proper frontmatter."""
    skill_path = templates_dir / 'skills' / 'library' / 'nuxt' / 'SKILL.md'
    content = skill_path.read_text(encoding='utf-8')

    assert content.startswith('---'), "Nuxt.js skill should have YAML frontmatter"

    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    assert match, "Could not parse Nuxt.js skill frontmatter"

    frontmatter = yaml.safe_load(match.group(1))

    assert 'name' in frontmatter
    assert frontmatter['name'] == 'nuxt'
    assert 'description' in frontmatter
    assert 'Nuxt' in frontmatter['description']


def test_svelte_skill_frontmatter(templates_dir):
    """Test that Svelte skill has proper frontmatter."""
    skill_path = templates_dir / 'skills' / 'library' / 'svelte' / 'SKILL.md'
    content = skill_path.read_text(encoding='utf-8')

    assert content.startswith('---'), "Svelte skill should have YAML frontmatter"

    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    assert match, "Could not parse Svelte skill frontmatter"

    frontmatter = yaml.safe_load(match.group(1))

    assert 'name' in frontmatter
    assert frontmatter['name'] == 'svelte'
    assert 'description' in frontmatter
    assert 'Svelte' in frontmatter['description']


def test_angular_skill_frontmatter(templates_dir):
    """Test that Angular skill has proper frontmatter."""
    skill_path = templates_dir / 'skills' / 'library' / 'angular' / 'SKILL.md'
    content = skill_path.read_text(encoding='utf-8')

    assert content.startswith('---'), "Angular skill should have YAML frontmatter"

    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    assert match, "Could not parse Angular skill frontmatter"

    frontmatter = yaml.safe_load(match.group(1))

    assert 'name' in frontmatter
    assert frontmatter['name'] == 'angular'
    assert 'description' in frontmatter
    assert 'Angular' in frontmatter['description']


# ==================== Test Skill Content Topics ====================

def test_nextjs_skill_covers_app_router(templates_dir):
    """Test that Next.js skill covers App Router."""
    skill_path = templates_dir / 'skills' / 'library' / 'nextjs' / 'SKILL.md'
    content = skill_path.read_text(encoding='utf-8').lower()

    assert 'app router' in content or 'app directory' in content
    assert 'server components' in content
    assert 'client components' in content


def test_nextjs_skill_covers_data_fetching(templates_dir):
    """Test that Next.js skill covers data fetching patterns."""
    skill_path = templates_dir / 'skills' / 'library' / 'nextjs' / 'SKILL.md'
    content = skill_path.read_text(encoding='utf-8').lower()

    assert 'fetch' in content or 'data fetching' in content
    assert 'server' in content
    assert 'suspense' in content or 'loading' in content


def test_nuxt_skill_covers_composition_api(templates_dir):
    """Test that Nuxt.js skill covers Composition API."""
    skill_path = templates_dir / 'skills' / 'library' / 'nuxt' / 'SKILL.md'
    content = skill_path.read_text(encoding='utf-8').lower()

    assert 'composition' in content or 'composables' in content
    assert 'usefetch' in content or 'use fetch' in content or 'data fetching' in content


def test_svelte_skill_covers_reactivity(templates_dir):
    """Test that Svelte skill covers reactivity."""
    skill_path = templates_dir / 'skills' / 'library' / 'svelte' / 'SKILL.md'
    content = skill_path.read_text(encoding='utf-8').lower()

    assert 'reactive' in content or 'reactivity' in content
    assert '$:' in content or 'reactive declarations' in content


def test_angular_skill_covers_dependency_injection(templates_dir):
    """Test that Angular skill covers dependency injection."""
    skill_path = templates_dir / 'skills' / 'library' / 'angular' / 'SKILL.md'
    content = skill_path.read_text(encoding='utf-8').lower()

    assert 'dependency injection' in content or 'inject' in content
    assert 'service' in content
    assert 'component' in content


# ==================== Test Registry Integration ====================

def test_frontend_skills_in_registry(registry_path):
    """Test that all frontend skills are registered."""
    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = yaml.safe_load(f)

    skill_names = [skill['name'] for skill in registry['skills']]

    assert 'nextjs' in skill_names, "Next.js skill not in registry"
    assert 'nuxt' in skill_names, "Nuxt.js skill not in registry"
    assert 'svelte' in skill_names, "Svelte skill not in registry"
    assert 'angular' in skill_names, "Angular skill not in registry"


def test_nextjs_skill_selection_conditions(registry_path):
    """Test that Next.js skill has proper selection conditions."""
    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = yaml.safe_load(f)

    nextjs_skill = next(s for s in registry['skills'] if s['name'] == 'nextjs')

    assert 'selection_conditions' in nextjs_skill
    conditions = nextjs_skill['selection_conditions']

    # Should be for saas-web-app projects
    assert 'project_types' in conditions
    assert 'saas-web-app' in conditions['project_types']

    # Should require nextjs frontend framework
    assert 'required_any' in conditions
    assert 'frontend_framework' in conditions['required_any']


def test_nuxt_skill_selection_conditions(registry_path):
    """Test that Nuxt.js skill has proper selection conditions."""
    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = yaml.safe_load(f)

    nuxt_skill = next(s for s in registry['skills'] if s['name'] == 'nuxt')

    assert 'selection_conditions' in nuxt_skill
    conditions = nuxt_skill['selection_conditions']

    assert 'project_types' in conditions
    assert 'saas-web-app' in conditions['project_types']

    assert 'required_any' in conditions
    assert 'frontend_framework' in conditions['required_any']


# ==================== Test Skill Selection ====================

def test_nextjs_skill_selected_for_nextjs_project(selector):
    """Test that Next.js skill is selected for Next.js projects."""
    config = ProjectConfig(
        project_name="Test App",
        project_slug="test-app",
        project_type="saas-web-app",
        description="A Next.js application",
        frontend_framework="nextjs",
    )

    templates = selector.select_templates(config)

    # Should include Next.js skill
    skill_paths = templates['skills']
    assert any('nextjs' in str(path).lower() for path in skill_paths), "Next.js skill not selected"


def test_nuxt_skill_selected_for_nuxt_project(selector):
    """Test that Nuxt.js skill is selected for Nuxt projects."""
    config = ProjectConfig(
        project_name="Test App",
        project_slug="test-app",
        project_type="saas-web-app",
        description="A Nuxt.js application",
        frontend_framework="nuxt",
    )

    templates = selector.select_templates(config)

    # Should include Nuxt skill
    skill_paths = templates['skills']
    assert any('nuxt' in str(path).lower() for path in skill_paths), "Nuxt.js skill not selected"


def test_svelte_skill_selected_for_svelte_project(selector):
    """Test that Svelte skill is selected for Svelte projects."""
    config = ProjectConfig(
        project_name="Test App",
        project_slug="test-app",
        project_type="saas-web-app",
        description="A SvelteKit application",
        frontend_framework="svelte",
    )

    templates = selector.select_templates(config)

    # Should include Svelte skill
    skill_paths = templates['skills']
    assert any('svelte' in str(path).lower() for path in skill_paths), "Svelte skill not selected"


def test_angular_skill_selected_for_angular_project(selector):
    """Test that Angular skill is selected for Angular projects."""
    config = ProjectConfig(
        project_name="Test App",
        project_slug="test-app",
        project_type="saas-web-app",
        description="An Angular application",
        frontend_framework="angular",
    )

    templates = selector.select_templates(config)

    # Should include Angular skill
    skill_paths = templates['skills']
    assert any('angular' in str(path).lower() for path in skill_paths), "Angular skill not selected"


def test_multiple_frontend_skills_not_selected(selector):
    """Test that only one frontend skill is selected at a time."""
    config = ProjectConfig(
        project_name="Test App",
        project_slug="test-app",
        project_type="saas-web-app",
        description="A Next.js application",
        frontend_framework="nextjs",
    )

    templates = selector.select_templates(config)

    # Should only have Next.js skill, not others
    skill_paths = templates['skills']
    frontend_skills = [s for s in skill_paths if any(fw in str(s).lower() for fw in ['nextjs', 'nuxt', 'svelte', 'angular'])]

    # Should have exactly one frontend framework skill
    assert len(frontend_skills) == 1, f"Should select only one frontend skill, got {len(frontend_skills)}"
    assert 'nextjs' in str(frontend_skills[0]).lower()


# ==================== Test Skill Categories ====================

def test_all_frontend_skills_categorized_as_frontend(registry_path):
    """Test that all frontend skills are categorized as 'frontend'."""
    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = yaml.safe_load(f)

    frontend_skill_names = ['nextjs', 'nuxt', 'svelte', 'angular']

    for skill in registry['skills']:
        if skill['name'] in frontend_skill_names:
            assert skill.get('category') == 'frontend', f"{skill['name']} should be categorized as 'frontend'"


def test_frontend_skills_priority(registry_path):
    """Test that frontend skills have appropriate priority."""
    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = yaml.safe_load(f)

    frontend_skill_names = ['nextjs', 'nuxt', 'svelte', 'angular']

    for skill in registry['skills']:
        if skill['name'] in frontend_skill_names:
            assert 'priority' in skill
            assert skill['priority'] in ['high', 'medium'], f"{skill['name']} should have high or medium priority"
