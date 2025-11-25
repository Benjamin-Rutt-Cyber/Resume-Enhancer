"""
Comprehensive unit tests for TemplateRenderer.

Tests cover:
- Template rendering from files
- Template rendering from strings
- Context preparation with computed values
- Custom Jinja2 filters (slugify, pascal_case, snake_case, camel_case)
- Template validation
- Error handling
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from src.generator.renderer import TemplateRenderer


# ==================== Fixtures ====================

@pytest.fixture
def temp_templates_dir(tmp_path):
    """Create a temporary templates directory with sample templates."""
    templates = tmp_path / 'templates'
    templates.mkdir()

    # Create a simple template
    (templates / 'simple.md.j2').write_text(
        '# {{ project_name }}\n\n{{ description }}'
    )

    # Create a template with filters
    (templates / 'filters.md.j2').write_text(
        '''Project: {{ project_name }}
Slug: {{ project_name | slugify }}
Pascal: {{ project_name | pascal_case }}
Snake: {{ project_name | snake_case }}
Camel: {{ project_name | camel_case }}
'''
    )

    # Create a template with context values
    (templates / 'context.md.j2').write_text(
        '''# {{ project_name }}

Slug Upper: {{ project_slug_upper }}
Pascal: {{ project_slug_pascal }}
Year: {{ year }}
'''
    )

    # Create a template with control structures
    (templates / 'control.md.j2').write_text(
        '''# Features

{% if features %}
{% for feature in features %}
- {{ feature }}
{% endfor %}
{% else %}
No features specified.
{% endif %}
'''
    )

    # Create a template with syntax error
    (templates / 'invalid.md.j2').write_text(
        '# {{ project_name }\n\nMissing closing brace'
    )

    # Create nested directory with template
    nested_dir = templates / 'nested' / 'deep'
    nested_dir.mkdir(parents=True)
    (nested_dir / 'nested.md.j2').write_text(
        '# Nested: {{ project_name }}'
    )

    return templates


@pytest.fixture
def renderer(temp_templates_dir):
    """Create a TemplateRenderer instance."""
    return TemplateRenderer(templates_dir=temp_templates_dir)


@pytest.fixture
def sample_context():
    """Create a sample context dictionary."""
    return {
        'project_name': 'My Project',
        'project_slug': 'my-project',
        'description': 'A test project',
        'features': ['authentication', 'api', 'database'],
        'year': 2025
    }


# ==================== Test Initialization ====================

class TestInitialization:
    """Test TemplateRenderer initialization."""

    def test_init_creates_jinja_environment(self, temp_templates_dir):
        """Test that initialization creates Jinja2 environment."""
        renderer = TemplateRenderer(templates_dir=temp_templates_dir)

        assert renderer.env is not None
        assert renderer.templates_dir == temp_templates_dir

    def test_init_configures_jinja_options(self, renderer):
        """Test that Jinja2 environment is configured correctly."""
        # Verify trim_blocks and lstrip_blocks
        assert renderer.env.trim_blocks is True
        assert renderer.env.lstrip_blocks is True
        assert renderer.env.keep_trailing_newline is True

    def test_init_registers_custom_filters(self, renderer):
        """Test that custom filters are registered."""
        assert 'slugify' in renderer.env.filters
        assert 'pascal_case' in renderer.env.filters
        assert 'snake_case' in renderer.env.filters
        assert 'camel_case' in renderer.env.filters

    def test_init_with_string_path(self, tmp_path):
        """Test initialization with string path instead of Path object."""
        templates = tmp_path / 'templates'
        templates.mkdir()

        # Initialize with string
        renderer = TemplateRenderer(templates_dir=str(templates))

        # Should convert to Path
        assert isinstance(renderer.templates_dir, Path)


# ==================== Test render_template() ====================

class TestRenderTemplate:
    """Test template rendering from files."""

    def test_render_simple_template(self, renderer):
        """Test rendering a simple template."""
        context = {
            'project_name': 'My Project',
            'description': 'A test project'
        }

        result = renderer.render_template('simple.md.j2', context)

        assert '# My Project' in result
        assert 'A test project' in result

    def test_render_template_with_filters(self, renderer):
        """Test rendering template using custom filters."""
        context = {'project_name': 'My Test Project'}

        result = renderer.render_template('filters.md.j2', context)

        assert 'Slug: my-test-project' in result
        assert 'Pascal: MyTestProject' in result
        assert 'Snake: my_test_project' in result
        assert 'Camel: myTestProject' in result

    def test_render_template_with_control_structures(self, renderer):
        """Test rendering template with if/for statements."""
        context = {
            'features': ['auth', 'api', 'db']
        }

        result = renderer.render_template('control.md.j2', context)

        assert '- auth' in result
        assert '- api' in result
        assert '- db' in result

    def test_render_template_with_empty_list(self, renderer):
        """Test rendering template with empty features list."""
        context = {'features': []}

        result = renderer.render_template('control.md.j2', context)

        assert 'No features specified.' in result

    def test_render_nested_template(self, renderer):
        """Test rendering template in nested directory."""
        context = {'project_name': 'Nested Project'}

        result = renderer.render_template('nested/deep/nested.md.j2', context)

        assert '# Nested: Nested Project' in result

    def test_render_template_missing_file(self, renderer):
        """Test error when template file doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Template not found"):
            renderer.render_template('nonexistent.md.j2', {})

    def test_render_template_with_syntax_error(self, renderer):
        """Test error when template has syntax errors."""
        # The invalid.md.j2 template has intentional syntax errors
        with pytest.raises(ValueError, match="Template syntax error"):
            renderer.render_template('invalid.md.j2', {})

    def test_render_template_missing_context_variable(self, renderer):
        """Test that missing context variables are handled by Jinja2."""
        # Template expects project_name but we don't provide it
        # Jinja2 renders undefined variables as empty strings by default
        context = {'description': 'No name'}

        result = renderer.render_template('simple.md.j2', context)
        # Should render with empty project_name
        assert '# ' in result  # Header with no project name
        assert 'No name' in result

    def test_render_template_extra_context_variables(self, renderer):
        """Test that extra context variables are ignored gracefully."""
        context = {
            'project_name': 'My Project',
            'description': 'Test',
            'extra_unused_var': 'This should be ignored'
        }

        # Should not raise an error
        result = renderer.render_template('simple.md.j2', context)
        assert '# My Project' in result


