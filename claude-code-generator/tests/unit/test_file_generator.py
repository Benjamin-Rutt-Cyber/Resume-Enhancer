"""
Comprehensive unit tests for FileGenerator.

Tests cover:
- Project generation orchestration
- Individual file generation methods
- Error handling and edge cases
- Template rendering integration
- Directory structure creation
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import shutil
import tempfile
import yaml

from src.generator.file_generator import FileGenerator
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
def mock_templates_dir(tmp_path):
    """Create a mock templates directory structure."""
    templates = tmp_path / 'templates'
    templates.mkdir()

    # Create subdirectories
    (templates / 'agents' / 'library').mkdir(parents=True)
    (templates / 'skills' / 'library').mkdir(parents=True)
    (templates / 'commands').mkdir(parents=True)
    (templates / 'docs' / 'library').mkdir(parents=True)
    (templates / 'project-types').mkdir(parents=True)

    # Create sample agent files
    (templates / 'agents' / 'library' / 'testing-agent.md').write_text(
        '# Testing Agent\n\nA reusable testing agent.'
    )
    (templates / 'agents' / 'testing-template-agent.md.j2').write_text(
        '# {{ project_name }} Testing\n\nCustom testing for {{ project_name }}.'
    )

    # Create sample skill files
    skill_dir = templates / 'skills' / 'library' / 'python-fastapi'
    skill_dir.mkdir(parents=True)
    (skill_dir / 'SKILL.md').write_text('# Python FastAPI Skill')
    (skill_dir / 'helper.py').write_text('# Helper file')

    # Create sample command templates
    (templates / 'commands' / 'run-tests.md.j2').write_text(
        '# Run Tests\n\nRun tests for {{ project_name }}'
    )
    (templates / 'commands' / 'deploy.md.j2').write_text(
        '# Deploy\n\nDeploy {{ project_name }}'
    )

    # Create sample doc templates
    (templates / 'docs' / 'API.md.j2').write_text(
        '# {{ project_name }} API\n\nAPI documentation'
    )
    (templates / 'docs' / 'library' / 'README-saas-web-app.md').write_text(
        '# SaaS Web App README\n\nComprehensive README'
    )
    (templates / 'docs' / 'library' / 'TESTING.md').write_text(
        '# Testing Guide\n\nHow to test'
    )

    # Create project-types directory with configuration
    (templates / 'project-types' / 'saas-web-app.yaml').write_text(
        '''name: saas-web-app
directory_structure:
  - src
  - tests
  - app
agents: []
skills: []
commands: []
docs: []
'''
    )

    return templates


@pytest.fixture
def sample_config():
    """Create a sample ProjectConfig for testing."""
    return ProjectConfig(
        project_name="Test Project",
        project_slug="test-project",
        description="A test project",
        project_type="saas-web-app",
        backend_framework="python-fastapi",  # Contains 'python' for __init__.py creation
        frontend_framework="react",
        database="postgresql",
        features=["authentication", "api"],
        deployment_platform="docker"
    )


@pytest.fixture
def file_generator(mock_templates_dir):
    """Create a FileGenerator instance with mock templates."""
    return FileGenerator(templates_dir=mock_templates_dir, api_key=None)


# ==================== Test generate_project() Orchestration ====================

class TestGenerateProject:
    """Test the main generate_project() orchestration method."""

    def test_generate_project_success(
        self, file_generator, sample_config, temp_output_dir
    ):
        """Test successful project generation."""
        result = file_generator.generate_project(
            config=sample_config,
            output_dir=temp_output_dir,
            overwrite=False,
            recommend_plugins=False,  # Skip plugin analyzer to avoid API calls
            use_ai_plugins=False
        )

        # Verify result structure
        assert 'agents' in result
        assert 'skills' in result
        assert 'commands' in result
        assert 'docs' in result
        assert 'other' in result

        # Verify README and gitignore created
        assert (temp_output_dir / 'README.md').exists()
        assert (temp_output_dir / '.gitignore').exists()

    def test_generate_project_directory_exists_no_overwrite(
        self, file_generator, sample_config, temp_output_dir
    ):
        """Test that FileExistsError is raised when directory exists and overwrite=False."""
        # Create a file in the output directory to make it non-empty
        (temp_output_dir / 'existing_file.txt').write_text('existing content')

        with pytest.raises(FileExistsError, match="already exists"):
            file_generator.generate_project(
                config=sample_config,
                output_dir=temp_output_dir,
                overwrite=False
            )

    def test_generate_project_directory_exists_with_overwrite(
        self, file_generator, sample_config, temp_output_dir
    ):
        """Test that existing directory is overwritten when overwrite=True."""
        # Create a file in the output directory
        existing_file = temp_output_dir / 'existing_file.txt'
        existing_file.write_text('existing content')

        result = file_generator.generate_project(
            config=sample_config,
            output_dir=temp_output_dir,
            overwrite=True,
            recommend_plugins=False
        )

        # Should succeed
        assert result is not None
        assert 'agents' in result

    def test_generate_project_empty_directory_no_overwrite(
        self, file_generator, sample_config, temp_output_dir
    ):
        """Test that empty directory is allowed even with overwrite=False."""
        # Ensure directory is empty
        assert not any(temp_output_dir.iterdir())

        result = file_generator.generate_project(
            config=sample_config,
            output_dir=temp_output_dir,
            overwrite=False,
            recommend_plugins=False
        )

        # Should succeed
        assert result is not None

    def test_generate_project_without_plugins(
        self, file_generator, sample_config, temp_output_dir
    ):
        """Test project generation without plugin recommendations."""
        result = file_generator.generate_project(
            config=sample_config,
            output_dir=temp_output_dir,
            recommend_plugins=False
        )

        # Verify plugins.yaml was NOT created
        assert not (temp_output_dir / '.claude' / 'plugins.yaml').exists()

        # Verify other files were created
        assert (temp_output_dir / 'README.md').exists()
        assert (temp_output_dir / '.gitignore').exists()

    def test_generate_project_creates_directory_structure(
        self, file_generator, sample_config, temp_output_dir
    ):
        """Test that directory structure is created correctly."""
        file_generator.generate_project(
            config=sample_config,
            output_dir=temp_output_dir,
            recommend_plugins=False
        )

        # Verify directories from project type config
        assert (temp_output_dir / 'src').exists()
        assert (temp_output_dir / 'tests').exists()
        assert (temp_output_dir / 'app').exists()

        # Verify __init__.py files for Python projects
        assert (temp_output_dir / 'src' / '__init__.py').exists()
        assert (temp_output_dir / 'app' / '__init__.py').exists()


# ==================== Test _generate_agent() ====================

class TestGenerateAgent:
    """Test agent file generation."""

    def test_generate_reusable_agent(
        self, file_generator, temp_output_dir
    ):
        """Test generating a reusable agent (copy as-is, no .j2)."""
        context = {'project_name': 'Test'}
        template_path = 'agents/library/testing-agent.md'

        result = file_generator._generate_agent(
            template_path=template_path,
            context=context,
            output_dir=temp_output_dir
        )

        # Verify file created
        assert result.exists()
        assert result.name == 'testing-agent.md'
        assert result.parent == temp_output_dir / '.claude' / 'agents'

        # Verify content is copied as-is
        content = result.read_text()
        assert '# Testing Agent' in content
        assert 'reusable testing agent' in content

    def test_generate_template_agent(
        self, file_generator, temp_output_dir
    ):
        """Test generating a template agent (render .j2)."""
        context = {
            'project_name': 'My Project',
            'project_slug': 'my-project'
        }
        template_path = 'agents/testing-template-agent.md.j2'

        result = file_generator._generate_agent(
            template_path=template_path,
            context=context,
            output_dir=temp_output_dir
        )

        # Verify file created with .j2 removed
        assert result.exists()
        assert result.name == 'testing-template-agent.md'

        # Verify template was rendered
        content = result.read_text()
        assert 'My Project Testing' in content

    def test_generate_agent_creates_directory(
        self, file_generator, temp_output_dir
    ):
        """Test that agent directory is created if it doesn't exist."""
        # Ensure directory doesn't exist
        agents_dir = temp_output_dir / '.claude' / 'agents'
        assert not agents_dir.exists()

        template_path = 'agents/library/testing-agent.md'
        result = file_generator._generate_agent(
            template_path=template_path,
            context={},
            output_dir=temp_output_dir
        )

        # Verify directory was created
        assert agents_dir.exists()
        assert result.parent == agents_dir


