---
name: jinja2-templating
description: Expert knowledge in Jinja2 template engine for code generation, including template syntax, filters, macros, inheritance, custom filters, template loading, and rendering. Use this skill when designing templates, implementing template renderers, creating custom filters, debugging template syntax, handling template variables, or building code generation systems with Jinja2.
allowed-tools: [Read, Write]
---

# Jinja2 Templating Skill

Comprehensive knowledge for building robust template systems with Jinja2, specialized for code generation and dynamic file creation.

## Core Concepts

### Template Basics

**Variable Substitution:**
```jinja2
Hello, {{ name }}!
Your email is: {{ email }}
```

**Expressions:**
```jinja2
{{ user.name }}
{{ items[0] }}
{{ dict['key'] }}
{{ function(arg1, arg2) }}
{{ value | filter }}
{{ value1 + value2 }}
```

### Control Structures

**If Statements:**
```jinja2
{% if user.is_admin %}
  <p>Welcome, admin!</p>
{% elif user.is_authenticated %}
  <p>Welcome, {{ user.name }}!</p>
{% else %}
  <p>Please log in.</p>
{% endif %}
```

**For Loops:**
```jinja2
{% for item in items %}
  {{ loop.index }}. {{ item }}
{% endfor %}

{# Loop variables #}
{% for user in users %}
  {{ loop.index }}     - Current iteration (1-indexed)
  {{ loop.index0 }}    - Current iteration (0-indexed)
  {{ loop.first }}     - True if first iteration
  {{ loop.last }}      - True if last iteration
  {{ loop.length }}    - Total number of items
{% endfor %}
```

**With Empty Block:**
```jinja2
{% for item in items %}
  {{ item }}
{% else %}
  No items found.
{% endfor %}
```

### Comments

```jinja2
{# Single line comment #}

{#
   Multi-line comment
   Can span multiple lines
#}

{#- Trim whitespace before -#}
{#- Trim whitespace after -#}
```

### Whitespace Control

```jinja2
{# Remove whitespace before #}
{%- if true %}
  content
{%- endif %}

{# Remove whitespace after #}
{% if true -%}
  content
{% endif -%}

{# Remove both #}
{%- if true -%}
  content
{%- endif -%}
```

## Built-in Filters

### String Filters

```jinja2
{{ "hello world" | capitalize }}      # "Hello world"
{{ "HELLO" | lower }}                 # "hello"
{{ "hello" | upper }}                 # "HELLO"
{{ "hello world" | title }}           # "Hello World"

{{ "  hello  " | trim }}              # "hello"
{{ "hello world" | replace("world", "there") }}  # "hello there"

{{ "hello" | length }}                # 5
{{ "hello world" | wordcount }}       # 2

{{ "hello world" | truncate(8) }}     # "hello..."
{{ "hello world" | truncate(8, True) }}  # "hello w..."
```

### List Filters

```jinja2
{{ [1, 2, 3] | first }}               # 1
{{ [1, 2, 3] | last }}                # 3
{{ [1, 2, 3] | length }}              # 3
{{ [1, 2, 3] | sum }}                 # 6
{{ [1, 2, 3] | max }}                 # 3
{{ [1, 2, 3] | min }}                 # 1

{{ [3, 1, 2] | sort }}                # [1, 2, 3]
{{ [1, 2, 3] | reverse }}             # [3, 2, 1]
{{ [1, 2, 2, 3] | unique }}           # [1, 2, 3]

{{ ['a', 'b', 'c'] | join(', ') }}    # "a, b, c"
{{ [1, 2, 3] | map('string') | join }}  # "123"
```

### Other Useful Filters

```jinja2
{{ value | default('N/A') }}          # Use default if undefined
{{ value | default('N/A', true) }}    # Use default if falsy

{{ none_value | default('empty') }}   # "empty"
{{ '' | default('empty', true) }}     # "empty"

{{ obj | tojson }}                    # Convert to JSON string
{{ obj | tojson(indent=2) }}          # Pretty JSON

{{ text | safe }}                     # Mark as safe (no escaping)
{{ html | escape }}                   # Escape HTML entities

{{ num | int }}                       # Convert to integer
{{ text | float }}                    # Convert to float
{{ value | string }}                  # Convert to string
```

## Template Inheritance

### Base Template

```jinja2
{# base.html.j2 #}
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Default Title{% endblock %}</title>
    {% block extra_css %}{% endblock %}
</head>
<body>
    <header>
        {% block header %}
        <h1>My Site</h1>
        {% endblock %}
    </header>

    <main>
        {% block content %}
        <!-- Main content goes here -->
        {% endblock %}
    </main>

    <footer>
        {% block footer %}
        <p>&copy; 2025</p>
        {% endblock %}
    </footer>

    {% block extra_js %}{% endblock %}
</body>
</html>
```

