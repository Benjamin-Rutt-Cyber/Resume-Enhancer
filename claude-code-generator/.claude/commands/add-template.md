# Add Template

Add a new agent, skill, or command template to the template library.

## Tasks to Complete

1. **Determine Template Type**
   - Ask user what type of template to create:
     - Agent template
     - Skill template
     - Command template
     - Documentation template
   - Each type has different requirements and structure

2. **Gather Template Information**

   **For Agent Templates:**
   - Template name (e.g., `api-development-agent`)
   - Description (when to use this agent)
   - Model preference (sonnet, opus, haiku)
   - Tools needed (Read, Write, Bash, Grep, etc.)
   - Responsibilities and tasks
   - Example workflows
   - Relevant skills to reference

   **For Skill Templates:**
   - Skill name (e.g., `python-fastapi`)
   - Description (what knowledge this provides)
   - Allowed tools (if any)
   - Core concepts to cover
   - Code examples to include
   - Best practices
   - Quick reference commands

   **For Command Templates:**
   - Command name (e.g., `deploy`)
   - Description (what the command does)
   - Tasks to complete
   - Example commands
   - Expected output
   - Configuration requirements

   **For Documentation Templates:**
   - Document type (ARCHITECTURE.md, API.md, etc.)
   - Sections to include
   - Project-specific placeholders

3. **Create Template Variables**
   - Identify which parts should be templated
   - Common variables:
     - `{{ project_name }}` - Human-readable project name
     - `{{ project_slug }}` - Kebab-case project identifier
     - `{{ project_type }}` - Project type (saas-web-app, etc.)
     - `{{ tech_stack }}` - Technology choices
     - `{{ features }}` - Selected features
     - `{{ author }}` - Project author
     - `{{ year }}` - Current year
   - Custom variables based on project type

4. **Write Template File**

   **Agent Template Structure:**
   ```markdown
   ---
   name: {{ project_slug }}-{agent-type}-agent
   description: {When to use this agent with examples}
   model: {sonnet|opus|haiku}
   tools: {Tool1, Tool2, ...}
   ---

   # {Agent Name}

   ## Purpose
   {What this agent does}

   ## Responsibilities
   {List of responsibilities}

   ## Key Workflows
   {Example workflows}

   ## Best Practices
   {Guidelines}

   ## Related Skills
   {References to skills}
   ```

   **Skill Template Structure:**
   ```markdown
   ---
   name: {skill-name}
   description: {What knowledge this provides}
   allowed-tools: [{Tool1, Tool2}]
   ---

   # {Skill Name}

   ## Core Concepts
   {Fundamental knowledge}

   ## Common Patterns
   {Code examples}

   ## Best Practices
   {Guidelines}

   ## Quick Reference
   {Cheat sheet}
   ```

   **Command Template Structure:**
   ```markdown
   # {Command Name}

   {Brief description}

   ## Tasks to Complete
   {Step-by-step tasks}

   ## Example Commands
   {Shell commands}

   ## Example Output
   {Expected results}

   ## Notes
   {Additional information}
   ```

5. **Save Template to Library**
   - Save to appropriate directory:
     - Agents: `templates/agents/{template-name}.md.j2`
     - Skills: `templates/skills/{template-name}/SKILL.md.j2`
     - Commands: `templates/commands/{template-name}.md.j2`
     - Docs: `templates/docs/{template-name}.md.j2`
   - Use `.j2` extension for Jinja2 templates

6. **Create Template Configuration**
   - Create YAML config file: `templates/agents/{template-name}.yaml`
   - Include metadata:
     ```yaml
     name: api-development-agent
     category: development
     description: Agent for building RESTful APIs
     project_types:
       - saas-web-app
       - api-service
       - mobile-backend
     tech_stacks:
       - python-fastapi
       - node-express
       - go-gin
     variables:
       - project_name
       - project_slug
       - api_framework
     dependencies:
       skills:
         - python-fastapi
         - openapi-design
       agents:
         - database-agent
     ```

7. **Add Example Usage**
   - Create example in `templates/examples/{template-name}/`
   - Show rendered output with sample variables
   - Include in template library documentation

8. **Update Template Registry**
   - Add template to `templates/registry.yaml`:
     ```yaml
     agents:
       - name: api-development-agent
         file: agents/api-development-agent.md.j2
         config: agents/api-development-agent.yaml
         category: development
     ```
   - This allows the generator to discover templates

9. **Validate Template**
   - Run template validator: `claude-gen validate-template {path}`
   - Check for:
     - Valid frontmatter (for agents/skills)
     - No syntax errors in Jinja2 template
     - All variables are defined in config
     - References to other templates exist
     - Example renders correctly

10. **Test Template Integration**
    - Run test generator with new template
    - Verify template is selected for appropriate project types
    - Check rendered output is correct
    - Test variable substitution works

11. **Document Template**
    - Add to `templates/README.md`:
      - Template name and purpose
      - When to use it
      - Required variables
      - Example usage
    - Update template count in project README

## Example Interactive Flow

```
📝 Add New Template to Library

What type of template do you want to create?
  ○ Agent
  ○ Skill
  ○ Command
  ○ Documentation

> Agent

Template name (e.g., api-development-agent): security-audit-agent

Description: Agent specialized in security audits, vulnerability scanning, and penetration testing

Model preference:
  ○ sonnet (balanced)
  ○ opus (complex reasoning)
  ○ haiku (fast, simple)

> opus

Tools needed (comma-separated): Read, Write, Bash, Grep

Which project types should use this agent?
  ☑ saas-web-app
  ☑ api-service
  ☑ mobile-backend
  ☐ hardware-iot
  ☐ data-science

Related skills (comma-separated): security-testing, penetration-testing, owasp

✅ Template created: templates/agents/security-audit-agent.md.j2
✅ Configuration created: templates/agents/security-audit-agent.yaml
✅ Registry updated
✅ Template validated

Would you like to test the template? (Y/n): Y

Testing template with sample project...
✅ Template renders correctly
✅ All variables substituted
✅ Output validated

📄 Template ready to use!

Next steps:
  - Add example: templates/examples/security-audit-agent/
  - Update documentation: templates/README.md
  - Test in real project: /test-generator
```

## Template Best Practices

1. **Clear Descriptions:** Make it obvious when to use the template
2. **Meaningful Variables:** Use descriptive placeholder names
3. **Complete Examples:** Include working code samples
4. **Project Type Mapping:** Specify which project types need this template
5. **Dependencies:** Document required skills/agents/tools
6. **Validation:** Test templates before committing
7. **Versioning:** Track template changes for compatibility
8. **Documentation:** Explain template purpose and usage

## Notes

- Templates use Jinja2 syntax: `{{ variable }}`, `{% if %}`, `{% for %}`
- Keep templates focused on one concern (single responsibility)
- Reuse existing templates when possible (DRY principle)
- Include error handling in command templates
- Provide sensible defaults for optional variables
- Test templates with various project types
- Version templates if making breaking changes
- Consider template inheritance for related templates