# ==================== Test _generate_skill() ====================

class TestGenerateSkill:
    """Test skill directory generation."""

    def test_generate_library_skill(
        self, file_generator, temp_output_dir
    ):
        """Test generating a library skill (copy as-is)."""
        context = {'project_name': 'Test'}
        template_path = 'skills/library/python-fastapi/SKILL.md'

        result = file_generator._generate_skill(
            template_path=template_path,
            context=context,
            output_dir=temp_output_dir
        )

        # Verify skill directory created
        assert result.exists()
        assert result.is_dir()
        assert result.name == 'python-fastapi'

        # Verify SKILL.md file
        skill_file = result / 'SKILL.md'
        assert skill_file.exists()
        content = skill_file.read_text()
        assert '# Python FastAPI Skill' in content

    def test_generate_library_skill_copies_additional_files(
        self, file_generator, temp_output_dir
    ):
        """Test that additional files in skill directory are copied."""
        context = {'project_name': 'Test'}
        template_path = 'skills/library/python-fastapi/SKILL.md'

        result = file_generator._generate_skill(
            template_path=template_path,
            context=context,
            output_dir=temp_output_dir
        )

        # Verify additional files were copied
        helper_file = result / 'helper.py'
        assert helper_file.exists()
        assert '# Helper file' in helper_file.read_text()

    def test_generate_skill_skips_skill_md_files(
        self, file_generator, temp_output_dir
    ):
        """Test that SKILL.md and SKILL.md.j2 are not copied as additional files."""
        context = {'project_name': 'Test'}
        template_path = 'skills/library/python-fastapi/SKILL.md'

        result = file_generator._generate_skill(
            template_path=template_path,
            context=context,
            output_dir=temp_output_dir
        )

        # Verify only one SKILL.md exists (not duplicated)
        skill_files = list(result.glob('SKILL.md*'))
        assert len(skill_files) == 1
        assert skill_files[0].name == 'SKILL.md'


