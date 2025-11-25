"""
Comprehensive unit tests for BoilerplateGenerator.

Tests cover:
- FastAPI backend boilerplate generation (real templates)
- Next.js frontend boilerplate generation (real templates)
- React frontend boilerplate generation (real templates)
- Configuration file generation (real templates)
- Error handling and edge cases
- Integration with FileGenerator
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import shutil
import tempfile
import yaml

from src.generator.boilerplate_generator import BoilerplateGenerator
from src.generator.analyzer import ProjectConfig


# ==================== Fixtures ====================

@pytest.fixture
def temp_output_dir():
    """Create a temporary output directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def templates_dir():
    """Return path to actual templates directory."""
    return Path(__file__).parent.parent.parent / 'templates'


@pytest.fixture
def sample_fastapi_config():
    """Sample FastAPI project configuration."""
    return ProjectConfig(
        project_name="Test FastAPI App",
        project_slug="test-fastapi-app",
        project_type="saas-web-app",
        description="A test FastAPI application",
        backend_framework="python-fastapi",
        database="postgresql",
        features=["authentication", "api_endpoints"],
    )


@pytest.fixture
def sample_nextjs_config():
    """Sample Next.js project configuration."""
    return ProjectConfig(
        project_name="Test Next.js App",
        project_slug="test-nextjs-app",
        project_type="saas-web-app",
        description="A test Next.js application",
        frontend_framework="nextjs",
        features=["authentication", "dashboard"],
    )


@pytest.fixture
def sample_react_config():
    """Sample React project configuration."""
    return ProjectConfig(
        project_name="Test React App",
        project_slug="test-react-app",
        project_type="saas-web-app",
        description="A test React application",
        frontend_framework="react",
        features=["authentication", "dashboard"],
    )


@pytest.fixture
def sample_fullstack_config():
    """Sample full-stack project configuration."""
    return ProjectConfig(
        project_name="Test Full Stack App",
        project_slug="test-fullstack-app",
        project_type="saas-web-app",
        description="A test full-stack application",
        backend_framework="python-fastapi",
        frontend_framework="react",
        database="postgresql",
        features=["authentication", "api_endpoints"],
    )


@pytest.fixture
def sample_express_config():
    """Sample Express.js project configuration."""
    return ProjectConfig(
        project_name="Test Express App",
        project_slug="test-express-app",
        project_type="saas-web-app",
        description="A test Express.js application",
        backend_framework="express",
        database="postgresql",
        features=["authentication", "api_endpoints"],
    )


@pytest.fixture
def sample_vue_config():
    """Sample Vue.js project configuration."""
    return ProjectConfig(
        project_name="Test Vue App",
        project_slug="test-vue-app",
        project_type="saas-web-app",
        description="A test Vue.js application",
        frontend_framework="vue",
        features=["authentication", "dashboard"],
    )


@pytest.fixture
def sample_django_config():
    """Sample Django project configuration."""
    return ProjectConfig(
        project_name="Test Django App",
        project_slug="test-django-app",
        project_type="saas-web-app",
        description="A test Django application",
        backend_framework="django",
        database="postgresql",
        features=["authentication", "api_endpoints"],
    )


@pytest.fixture
def sample_nuxt_config():
    """Sample Nuxt.js project configuration."""
    return ProjectConfig(
        project_name="Test Nuxt App",
        project_slug="test-nuxt-app",
        project_type="saas-web-app",
        description="A test Nuxt.js application",
        frontend_framework="nuxt",
        features=["authentication", "dashboard"],
    )


@pytest.fixture
def sample_svelte_config():
    """Sample SvelteKit project configuration."""
    return ProjectConfig(
        project_name="Test SvelteKit App",
        project_slug="test-sveltekit-app",
        project_type="saas-web-app",
        description="A test SvelteKit application",
        frontend_framework="svelte",
        features=["authentication", "dashboard"],
    )


@pytest.fixture
def sample_angular_config():
    """Sample Angular project configuration."""
    return ProjectConfig(
        project_name="Test Angular App",
        project_slug="test-angular-app",
        project_type="saas-web-app",
        description="A test Angular application",
        frontend_framework="angular",
        features=["authentication", "dashboard"],
    )


# ==================== Test Integration with Real Templates ====================

def test_real_fastapi_templates(templates_dir, temp_output_dir, sample_fastapi_config):
    """Test generation with real FastAPI templates."""
    # Skip if templates don't exist
    fastapi_template_dir = templates_dir / 'boilerplate' / 'python-fastapi'
    if not fastapi_template_dir.exists():
        pytest.skip("Real FastAPI templates not found")

    generator = BoilerplateGenerator(templates_dir)
    result = generator.generate_boilerplate(sample_fastapi_config, temp_output_dir)

    # Should generate backend files
    assert 'backend' in result
    assert len(result['backend']) > 0