### Child Template

```jinja2
{# page.html.j2 #}
{% extends "base.html.j2" %}

{% block title %}My Page{% endblock %}

{% block content %}
    <h2>Page Content</h2>
    <p>This is my custom content.</p>

    {# Call parent block content #}
    {{ super() }}
{% endblock %}

{% block extra_css %}
    <link rel="stylesheet" href="custom.css">
{% endblock %}
```

## Macros (Reusable Components)

### Defining Macros

```jinja2
{# macros.j2 #}
{% macro button(text, type='primary', size='medium') %}
    <button class="btn btn-{{ type }} btn-{{ size }}">
        {{ text }}
    </button>
{% endmacro %}

{% macro input(name, label, type='text', required=false) %}
    <div class="form-group">
        <label for="{{ name }}">{{ label }}</label>
        <input
            type="{{ type }}"
            name="{{ name }}"
            id="{{ name }}"
            {% if required %}required{% endif %}
        >
    </div>
{% endmacro %}

{% macro code_block(language='python') %}
    ```{{ language }}
    {{ caller() }}
    ```
{% endmacro %}
```

### Using Macros

```jinja2
{% from 'macros.j2' import button, input, code_block %}

{{ button('Submit', type='success') }}
{{ button('Cancel', type='danger', size='small') }}

{{ input('email', 'Email Address', type='email', required=true) }}

{# Using macro with caller #}
{% call code_block('python') %}
def hello():
    print("Hello!")
{% endcall %}
```

## Includes

```jinja2
{# Include entire template #}
{% include 'header.j2' %}

{# Include with variables #}
{% include 'item.j2' with context %}

{# Include with specific variables #}
{% include 'user_card.j2', user=current_user %}

{# Conditional include #}
{% include 'admin_panel.j2' ignore missing %}
```

## Custom Filters

### Creating Custom Filters

```python
from jinja2 import Environment, FileSystemLoader
import re

def slugify(text):
    """Convert text to URL-friendly slug."""
    slug = text.lower()
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    slug = slug.strip('-')
    slug = re.sub(r'-+', '-', slug)
    return slug

def pascal_case(text):
    """Convert text to PascalCase."""
    words = re.findall(r'[a-zA-Z0-9]+', text)
    return ''.join(word.capitalize() for word in words)

def snake_case(text):
    """Convert text to snake_case."""
    text = re.sub(r'([A-Z])', r'_\1', text)
    text = re.sub(r'[\s-]+', '_', text)
    text = re.sub(r'_+', '_', text)
    return text.lower().strip('_')

def indent_code(code, spaces=4):
    """Indent code block."""
    indent = ' ' * spaces
    lines = code.split('\n')
    return '\n'.join(indent + line if line.strip() else line for line in lines)

# Register filters
env = Environment(loader=FileSystemLoader('templates'))
env.filters['slugify'] = slugify
env.filters['pascalcase'] = pascal_case
env.filters['snakecase'] = snake_case
env.filters['indent_code'] = indent_code
```

### Using Custom Filters

```jinja2
{{ "My Project Name" | slugify }}           # "my-project-name"
{{ "my_variable_name" | pascalcase }}       # "MyVariableName"
{{ "MyClassName" | snakecase }}             # "my_class_name"

{{ code_sample | indent_code(8) }}
```

## Template Loading and Rendering

### Basic Setup

```python
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path

# Create environment
env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=select_autoescape(['html', 'xml']),
    trim_blocks=True,           # Remove first newline after block
    lstrip_blocks=True,         # Remove leading whitespace
    keep_trailing_newline=True  # Keep trailing newline in output
)

# Load template
template = env.get_template('my_template.j2')

# Render with context
output = template.render(
    name='John',
    items=['a', 'b', 'c'],
    user={'email': 'john@example.com'}
)

# Save to file
Path('output.txt').write_text(output)
```

### Advanced Environment Configuration

```python
from jinja2 import Environment, FileSystemLoader, ChoiceLoader, PrefixLoader

# Multiple template directories
loader = ChoiceLoader([
    FileSystemLoader('templates'),
    FileSystemLoader('fallback_templates')
])

# Prefixed loaders (namespaces)
loader = PrefixLoader({
    'base': FileSystemLoader('templates/base'),
    'components': FileSystemLoader('templates/components')
})

# Use: {% extends "base/layout.j2" %}
#      {% include "components/button.j2" %}

env = Environment(
    loader=loader,
    # Custom delimiters (if {{ }} conflicts with your output)
    variable_start_string='<{',
    variable_end_string='}>',
    block_start_string='<{%',
    block_end_string='%}>',
    comment_start_string='<{#',
    comment_end_string='#}>',
)
```