# ==================== Test _generate_command() ====================

class TestGenerateCommand:
    """Test command file generation."""

    def test_generate_command(
        self, file_generator, temp_output_dir
    ):
        """Test generating a command file."""
        context = {'project_name': 'My Project'}
        template_path = 'commands/run-tests.md.j2'

        result = file_generator._generate_command(
            template_path=template_path,
            context=context,
            output_dir=temp_output_dir
        )

        # Verify file created
        assert result.exists()
        assert result.name == 'run-tests.md'
        assert result.parent == temp_output_dir / '.claude' / 'commands'

        # Verify content rendered
        content = result.read_text()
        assert 'Run tests for My Project' in content

    def test_generate_command_removes_j2_extension(
        self, file_generator, temp_output_dir
    ):
        """Test that .j2 extension is removed from command filename."""
        template_path = 'commands/deploy.md.j2'

        result = file_generator._generate_command(
            template_path=template_path,
            context={},
            output_dir=temp_output_dir
        )

        # Verify .j2 removed
        assert result.name == 'deploy.md'
        assert not result.name.endswith('.j2')

    def test_generate_command_creates_directory(
        self, file_generator, temp_output_dir
    ):
        """Test that commands directory is created."""
        commands_dir = temp_output_dir / '.claude' / 'commands'
        assert not commands_dir.exists()

        file_generator._generate_command(
            template_path='commands/run-tests.md.j2',
            context={},
            output_dir=temp_output_dir
        )

        assert commands_dir.exists()


# ==================== Test _generate_doc() ====================

