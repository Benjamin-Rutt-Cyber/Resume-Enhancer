"""Generate all test projects for validation."""
import sys
from pathlib import Path
sys.path.insert(0, 'src')

from generator.file_generator import FileGenerator
from generator.analyzer import ProjectConfig

templates_dir = Path('templates')
generator = FileGenerator(templates_dir, api_key=None)

# Test configurations for all 5 project types
test_configs = [
    {
        'name': 'Test SaaS App',
        'slug': 'test-saas',
        'type': 'saas-web-app',
        'desc': 'A comprehensive SaaS web application with FastAPI and React',
        'backend': 'python-fastapi',
        'frontend': 'react-typescript',
        'database': 'postgresql',
        'output': 'test-output/test-saas'
    },
    {
        'name': 'Test API Service',
        'slug': 'test-api',
        'type': 'api-service',
        'desc': 'A REST API service with FastAPI and PostgreSQL',
        'backend': 'python-fastapi',
        'frontend': None,
        'database': 'postgresql',
        'output': 'test-output/test-api'
    },
    {
        'name': 'Test Mobile App',
        'slug': 'test-mobile',
        'type': 'mobile-app',
        'desc': 'A mobile application with React Native and FastAPI backend',
        'backend': 'python-fastapi',
        'frontend': 'react-native',
        'database': 'postgresql',
        'output': 'test-output/test-mobile'
    },
    {
        'name': 'Test IoT Device',
        'slug': 'test-iot',
        'type': 'hardware-iot',
        'desc': 'An IoT device with Raspberry Pi Pico W and MicroPython',
        'backend': None,
        'frontend': None,
        'database': None,
        'output': 'test-output/test-iot'
    },
    {
        'name': 'Test ML Project',
        'slug': 'test-ml',
        'type': 'data-science',
        'desc': 'A machine learning project with Python and FastAPI',
        'backend': 'python-fastapi',
        'frontend': None,
        'database': 'postgresql',
        'output': 'test-output/test-ml'
    }
]

print("=" * 80)
print("GENERATING TEST PROJECTS")
print("=" * 80)

for config_data in test_configs:
    print(f"\n[{config_data['name']}]")
    print(f"Type: {config_data['type']}")
    print(f"Output: {config_data['output']}")

    # Create ProjectConfig
    config = ProjectConfig(
        project_name=config_data['name'],
        project_slug=config_data['slug'],
        project_type=config_data['type'],
        description=config_data['desc'],
        backend_framework=config_data['backend'],
        frontend_framework=config_data['frontend'],
        database=config_data['database'],
        features=['authentication'] if config_data['type'] != 'hardware-iot' else []
    )

    # Generate project
    try:
        output_dir = Path(config_data['output'])

        # Remove old output if exists
        if output_dir.exists():
            import shutil
            shutil.rmtree(output_dir)

        generator.generate_project(config, output_dir)

        # Validate structure
        agents_dir = output_dir / '.claude' / 'agents'
        skills_dir = output_dir / '.claude' / 'skills'
        readme = output_dir / 'README.md'
        plugins = output_dir / '.claude' / 'plugins.yaml'

        agent_count = len(list(agents_dir.glob('*.md'))) if agents_dir.exists() else 0
        skill_count = len(list(skills_dir.glob('**/SKILL.md'))) if skills_dir.exists() else 0

        print(f"  Agents: {agent_count}")
        print(f"  Skills: {skill_count}")
        print(f"  README: {'EXISTS' if readme.exists() else 'MISSING'}")
        print(f"  Plugins: {'EXISTS' if plugins.exists() else 'MISSING'}")

        # Check README content
        if readme.exists():
            content = readme.read_text()
            if config_data['type'] == 'saas-web-app' and 'SaaS Web Application' in content:
                print(f"  README Type: CORRECT (library template)")
            elif config_data['type'] == 'api-service' and 'REST API Service' in content:
                print(f"  README Type: CORRECT (library template)")
            elif config_data['type'] == 'mobile-app' and 'Mobile Application' in content:
                print(f"  README Type: CORRECT (library template)")
            elif config_data['type'] == 'hardware-iot' and 'Hardware/IoT Project' in content:
                print(f"  README Type: CORRECT (library template)")
            elif config_data['type'] == 'data-science' and 'Data Science' in content:
                print(f"  README Type: CORRECT (library template)")
            else:
                print(f"  README Type: WARNING - May be basic template")

        print(f"  Status: SUCCESS")

    except Exception as e:
        print(f"  Status: FAILED - {str(e)}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)
print("GENERATION COMPLETE")
print("=" * 80)