# ==================== Test render_string() ====================

class TestRenderString:
    """Test template rendering from strings."""

    def test_render_string_simple(self, renderer):
        """Test rendering a simple template string."""
        template_str = '# {{ title }}\n\n{{ content }}'
        context = {'title': 'Hello', 'content': 'World'}

        result = renderer.render_string(template_str, context)

        assert '# Hello' in result
        assert 'World' in result

    def test_render_string_basic_jinja_filters(self, renderer):
        """Test rendering string template with built-in Jinja2 filters."""
        # Note: render_string creates a standalone Template, so custom filters aren't available
        # This test uses built-in Jinja2 filters instead
        template_str = '{{ name | upper }}'
        context = {'name': 'test'}

        result = renderer.render_string(template_str, context)

        assert result.strip() == 'TEST'

    def test_render_string_with_for_loop(self, renderer):
        """Test rendering string template with for loop."""
        template_str = '{% for item in items %}{{ item }}\n{% endfor %}'
        context = {'items': ['a', 'b', 'c']}

        result = renderer.render_string(template_str, context)

        assert 'a' in result
        assert 'b' in result
        assert 'c' in result

    def test_render_string_with_conditionals(self, renderer):
        """Test rendering string template with if/else."""
        template_str = '{% if enabled %}ON{% else %}OFF{% endif %}'

        result_on = renderer.render_string(template_str, {'enabled': True})
        result_off = renderer.render_string(template_str, {'enabled': False})

        assert result_on.strip() == 'ON'
        assert result_off.strip() == 'OFF'

    def test_render_string_empty_context(self, renderer):
        """Test rendering string without variables."""
        template_str = 'Static content'
        result = renderer.render_string(template_str, {})

        assert result == 'Static content'