class TestGenerateDoc:
    """Test documentation file generation."""

    def test_generate_template_doc(
        self, file_generator, temp_output_dir
    ):
        """Test generating a template doc (render .j2)."""
        context = {'project_name': 'My Project'}
        template_path = 'docs/API.md.j2'

        result = file_generator._generate_doc(
            template_path=template_path,
            context=context,
            output_dir=temp_output_dir
        )

        # Verify file created
        assert result.exists()
        assert result.name == 'API.md'
        assert result.parent == temp_output_dir / 'docs'

        # Verify template rendered
        content = result.read_text()
        assert 'My Project API' in content

    def test_generate_library_doc(
        self, file_generator, temp_output_dir
    ):
        """Test generating a library doc (copy as-is)."""
        context = {}
        template_path = 'docs/library/TESTING.md'

        result = file_generator._generate_doc(
            template_path=template_path,
            context=context,
            output_dir=temp_output_dir
        )

        # Verify file created
        assert result.exists()
        assert result.name == 'TESTING.md'

        # Verify content copied as-is
        content = result.read_text()
        assert '# Testing Guide' in content

    def test_generate_doc_skips_library_readme(
        self, file_generator, temp_output_dir
    ):
        """Test that library READMEs are skipped (handled by _generate_readme)."""
        template_path = 'docs/library/README-saas-web-app.md'

        result = file_generator._generate_doc(
            template_path=template_path,
            context={},
            output_dir=temp_output_dir
        )

        # Should return README.md path but not create it via _generate_doc
        assert result == temp_output_dir / 'README.md'

    def test_generate_doc_handles_missing_library_doc(
        self, file_generator, temp_output_dir, caplog
    ):
        """Test graceful handling of missing library doc."""
        import logging
        caplog.set_level(logging.WARNING)

        template_path = 'docs/library/NONEXISTENT.md'

        result = file_generator._generate_doc(
            template_path=template_path,
            context={},
            output_dir=temp_output_dir
        )

        # Should return expected path but not fail
        assert result == temp_output_dir / 'docs' / 'NONEXISTENT.md'

        # Should log warning
        assert any('Library doc not found' in record.message for record in caplog.records)

    def test_generate_doc_handles_missing_template(
        self, file_generator, temp_output_dir, caplog
    ):
        """Test graceful handling of missing template doc."""
        import logging
        caplog.set_level(logging.WARNING)

        template_path = 'docs/NONEXISTENT.md.j2'

        result = file_generator._generate_doc(
            template_path=template_path,
            context={},
            output_dir=temp_output_dir
        )

        # Should return expected path
        assert result == temp_output_dir / 'docs' / 'NONEXISTENT.md'

        # Should log warning
        assert any('Doc template not found' in record.message for record in caplog.records)


# ==================== Test _generate_readme() ====================

class TestGenerateReadme:
    """Test README generation."""

    def test_generate_readme_with_library_template(
        self, file_generator, temp_output_dir, caplog
    ):
        """Test README generation using library template."""
        import logging
        caplog.set_level(logging.INFO)

        context = {
            'project_type': 'saas-web-app',
            'project_name': 'My SaaS',
            'description': 'A SaaS application'
        }

        result = file_generator._generate_readme(
            context=context,
            output_dir=temp_output_dir
        )

        # Verify README created
        assert result.exists()
        assert result.name == 'README.md'

        # Verify library template was used
        content = result.read_text()
        assert 'SaaS Web App README' in content

        # Verify message logged
        assert any('comprehensive README' in record.message for record in caplog.records)

    def test_generate_readme_fallback_to_basic(
        self, file_generator, temp_output_dir, caplog
    ):
        """Test README generation falls back to basic template when library missing."""
        import logging
        caplog.set_level(logging.WARNING)

        context = {
            'project_type': 'nonexistent-type',
            'project_name': 'My Project',
            'description': 'A test project',
            'backend_framework': 'fastapi',
            'frontend_framework': 'react',
            'database': 'postgresql',
            'features': ['authentication', 'api']
        }

        result = file_generator._generate_readme(
            context=context,
            output_dir=temp_output_dir
        )

        # Verify README created
        assert result.exists()

        # Verify basic template was used
        content = result.read_text()
        assert 'My Project' in content
        assert 'A test project' in content
        assert 'fastapi' in content
        assert 'react' in content
        assert 'authentication' in content.lower()

        # Verify warning logged
        assert any('Library README not found' in record.message and 'basic template' in record.message for record in caplog.records)

    def test_generate_basic_readme_includes_features(
        self, file_generator, temp_output_dir
    ):
        """Test that basic README includes all features."""
        context = {
            'project_type': 'custom',
            'project_name': 'Feature Rich App',
            'description': 'An app with many features',
            'features': ['user_authentication', 'payment_processing', 'real_time_notifications']
        }

        result = file_generator._generate_readme(
            context=context,
            output_dir=temp_output_dir
        )

        content = result.read_text()
        assert 'User Authentication' in content
        assert 'Payment Processing' in content
        assert 'Real Time Notifications' in content


# ==================== Test _generate_gitignore() ====================