def test_real_nextjs_templates(templates_dir, temp_output_dir, sample_nextjs_config):
    """Test generation with real Next.js templates."""
    # Skip if templates don't exist
    nextjs_template_dir = templates_dir / 'boilerplate' / 'nextjs'
    if not nextjs_template_dir.exists():
        pytest.skip("Real Next.js templates not found")

    generator = BoilerplateGenerator(templates_dir)
    result = generator.generate_boilerplate(sample_nextjs_config, temp_output_dir)

    # Should generate frontend files
    assert 'frontend' in result
    assert len(result['frontend']) > 0


def test_real_react_templates(templates_dir, temp_output_dir, sample_react_config):
    """Test generation with real React templates."""
    # Skip if templates don't exist
    react_template_dir = templates_dir / 'boilerplate' / 'react'
    if not react_template_dir.exists():
        pytest.skip("Real React templates not found")

    generator = BoilerplateGenerator(templates_dir)
    result = generator.generate_boilerplate(sample_react_config, temp_output_dir)

    # Should generate frontend files
    assert 'frontend' in result
    assert len(result['frontend']) > 0

    # Verify some expected React files exist
    frontend_dir = temp_output_dir / 'frontend'
    assert frontend_dir.exists()
    assert (frontend_dir / 'package.json').exists()


def test_real_config_templates(templates_dir, temp_output_dir, sample_fastapi_config):
    """Test generation with real config templates."""
    # Skip if templates don't exist
    config_template_dir = templates_dir / 'boilerplate' / 'config'
    if not config_template_dir.exists():
        pytest.skip("Real config templates not found")

    generator = BoilerplateGenerator(templates_dir)
    result = generator.generate_boilerplate(sample_fastapi_config, temp_output_dir)

    # Should generate config files
    assert 'config' in result
    assert len(result['config']) > 0


# ==================== Test Error Handling ====================

def test_real_missing_backend_template(templates_dir, temp_output_dir):
    """Test graceful handling when backend template doesn't exist (Laravel)."""
    generator = BoilerplateGenerator(templates_dir)

    config = ProjectConfig(
        project_name="Test Laravel App",
        project_slug="test-laravel-app",
        project_type="saas-web-app",
        description="Test application with Laravel backend",
        backend_framework="laravel",  # Template doesn't exist
    )

    # Should not raise error, just skip backend generation gracefully
    result = generator.generate_boilerplate(config, temp_output_dir)

    # Backend should either not be in result or be empty
    # (implementation returns empty list for unimplemented frameworks)
    assert 'backend' not in result or len(result.get('backend', [])) == 0


def test_real_missing_frontend_template(templates_dir, temp_output_dir):
    """Test graceful handling when frontend template doesn't exist (Ember)."""
    generator = BoilerplateGenerator(templates_dir)

    config = ProjectConfig(
        project_name="Test Ember App",
        project_slug="test-ember-app",
        project_type="saas-web-app",
        description="Test application with Ember frontend",
        frontend_framework="ember",  # Template doesn't exist
    )

    # Should not raise error, just skip frontend generation gracefully
    result = generator.generate_boilerplate(config, temp_output_dir)

    # Frontend should either not be in result or be empty
    # (implementation returns empty list for unimplemented frameworks)
    assert 'frontend' not in result or len(result.get('frontend', [])) == 0


def test_real_fullstack_generation(templates_dir, temp_output_dir, sample_fullstack_config):
    """Test full-stack generation with both backend and frontend (integration test)."""
    # Skip if templates don't exist
    fastapi_template_dir = templates_dir / 'boilerplate' / 'python-fastapi'
    react_template_dir = templates_dir / 'boilerplate' / 'react'
    if not fastapi_template_dir.exists() or not react_template_dir.exists():
        pytest.skip("Real FastAPI or React templates not found")

    generator = BoilerplateGenerator(templates_dir)
    result = generator.generate_boilerplate(sample_fullstack_config, temp_output_dir)

    # Should generate both backend and frontend
    assert 'backend' in result
    assert 'frontend' in result
    assert len(result['backend']) > 0
    assert len(result['frontend']) > 0

    # Verify directory structure
    assert (temp_output_dir / 'backend').exists()
    assert (temp_output_dir / 'frontend').exists()