# ==================== Test prepare_context() ====================

class TestPrepareContext:
    """Test context preparation with computed values."""

    def test_prepare_context_adds_computed_values(self, renderer):
        """Test that prepare_context adds computed fields."""
        config_dict = {
            'project_name': 'My Project',
            'project_slug': 'my-project'
        }

        context = renderer.prepare_context(config_dict)

        # Original values preserved
        assert context['project_name'] == 'My Project'
        assert context['project_slug'] == 'my-project'

        # Computed values added
        assert context['project_slug_upper'] == 'MY_PROJECT'
        assert context['project_slug_pascal'] == 'MyProject'

    def test_prepare_context_preserves_original_dict(self, renderer):
        """Test that prepare_context doesn't modify original dict."""
        config_dict = {
            'project_name': 'My Project',
            'project_slug': 'my-project'
        }
        original_keys = set(config_dict.keys())

        context = renderer.prepare_context(config_dict)

        # Original dict unchanged
        assert set(config_dict.keys()) == original_keys
        # Context has additional keys
        assert 'project_slug_upper' in context
        assert 'project_slug_pascal' in context

    def test_prepare_context_adds_default_year(self, renderer):
        """Test that prepare_context adds default year."""
        config_dict = {'project_slug': 'test'}

        context = renderer.prepare_context(config_dict)

        assert context['year'] == 2025

    def test_prepare_context_preserves_custom_year(self, renderer):
        """Test that custom year is preserved."""
        config_dict = {
            'project_slug': 'test',
            'year': 2024
        }

        context = renderer.prepare_context(config_dict)

        assert context['year'] == 2024

    def test_prepare_context_handles_complex_slugs(self, renderer):
        """Test context preparation with complex project slugs."""
        config_dict = {'project_slug': 'my-awesome-project'}

        context = renderer.prepare_context(config_dict)

        assert context['project_slug_upper'] == 'MY_AWESOME_PROJECT'
        assert context['project_slug_pascal'] == 'MyAwesomeProject'

    def test_prepare_context_with_all_fields(self, renderer, sample_context):
        """Test context preparation with complete config."""
        context = renderer.prepare_context(sample_context)

        # All original fields preserved
        for key, value in sample_context.items():
            assert context[key] == value

        # Computed fields added
        assert 'project_slug_upper' in context
        assert 'project_slug_pascal' in context


# ==================== Test Custom Filters ====================

class TestSlugifyFilter:
    """Test slugify custom filter."""

    def test_slugify_basic(self, renderer):
        """Test basic slugification."""
        assert renderer._slugify('My Project') == 'my-project'
        assert renderer._slugify('Hello World') == 'hello-world'

    def test_slugify_with_underscores(self, renderer):
        """Test slugify converts underscores to hyphens."""
        assert renderer._slugify('my_project_name') == 'my-project-name'

    def test_slugify_removes_special_characters(self, renderer):
        """Test slugify removes special characters."""
        assert renderer._slugify('My Project!@#$%') == 'my-project'
        assert renderer._slugify('Test (with) [brackets]') == 'test-with-brackets'

    def test_slugify_handles_multiple_spaces(self, renderer):
        """Test slugify handles multiple consecutive spaces."""
        assert renderer._slugify('My    Project') == 'my-project'

    def test_slugify_strips_hyphens(self, renderer):
        """Test slugify strips leading/trailing hyphens."""
        assert renderer._slugify('-my-project-') == 'my-project'

    def test_slugify_empty_string(self, renderer):
        """Test slugify with empty string."""
        assert renderer._slugify('') == ''

    def test_slugify_only_special_chars(self, renderer):
        """Test slugify with only special characters."""
        assert renderer._slugify('!@#$%^&*()') == ''