class TestGenerateGitignore:
    """Test .gitignore generation."""

    def test_generate_gitignore(
        self, file_generator, temp_output_dir
    ):
        """Test .gitignore file generation."""
        result = file_generator._generate_gitignore(
            context={},
            output_dir=temp_output_dir
        )

        # Verify file created
        assert result.exists()
        assert result.name == '.gitignore'

        # Verify content includes common patterns
        content = result.read_text()
        assert '__pycache__/' in content
        assert 'node_modules/' in content
        assert '.env' in content
        assert '*.db' in content
        assert '.vscode/' in content
        assert '.DS_Store' in content

    def test_generate_gitignore_comprehensive_coverage(
        self, file_generator, temp_output_dir
    ):
        """Test that gitignore covers Python, Node, IDE, env, DB, build, test, and OS."""
        result = file_generator._generate_gitignore({}, temp_output_dir)
        content = result.read_text()

        # Python patterns
        assert '*.py[cod]' in content
        assert 'venv/' in content

        # Node patterns
        assert 'yarn-error.log*' in content

        # IDE patterns
        assert '.idea/' in content
        assert '*.swp' in content

        # Environment patterns
        assert '.env.local' in content

        # Database patterns
        assert '*.sqlite3' in content

        # Build patterns
        assert 'dist/' in content
        assert '*.egg-info/' in content

        # Testing patterns
        assert '.coverage' in content
        assert '.pytest_cache/' in content

        # OS patterns
        assert 'Thumbs.db' in content


# ==================== Test _generate_plugin_config() ====================

class TestGeneratePluginConfig:
    """Test plugin configuration generation."""

    def test_generate_plugin_config(
        self, file_generator, sample_config, temp_output_dir
    ):
        """Test plugin config generation."""
        # Mock the plugin analyzer to avoid API calls
        with patch.object(file_generator.plugin_analyzer, 'get_plugin_config_dict') as mock_method:
            mock_method.return_value = {
                'plugins': {
                    'testing': {'enabled': True},
                    'linting': {'enabled': True}
                }
            }

            result = file_generator._generate_plugin_config(
                config=sample_config,
                output_dir=temp_output_dir,
                use_ai=False
            )

            # Verify file created
            assert result.exists()
            assert result.name == 'plugins.yaml'
            assert result.parent == temp_output_dir / '.claude'

            # Verify YAML content
            with open(result, 'r') as f:
                config = yaml.safe_load(f)
            assert 'plugins' in config
            assert 'testing' in config['plugins']

            # Verify method was called
            mock_method.assert_called_once_with(sample_config, use_ai=False)

    def test_generate_plugin_config_creates_claude_directory(
        self, file_generator, sample_config, temp_output_dir
    ):
        """Test that .claude directory is created if missing."""
        claude_dir = temp_output_dir / '.claude'
        assert not claude_dir.exists()

        with patch.object(file_generator.plugin_analyzer, 'get_plugin_config_dict') as mock_method:
            mock_method.return_value = {'plugins': {}}

            file_generator._generate_plugin_config(
                config=sample_config,
                output_dir=temp_output_dir
            )

            assert claude_dir.exists()


# ==================== Test _create_directory_structure() ====================

class TestCreateDirectoryStructure:
    """Test directory structure creation."""

    def test_create_directory_structure_basic(
        self, file_generator, sample_config, temp_output_dir
    ):
        """Test basic directory structure creation."""
        file_generator._create_directory_structure(
            config=sample_config,
            output_dir=temp_output_dir
        )

        # Verify directories created
        assert (temp_output_dir / 'src').exists()
        assert (temp_output_dir / 'tests').exists()
        assert (temp_output_dir / 'app').exists()

    def test_create_directory_structure_creates_init_files_for_python(
        self, file_generator, sample_config, temp_output_dir
    ):
        """Test that __init__.py files are created for Python projects."""
        file_generator._create_directory_structure(
            config=sample_config,
            output_dir=temp_output_dir
        )

        # Verify __init__.py files
        assert (temp_output_dir / 'src' / '__init__.py').exists()
        assert (temp_output_dir / 'app' / '__init__.py').exists()

        # Verify content
        content = (temp_output_dir / 'src' / '__init__.py').read_text()
        assert '"""Package module."""' in content

    def test_create_directory_structure_no_duplicate_init_files(
        self, file_generator, sample_config, temp_output_dir
    ):
        """Test that __init__.py files are not duplicated."""
        # Create directory with existing __init__.py
        src_dir = temp_output_dir / 'src'
        src_dir.mkdir(parents=True)
        init_file = src_dir / '__init__.py'
        init_file.write_text('# Existing init file')

        file_generator._create_directory_structure(
            config=sample_config,
            output_dir=temp_output_dir
        )

        # Verify existing file not overwritten
        content = init_file.read_text()
        assert '# Existing init file' in content
        assert content.count('"""Package module."""') == 0