def test_real_express_templates(templates_dir, temp_output_dir, sample_express_config):
    """Test generation with real Express.js templates."""
    # Skip if templates don't exist
    express_template_dir = templates_dir / 'boilerplate' / 'express'
    if not express_template_dir.exists():
        pytest.skip("Real Express templates not found")

    generator = BoilerplateGenerator(templates_dir)
    result = generator.generate_boilerplate(sample_express_config, temp_output_dir)

    # Should generate backend files
    assert 'backend' in result
    assert len(result['backend']) > 0

    # Verify some expected Express files exist
    backend_dir = temp_output_dir / 'backend'
    assert backend_dir.exists()
    assert (backend_dir / 'package.json').exists()
    assert (backend_dir / 'src' / 'index.ts').exists()


def test_real_vue_templates(templates_dir, temp_output_dir, sample_vue_config):
    """Test generation with real Vue.js templates."""
    # Skip if templates don't exist
    vue_template_dir = templates_dir / 'boilerplate' / 'vue'
    if not vue_template_dir.exists():
        pytest.skip("Real Vue templates not found")

    generator = BoilerplateGenerator(templates_dir)
    result = generator.generate_boilerplate(sample_vue_config, temp_output_dir)

    # Should generate frontend files
    assert 'frontend' in result
    assert len(result['frontend']) > 0

    # Verify some expected Vue files exist
    frontend_dir = temp_output_dir / 'frontend'
    assert frontend_dir.exists()
    assert (frontend_dir / 'package.json').exists()
    assert (frontend_dir / 'src' / 'App.vue').exists()


def test_real_django_templates(templates_dir, temp_output_dir, sample_django_config):
    """Test generation with real Django templates."""
    # Skip if templates don't exist
    django_template_dir = templates_dir / 'boilerplate' / 'django'
    if not django_template_dir.exists():
        pytest.skip("Real Django templates not found")

    generator = BoilerplateGenerator(templates_dir)
    result = generator.generate_boilerplate(sample_django_config, temp_output_dir)

    # Should generate backend files
    assert 'backend' in result
    assert len(result['backend']) > 0

    # Verify some expected Django files exist
    backend_dir = temp_output_dir / 'backend'
    assert backend_dir.exists()
    assert (backend_dir / 'manage.py').exists()
    assert (backend_dir / 'requirements.txt').exists()
    assert (backend_dir / 'config' / 'settings.py').exists()


def test_real_nuxt_templates(templates_dir, temp_output_dir, sample_nuxt_config):
    """Test generation with real Nuxt.js templates."""
    # Skip if templates don't exist
    nuxt_template_dir = templates_dir / 'boilerplate' / 'nuxt'
    if not nuxt_template_dir.exists():
        pytest.skip("Real Nuxt templates not found")

    generator = BoilerplateGenerator(templates_dir)
    result = generator.generate_boilerplate(sample_nuxt_config, temp_output_dir)

    # Should generate frontend files
    assert 'frontend' in result
    assert len(result['frontend']) > 0

    # Verify some expected Nuxt files exist
    frontend_dir = temp_output_dir / 'frontend'
    assert frontend_dir.exists()
    assert (frontend_dir / 'package.json').exists()
    assert (frontend_dir / 'nuxt.config.ts').exists()
    assert (frontend_dir / 'app.vue').exists()


def test_real_svelte_templates(templates_dir, temp_output_dir, sample_svelte_config):
    """Test generation with real SvelteKit templates."""
    # Skip if templates don't exist
    svelte_template_dir = templates_dir / 'boilerplate' / 'svelte'
    if not svelte_template_dir.exists():
        pytest.skip("Real SvelteKit templates not found")

    generator = BoilerplateGenerator(templates_dir)
    result = generator.generate_boilerplate(sample_svelte_config, temp_output_dir)

    # Should generate frontend files
    assert 'frontend' in result
    assert len(result['frontend']) > 0

    # Verify some expected SvelteKit files exist
    frontend_dir = temp_output_dir / 'frontend'
    assert frontend_dir.exists()
    assert (frontend_dir / 'package.json').exists()
    assert (frontend_dir / 'svelte.config.js').exists()
    assert (frontend_dir / 'src' / 'routes' / '+page.svelte').exists()


def test_real_angular_templates(templates_dir, temp_output_dir, sample_angular_config):
    """Test generation with real Angular templates."""
    # Skip if templates don't exist
    angular_template_dir = templates_dir / 'boilerplate' / 'angular'
    if not angular_template_dir.exists():
        pytest.skip("Real Angular templates not found")

    generator = BoilerplateGenerator(templates_dir)
    result = generator.generate_boilerplate(sample_angular_config, temp_output_dir)

    # Should generate frontend files
    assert 'frontend' in result
    assert len(result['frontend']) > 0

    # Verify some expected Angular files exist
    frontend_dir = temp_output_dir / 'frontend'
    assert frontend_dir.exists()
    assert (frontend_dir / 'package.json').exists()
    assert (frontend_dir / 'angular.json').exists()
    assert (frontend_dir / 'src' / 'app' / 'app.component.ts').exists()