### Error Handling

```python
from jinja2 import TemplateNotFound, UndefinedError, TemplateSyntaxError

try:
    template = env.get_template('nonexistent.j2')
except TemplateNotFound:
    print("Template file not found")

try:
    output = template.render(context)
except UndefinedError as e:
    print(f"Missing variable: {e}")
except TemplateSyntaxError as e:
    print(f"Template syntax error at line {e.lineno}: {e.message}")
```

## Practical Patterns for Code Generation

### 1. Agent Template

```jinja2
{# agent.j2 #}
{#
Variables:
  - project_name (str): Human-readable project name
  - project_slug (str): kebab-case identifier
  - agent_role (str): Agent's role/specialty
  - tech_stack (dict): Technology stack details
  - features (list): List of features
#}
---
name: {{ project_slug }}-{{ agent_role }}-agent
description: Use this agent for {{ agent_role }} tasks in {{ project_name }}.
model: sonnet
tools: Read, Write, Grep, Bash
---

# {{ agent_role | title }} Agent

You are an expert {{ agent_role }} developer for {{ project_name }}.

## Tech Stack

{% for key, value in tech_stack.items() %}
- **{{ key | title }}:** {{ value }}
{% endfor %}

## Features

{% if features %}
{% for feature in features %}
- {{ feature }}
{% endfor %}
{% else %}
No special features configured.
{% endif %}

## Your Responsibilities

{% if agent_role == 'api-development' %}
- Design RESTful API endpoints
- Implement request/response handling
- Add comprehensive validation
- Write API documentation
{% elif agent_role == 'frontend' %}
- Build React components
- Implement state management
- Ensure responsive design
- Optimize performance
{% else %}
- Implement {{ agent_role }} functionality
- Follow best practices
- Write comprehensive tests
{% endif %}
```

### 2. Configuration File Template

```jinja2
{# docker-compose.yml.j2 #}
version: '3.8'

services:
  {% if tech_stack.backend %}
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL={{ database_url }}
    {% if tech_stack.database %}
    depends_on:
      - {{ tech_stack.database }}
    {% endif %}
  {% endif %}

  {% if tech_stack.database == 'postgresql' %}
  postgresql:
    image: postgres:15
    environment:
      POSTGRES_DB: {{ project_slug }}
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
  {% elif tech_stack.database == 'mongodb' %}
  mongodb:
    image: mongo:6
    environment:
      MONGO_INITDB_DATABASE: {{ project_slug }}
    volumes:
      - mongo_data:/data/db
  {% endif %}

volumes:
  {% if tech_stack.database == 'postgresql' %}
  postgres_data:
  {% elif tech_stack.database == 'mongodb' %}
  mongo_data:
  {% endif %}
```

### 3. README Template

```jinja2
{# README.md.j2 #}
# {{ project_name }}

{{ description }}

## Tech Stack

{% if tech_stack.backend -%}
- **Backend:** {{ tech_stack.backend }}
{% endif -%}
{% if tech_stack.frontend -%}
- **Frontend:** {{ tech_stack.frontend }}
{% endif -%}
{% if tech_stack.database -%}
- **Database:** {{ tech_stack.database }}
{% endif %}

## Features

{% for feature in features -%}
- {{ feature }}
{% endfor %}

## Getting Started

### Prerequisites

{%- if 'python' in tech_stack.backend | lower %}
- Python 3.9+
- pip
{%- elif 'node' in tech_stack.backend | lower %}
- Node.js 18+
- npm or yarn
{%- endif %}

### Installation

```bash
# Clone repository
git clone https://github.com/{{ github_username }}/{{ project_slug }}.git
cd {{ project_slug }}

{%- if 'python' in tech_stack.backend | lower %}

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
{%- elif 'node' in tech_stack.backend | lower %}

# Install dependencies
npm install
{%- endif %}

# Run development server
{%- if 'fastapi' in tech_stack.backend | lower %}
uvicorn main:app --reload
{%- elif 'express' in tech_stack.backend | lower %}
npm run dev
{%- endif %}
```

## License

MIT
```

### 4. API Endpoint Template