# ==================== Error Handling and Edge Cases ====================

class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_file_exists_error_with_non_empty_directory(
        self, file_generator, sample_config, temp_output_dir
    ):
        """Test FileExistsError when directory is non-empty."""
        # Create a non-empty directory
        (temp_output_dir / 'file.txt').write_text('content')

        with pytest.raises(FileExistsError):
            file_generator.generate_project(
                config=sample_config,
                output_dir=temp_output_dir,
                overwrite=False
            )

    def test_handles_special_characters_in_project_name(
        self, file_generator, temp_output_dir
    ):
        """Test handling of special characters in project names."""
        config = ProjectConfig(
            project_name="My Ûñíçödé Project!",
            project_slug="my-unicode-project",
            description="Testing unicode",
            project_type="saas-web-app",
            backend_framework="fastapi",
            features=[]
        )

        # Should not raise an error
        result = file_generator.generate_project(
            config=config,
            output_dir=temp_output_dir,
            recommend_plugins=False
        )

        assert result is not None

    def test_handles_empty_features_list(
        self, file_generator, temp_output_dir
    ):
        """Test handling of empty features list."""
        config = ProjectConfig(
            project_name="Minimal Project",
            project_slug="minimal",
            description="Minimal config",
            project_type="saas-web-app",
            backend_framework="fastapi",
            features=[]
        )

        result = file_generator.generate_project(
            config=config,
            output_dir=temp_output_dir,
            recommend_plugins=False
        )

        # Should succeed with empty features
        assert result is not None
        assert 'agents' in result

    def test_path_normalization(
        self, file_generator, sample_config, tmp_path
    ):
        """Test that paths are properly normalized."""
        # Use string path instead of Path object
        output_dir_str = str(tmp_path / 'output')

        result = file_generator.generate_project(
            config=sample_config,
            output_dir=output_dir_str,
            recommend_plugins=False
        )

        # Should work with string paths
        assert result is not None
        # Verify paths are Path objects
        for files in result.values():
            for file_path in files:
                assert isinstance(file_path, Path)

    def test_path_traversal_blocked(
        self, file_generator, sample_config
    ):
        """Test that path traversal attempts are blocked (security fix)."""
        # Test 1: Path with .. at the beginning
        with pytest.raises(ValueError, match="Path traversal not allowed"):
            file_generator.generate_project(
                config=sample_config,
                output_dir="../../../etc/passwd",
                recommend_plugins=False
            )

        # Test 2: Path with .. in the middle
        with pytest.raises(ValueError, match="Path traversal not allowed"):
            file_generator.generate_project(
                config=sample_config,
                output_dir="/home/user/../admin/config",
                recommend_plugins=False
            )

        # Test 3: Relative path with ..
        with pytest.raises(ValueError, match="Path traversal not allowed"):
            file_generator.generate_project(
                config=sample_config,
                output_dir="./test/../../../secret",
                recommend_plugins=False
            )

    def test_validate_output_path_security(
        self, file_generator
    ):
        """Test _validate_output_path method directly for security."""
        # Valid paths should pass
        valid_path = file_generator._validate_output_path("./test-output")
        assert valid_path is not None
        assert isinstance(valid_path, Path)

        # Paths with .. should be rejected BEFORE resolving
        with pytest.raises(ValueError, match="Path traversal not allowed"):
            file_generator._validate_output_path("../malicious")

        with pytest.raises(ValueError, match="Path traversal not allowed"):
            file_generator._validate_output_path("test/../../../etc")

        with pytest.raises(ValueError, match="Path traversal not allowed"):
            file_generator._validate_output_path("/home/user/..")

    def test_validate_output_path_length(
        self, file_generator
    ):
        """Test that overly long paths are rejected."""
        # Create a path longer than MAX_PATH_LENGTH
        long_path = "a" * 300  # Longer than typical MAX_PATH_LENGTH

        with pytest.raises(ValueError, match="Output path too long"):
            file_generator._validate_output_path(long_path)
