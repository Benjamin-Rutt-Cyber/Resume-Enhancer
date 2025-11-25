# Test Generator

Test the Claude Code Generator on sample project descriptions to verify it works correctly.

## Tasks to Complete

1. **Prepare Test Environment**
   - Create temporary test directory: `tests/output/`
   - Clear any previous test output
   - Verify generator is installed: `claude-gen --version`

2. **Test Case 1: SaaS Web App**
   - Project description: "Build a SaaS platform for project management with team collaboration"
   - Expected output:
     - `.claude/agents/` with api-development-agent, frontend-agent, database-agent
     - `.claude/skills/` with python-fastapi, react-typescript, postgresql
     - `.claude/commands/` with setup-dev, run-server, db-migrate
     - Documentation: ARCHITECTURE.md, API.md, SETUP.md
     - README.md with project overview
   - Verify all files are created correctly
   - Check template variable substitution worked

3. **Test Case 2: API Service**
   - Project description: "Create a REST API for weather data aggregation"
   - Expected output:
     - `.claude/agents/` with api-development-agent, testing-agent
     - `.claude/skills/` with python-fastapi, openapi-design, testing
     - `.claude/commands/` with setup-dev, run-server, test-api
     - Documentation: API.md, ARCHITECTURE.md
   - Verify API-specific templates are used

4. **Test Case 3: Hardware IoT**
   - Project description: "Build an IoT temperature monitoring system with Raspberry Pi Pico W"
   - Expected output:
     - `.claude/agents/` with embedded-agent, iot-agent, hardware-agent
     - `.claude/skills/` with micropython, mqtt, hardware-design
     - `.claude/commands/` with flash-firmware, test-hardware, monitor-sensors
     - Documentation: HARDWARE.md, FIRMWARE.md, SETUP.md
   - Verify hardware-specific templates are used

5. **Test Case 4: Mobile App**
   - Project description: "Create a mobile fitness tracking app for iOS and Android"
   - Expected output:
     - `.claude/agents/` with mobile-agent, backend-agent, ui-ux-agent
     - `.claude/skills/` with react-native, mobile-ui, backend-api
     - `.claude/commands/` with run-ios, run-android, build-release
     - Documentation: MOBILE.md, API.md, DESIGN.md
   - Verify mobile-specific templates are used

6. **Test Case 5: Data Science**
   - Project description: "Build a machine learning model for stock price prediction"
   - Expected output:
     - `.claude/agents/` with data-science-agent, ml-agent, visualization-agent
     - `.claude/skills/` with pandas-numpy, scikit-learn, data-visualization
     - `.claude/commands/` with train-model, evaluate, visualize
     - Documentation: MODEL.md, DATA.md, EXPERIMENTS.md
   - Verify data science templates are used

7. **Validation Checks**
   For each generated project, verify:
   - All required directories exist
   - All agent files have valid frontmatter (name, description, model, tools)
   - All skill SKILL.md files exist and have frontmatter
   - All command files are valid markdown
   - No template variables left unsubstituted (e.g., `{{ project_name }}`)
   - README.md contains project-specific information
   - File permissions are correct (especially on Unix)

8. **Interactive Mode Test**
   - Run generator in interactive mode: `claude-gen init`
   - Verify prompts appear correctly:
     - Project name input
     - Project type selection (saas-web-app, api-service, etc.)
     - Tech stack selection
     - Feature selection
   - Verify answers are processed correctly
   - Verify output matches selections

9. **Error Handling Tests**
   - Test with empty project description
   - Test with invalid project type
   - Test with existing directory (should ask to overwrite)
   - Test with invalid characters in project name
   - Test without ANTHROPIC_API_KEY (should gracefully fallback)

10. **Performance Test**
    - Measure generation time for each test case
    - Should complete within 10 seconds per project
    - Display timing information

11. **Generate Test Report**
    - Create markdown report: `tests/output/TEST_REPORT.md`
    - Include:
      - Test results (pass/fail for each test case)
      - Generated file counts
      - Timing information
      - Screenshots or file tree outputs
      - Any errors or warnings

## Example Commands

```bash
# Test with sample descriptions
claude-gen init \
  --project "My SaaS App" \
  --description "Build a SaaS platform for project management" \
  --type saas-web-app \
  --output tests/output/saas-test

# Interactive mode test
claude-gen init --output tests/output/interactive-test

# Validate generated project
claude-gen validate tests/output/saas-test
```

## Example Output

```
🧪 Testing Claude Code Generator

Test Case 1: SaaS Web App
  ✅ Generated .claude/agents/ (5 agents)
  ✅ Generated .claude/skills/ (7 skills)
  ✅ Generated .claude/commands/ (6 commands)
  ✅ Generated documentation (4 files)
  ✅ README.md created
  ✅ All variables substituted correctly
  ⏱️  Completed in 3.2s

Test Case 2: API Service
  ✅ Generated .claude/agents/ (3 agents)
  ✅ Generated .claude/skills/ (5 skills)
  ✅ Generated .claude/commands/ (4 commands)
  ✅ Generated documentation (3 files)
  ✅ README.md created
  ✅ All variables substituted correctly
  ⏱️  Completed in 2.8s

Test Case 3: Hardware IoT
  ✅ Generated .claude/agents/ (4 agents)
  ✅ Generated .claude/skills/ (6 skills)
  ✅ Generated .claude/commands/ (5 commands)
  ✅ Generated documentation (4 files)
  ✅ README.md created
  ✅ All variables substituted correctly
  ⏱️  Completed in 3.5s

================================
📊 Test Summary
================================
Total Test Cases: 5
Passed: 5
Failed: 0
Average Time: 3.1s
Total Files Generated: 127

✅ All tests passed!

📄 Full report: tests/output/TEST_REPORT.md
```

## Notes

- Run this command frequently during development to catch regressions
- Keep test cases updated as new templates are added
- Use this to demo the generator to potential users
- Test output directory should be in .gitignore
- Consider automating this as part of CI/CD pipeline