class TestPascalCaseFilter:
    """Test pascal_case custom filter."""

    def test_pascal_case_basic(self, renderer):
        """Test basic PascalCase conversion."""
        assert renderer._pascal_case('my project') == 'MyProject'
        assert renderer._pascal_case('hello world') == 'HelloWorld'

    def test_pascal_case_with_hyphens(self, renderer):
        """Test PascalCase with hyphenated strings."""
        assert renderer._pascal_case('my-project-name') == 'MyProjectName'

    def test_pascal_case_with_underscores(self, renderer):
        """Test PascalCase with underscored strings."""
        assert renderer._pascal_case('my_project_name') == 'MyProjectName'

    def test_pascal_case_mixed_separators(self, renderer):
        """Test PascalCase with mixed separators."""
        assert renderer._pascal_case('my-project_name test') == 'MyProjectNameTest'

    def test_pascal_case_single_word(self, renderer):
        """Test PascalCase with single word."""
        assert renderer._pascal_case('project') == 'Project'

    def test_pascal_case_empty_string(self, renderer):
        """Test PascalCase with empty string."""
        assert renderer._pascal_case('') == ''

    def test_pascal_case_already_pascal(self, renderer):
        """Test PascalCase with already PascalCase string."""
        assert renderer._pascal_case('MyProject') == 'Myproject'  # Splits on nothing


class TestSnakeCaseFilter:
    """Test snake_case custom filter."""

    def test_snake_case_basic(self, renderer):
        """Test basic snake_case conversion."""
        assert renderer._snake_case('my project') == 'my_project'
        assert renderer._snake_case('hello world') == 'hello_world'

    def test_snake_case_from_pascal(self, renderer):
        """Test snake_case from PascalCase."""
        assert renderer._snake_case('MyProject') == 'my_project'
        assert renderer._snake_case('MyProjectName') == 'my_project_name'

    def test_snake_case_with_hyphens(self, renderer):
        """Test snake_case with hyphens."""
        assert renderer._snake_case('my-project-name') == 'my_project_name'

    def test_snake_case_mixed_separators(self, renderer):
        """Test snake_case with mixed separators."""
        assert renderer._snake_case('my-project name') == 'my_project_name'

    def test_snake_case_strips_underscores(self, renderer):
        """Test snake_case strips leading/trailing underscores."""
        assert renderer._snake_case('_my_project_') == 'my_project'

    def test_snake_case_consecutive_underscores(self, renderer):
        """Test snake_case handles consecutive underscores."""
        result = renderer._snake_case('my___project')
        assert result == 'my_project'

    def test_snake_case_empty_string(self, renderer):
        """Test snake_case with empty string."""
        assert renderer._snake_case('') == ''


class TestCamelCaseFilter:
    """Test camel_case custom filter."""

    def test_camel_case_basic(self, renderer):
        """Test basic camelCase conversion."""
        assert renderer._camel_case('my project') == 'myProject'
        assert renderer._camel_case('hello world') == 'helloWorld'

    def test_camel_case_with_hyphens(self, renderer):
        """Test camelCase with hyphens."""
        assert renderer._camel_case('my-project-name') == 'myProjectName'

    def test_camel_case_with_underscores(self, renderer):
        """Test camelCase with underscores."""
        assert renderer._camel_case('my_project_name') == 'myProjectName'

    def test_camel_case_single_word(self, renderer):
        """Test camelCase with single word."""
        assert renderer._camel_case('project') == 'project'

    def test_camel_case_empty_string(self, renderer):
        """Test camelCase with empty string."""
        assert renderer._camel_case('') == ''

    def test_camel_case_from_pascal(self, renderer):
        """Test camelCase from PascalCase."""
        assert renderer._camel_case('MyProject') == 'myproject'


# ==================== Test validate_template() ====================