```jinja2
{# routes.py.j2 #}
{%- macro create_route(resource, methods=['GET', 'POST', 'PUT', 'DELETE']) -%}
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .database import get_db
from .models import {{ resource | pascalcase }}
from .schemas import {{ resource | pascalcase }}Create, {{ resource | pascalcase }}Response

router = APIRouter(prefix="/{{ resource | lower }}s", tags=["{{ resource | lower }}s"])

{% if 'GET' in methods %}
@router.get("/", response_model=List[{{ resource | pascalcase }}Response])
def list_{{ resource | lower }}s(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all {{ resource | lower }}s."""
    {{ resource | lower }}s = db.query({{ resource | pascalcase }}).offset(skip).limit(limit).all()
    return {{ resource | lower }}s

@router.get("/{id}", response_model={{ resource | pascalcase }}Response)
def get_{{ resource | lower }}(id: int, db: Session = Depends(get_db)):
    """Get specific {{ resource | lower }} by ID."""
    {{ resource | lower }} = db.query({{ resource | pascalcase }}).filter({{ resource | pascalcase }}.id == id).first()
    if not {{ resource | lower }}:
        raise HTTPException(status_code=404, detail="{{ resource | pascalcase }} not found")
    return {{ resource | lower }}
{% endif %}

{% if 'POST' in methods %}
@router.post("/", response_model={{ resource | pascalcase }}Response, status_code=201)
def create_{{ resource | lower }}(
    {{ resource | lower }}_data: {{ resource | pascalcase }}Create,
    db: Session = Depends(get_db)
):
    """Create new {{ resource | lower }}."""
    {{ resource | lower }} = {{ resource | pascalcase }}(**{{ resource | lower }}_data.dict())
    db.add({{ resource | lower }})
    db.commit()
    db.refresh({{ resource | lower }})
    return {{ resource | lower }}
{% endif %}

{% if 'PUT' in methods %}
@router.put("/{id}", response_model={{ resource | pascalcase }}Response)
def update_{{ resource | lower }}(
    id: int,
    {{ resource | lower }}_data: {{ resource | pascalcase }}Create,
    db: Session = Depends(get_db)
):
    """Update existing {{ resource | lower }}."""
    {{ resource | lower }} = db.query({{ resource | pascalcase }}).filter({{ resource | pascalcase }}.id == id).first()
    if not {{ resource | lower }}:
        raise HTTPException(status_code=404, detail="{{ resource | pascalcase }} not found")

    for key, value in {{ resource | lower }}_data.dict().items():
        setattr({{ resource | lower }}, key, value)

    db.commit()
    db.refresh({{ resource | lower }})
    return {{ resource | lower }}
{% endif %}

{% if 'DELETE' in methods %}
@router.delete("/{id}", status_code=204)
def delete_{{ resource | lower }}(id: int, db: Session = Depends(get_db)):
    """Delete {{ resource | lower }}."""
    {{ resource | lower }} = db.query({{ resource | pascalcase }}).filter({{ resource | pascalcase }}.id == id).first()
    if not {{ resource | lower }}:
        raise HTTPException(status_code=404, detail="{{ resource | pascalcase }} not found")

    db.delete({{ resource | lower }})
    db.commit()
{% endif %}
{%- endmacro -%}

{{ create_route('User') }}
```

## Best Practices

1. **Document template variables**
```jinja2
{#
Variables:
  - project_name (str): Project name
  - features (list[str]): Feature list
  - tech_stack (dict): Technology stack
#}
```

2. **Use meaningful filter names**
```python
env.filters['to_kebab_case'] = slugify  # Clear what it does
```

3. **Provide defaults for optional variables**
```jinja2
{{ title | default('Untitled') }}
{{ items | default([]) }}
```

4. **Use whitespace control wisely**
```jinja2
{%- for item in items -%}
  {{ item }}
{%- endfor -%}
```

5. **Keep templates focused**
```jinja2
{# Good: One responsibility #}
{% include 'header.j2' %}
{% include 'nav.j2' %}
{% include 'content.j2' %}

{# Bad: Everything in one file #}
```

6. **Test templates with various contexts**
```python
test_contexts = [
    {'name': 'Test', 'items': ['a', 'b']},
    {'name': 'Test', 'items': []},
    {'name': 'Test'},  # Missing items
]

for context in test_contexts:
    output = template.render(**context)
    assert output  # Basic validation
```

## Available Resources

- `examples/template_examples.py` - Complete template renderer implementation
- `examples/agent_template.j2` - Agent template example
- `reference/filters.md` - Complete filter reference
- `reference/tests.md` - Built-in tests reference

## Quick Reference

**Variable Output:** `{{ variable }}`
**Control:** `{% if %} {% for %} {% include %}`
**Comments:** `{# comment #}`
**Filters:** `{{ value | filter }}`
**Macros:** `{% macro name() %}`
**Inheritance:** `{% extends %} {% block %}`

**Common Filters:**
- `default`, `length`, `first`, `last`
- `upper`, `lower`, `title`, `capitalize`
- `join`, `sort`, `reverse`, `unique`
- `replace`, `trim`, `truncate`
- `tojson`, `safe`, `escape`