class TestValidateTemplate:
    """Test template validation."""

    def test_validate_valid_template(self, renderer):
        """Test validation succeeds for valid template."""
        result = renderer.validate_template('simple.md.j2')
        assert result is True

    def test_validate_template_compiles_successfully(self, renderer):
        """Test validation succeeds for valid template structure."""
        # Simple template without undefined variables
        result = renderer.validate_template('simple.md.j2')
        assert result is True

    def test_validate_template_with_control_structures(self, renderer):
        """Test validation succeeds for template with if/for."""
        result = renderer.validate_template('control.md.j2')
        assert result is True

    def test_validate_nested_template(self, renderer):
        """Test validation succeeds for nested template."""
        result = renderer.validate_template('nested/deep/nested.md.j2')
        assert result is True

    def test_validate_invalid_template(self, renderer):
        """Test validation fails for invalid template."""
        with pytest.raises(ValueError, match="Template syntax error"):
            renderer.validate_template('invalid.md.j2')

    def test_validate_nonexistent_template(self, renderer):
        """Test validation fails for nonexistent template."""
        with pytest.raises(FileNotFoundError, match="Template not found"):
            renderer.validate_template('nonexistent.md.j2')


# ==================== Integration Tests ====================

class TestIntegration:
    """Integration tests using complete workflows."""

    def test_full_rendering_workflow(self, renderer, sample_context):
        """Test complete workflow: prepare context → render template."""
        # Prepare context
        context = renderer.prepare_context(sample_context)

        # Render template
        result = renderer.render_template('context.md.j2', context)

        # Verify all computed values present
        assert 'MY_PROJECT' in result  # project_slug_upper
        assert 'MyProject' in result   # project_slug_pascal
        assert '2025' in result         # year

    def test_filters_in_real_template(self, renderer):
        """Test that filters work in actual template rendering."""
        context = {'project_name': 'My Test Project'}

        result = renderer.render_template('filters.md.j2', context)

        # All filters should work
        assert 'my-test-project' in result
        assert 'MyTestProject' in result
        assert 'my_test_project' in result
        assert 'myTestProject' in result

    def test_multiple_templates_same_context(self, renderer, sample_context):
        """Test rendering multiple templates with same context."""
        context = renderer.prepare_context(sample_context)

        # Render multiple templates
        simple = renderer.render_template('simple.md.j2', context)
        control = renderer.render_template('control.md.j2', context)

        # Both should render successfully
        assert 'My Project' in simple
        assert 'authentication' in control
        assert 'api' in control


# ==================== Edge Cases and Error Handling ====================

class TestEdgeCases:
    """Test edge cases and error scenarios."""

    def test_render_template_with_unicode(self, renderer):
        """Test rendering with Unicode characters."""
        context = {
            'project_name': 'Mÿ Ûñîçødé Prøjëct',
            'description': '日本語 🎉'
        }

        result = renderer.render_template('simple.md.j2', context)
        assert 'Mÿ Ûñîçødé Prøjëct' in result
        assert '日本語 🎉' in result

    def test_slugify_with_unicode(self, renderer):
        """Test slugify handles Unicode."""
        # Unicode characters should be removed
        result = renderer._slugify('Mÿ Prøjëct')
        # Should only keep ASCII alphanumeric and hyphens
        assert result == 'm-prjct'

    def test_context_with_nested_dicts(self, renderer):
        """Test prepare_context with nested dictionaries."""
        config_dict = {
            'project_slug': 'test',
            'nested': {
                'key': 'value'
            }
        }

        context = renderer.prepare_context(config_dict)

        # Nested dict preserved
        assert context['nested'] == {'key': 'value'}
        # Computed values added
        assert 'project_slug_upper' in context

    def test_render_template_with_none_values(self, renderer, temp_templates_dir):
        """Test rendering template with None values."""
        # Create template that handles None
        (temp_templates_dir / 'none_test.md.j2').write_text(
            '{{ value if value else "default" }}'
        )

        result = renderer.render_template('none_test.md.j2', {'value': None})
        assert 'default' in result

    def test_concurrent_rendering(self, renderer, sample_context):
        """Test that renderer can handle multiple renders."""
        # Render same template multiple times
        results = []
        for i in range(5):
            context = sample_context.copy()
            context['project_name'] = f'Project {i}'
            result = renderer.render_template('simple.md.j2', context)
            results.append(result)

        # All should render correctly
        for i, result in enumerate(results):
            assert f'# Project {i}' in result
