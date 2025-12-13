"""
Analyze selection coverage - what gets selected for each project type.
"""

from pathlib import Path

from src.generator.selector import TemplateSelector
from src.generator.analyzer import ProjectConfig


def analyze_project_type(selector, project_type, config):
    """Analyze what gets selected for a specific project type."""
    print(f"\n{'='*80}")
    print(f"PROJECT TYPE: {project_type.upper()}")
    print(f"{'='*80}")

    selected = selector.select_templates(config)

    print(f"\n[Configuration]")
    print(f"  - Backend: {config.backend_framework or 'None'}")
    print(f"  - Frontend: {config.frontend_framework or 'None'}")
    print(f"  - Database: {config.database or 'None'}")
    print(f"  - Platform: {config.platform or 'None'}")
    print(f"  - Features: {', '.join(config.features) if config.features else 'None'}")

    print(f"\n[Selected Agents] ({len(selected['agents'])}):")
    for i, agent_path in enumerate(selected['agents'], 1):
        agent_name = Path(agent_path).stem
        print(f"  {i}. {agent_name}")

    print(f"\n[Selected Skills] ({len(selected['skills'])}):")
    for i, skill_path in enumerate(selected['skills'], 1):
        skill_name = Path(skill_path).parent.name
        print(f"  {i}. {skill_name}")

    return {
        'agents': len(selected['agents']),
        'skills': len(selected['skills']),
        'agent_names': [Path(p).stem for p in selected['agents']],
        'skill_names': [Path(p).parent.name for p in selected['skills']]
    }


def main():
    """Run coverage analysis for all project types."""
    templates_dir = Path(__file__).parent.parent.parent / 'templates'
    selector = TemplateSelector(templates_dir)

    print("="*80)
    print("SELECTION COVERAGE ANALYSIS")
    print("="*80)
    print("\nAnalyzing what agents and skills get selected for each project type")
    print("with various tech stack combinations...\n")

    results = {}

    # 1. SaaS Web App - React + FastAPI
    print("\n" + "="*80)
    print("SCENARIO 1: SaaS Web App - React + FastAPI + PostgreSQL")
    config = ProjectConfig(
        project_name='saas-react-fastapi',
        project_slug='saas-react-fastapi',
        project_type='saas-web-app',
        description='SaaS web application with React and FastAPI',
        backend_framework='python-fastapi',
        frontend_framework='react-typescript',
        database='postgresql',
        deployment_platform='docker',
        features=['authentication']
    )
    results['saas-react-fastapi'] = analyze_project_type(selector, 'saas-react-fastapi', config)

    # 2. SaaS Web App - Vue + Django
    print("\n" + "="*80)
    print("SCENARIO 2: SaaS Web App - Vue + Django + PostgreSQL")
    config = ProjectConfig(
        project_name='saas-vue-django',
        project_slug='saas-vue-django',
        project_type='saas-web-app',
        description='SaaS web application with Vue and Django',
        backend_framework='django',
        frontend_framework='vue-typescript',
        database='postgresql',
        deployment_platform='docker',
        features=[]
    )
    results['saas-vue-django'] = analyze_project_type(selector, 'saas-vue-django', config)

    # 3. API Service - FastAPI
    print("\n" + "="*80)
    print("SCENARIO 3: API Service - FastAPI + PostgreSQL")
    config = ProjectConfig(
        project_name='api-fastapi',
        project_slug='api-fastapi',
        project_type='api-service',
        description='REST API service with FastAPI',
        backend_framework='python-fastapi',
        database='postgresql',
        deployment_platform='docker',
        features=['authentication']
    )
    results['api-fastapi'] = analyze_project_type(selector, 'api-fastapi', config)

    # 4. API Service - Express
    print("\n" + "="*80)
    print("SCENARIO 4: API Service - Node Express + PostgreSQL")
    config = ProjectConfig(
        project_name='api-express',
        project_slug='api-express',
        project_type='api-service',
        description='REST API service with Express',
        backend_framework='node-express',
        database='postgresql',
        deployment_platform='docker',
        features=[]
    )
    results['api-express'] = analyze_project_type(selector, 'api-express', config)

    # 5. Mobile App - React Native
    print("\n" + "="*80)
    print("SCENARIO 5: Mobile App - React Native + FastAPI")
    config = ProjectConfig(
        project_name='mobile-react-native',
        project_slug='mobile-react-native',
        project_type='mobile-app',
        description='Mobile app with React Native',
        frontend_framework='react-native',
        backend_framework='python-fastapi',
        database='postgresql',
        features=['authentication']
    )
    results['mobile-react-native'] = analyze_project_type(selector, 'mobile-react-native', config)

    # 6. Hardware IoT - Pico W
    print("\n" + "="*80)
    print("SCENARIO 6: Hardware IoT - Raspberry Pi Pico W")
    config = ProjectConfig(
        project_name='iot-pico',
        project_slug='iot-pico',
        project_type='hardware-iot',
        description='IoT device with Raspberry Pi Pico W',
        platform='pico-w',
        firmware_language='micropython',
        connectivity='mqtt',
        features=[]
    )
    results['iot-pico'] = analyze_project_type(selector, 'iot-pico', config)

    # 7. Data Science - Python
    print("\n" + "="*80)
    print("SCENARIO 7: Data Science - Python + FastAPI")
    config = ProjectConfig(
        project_name='ml-project',
        project_slug='ml-project',
        project_type='data-science',
        description='Machine learning project with Python',
        backend_framework='python-fastapi',
        database='postgresql',
        features=[]
    )
    results['ml-project'] = analyze_project_type(selector, 'ml-project', config)

    # Summary
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)

    print("\n[Resources Selected Per Scenario]")
    print(f"{'Scenario':<30} {'Agents':<10} {'Skills':<10} {'Total':<10}")
    print("-" * 60)
    for scenario, data in results.items():
        total = data['agents'] + data['skills']
        print(f"{scenario:<30} {data['agents']:<10} {data['skills']:<10} {total:<10}")

    print(f"\n[Overall Statistics]")
    total_agents = sum(r['agents'] for r in results.values())
    total_skills = sum(r['skills'] for r in results.values())
    avg_agents = total_agents / len(results)
    avg_skills = total_skills / len(results)

    print(f"  - Average agents per scenario: {avg_agents:.1f}")
    print(f"  - Average skills per scenario: {avg_skills:.1f}")
    print(f"  - Total selections: {total_agents + total_skills}")

    # Resource usage
    print(f"\n[Resource Usage]")
    all_agent_names = set()
    all_skill_names = set()
    for data in results.values():
        all_agent_names.update(data['agent_names'])
        all_skill_names.update(data['skill_names'])

    registry = selector.registry
    total_agents_in_registry = len(registry.get('agents', []))
    total_skills_in_registry = len(registry.get('skills', []))

    print(f"  - Agents used: {len(all_agent_names)}/{total_agents_in_registry}")
    print(f"  - Skills used: {len(all_skill_names)}/{total_skills_in_registry}")

    unused_agents = set(a['name'] for a in registry.get('agents', [])) - all_agent_names
    unused_skills = set(s['name'] for s in registry.get('skills', [])) - all_skill_names

    if unused_agents:
        print(f"\n  [WARNING] Unused agents in these scenarios: {', '.join(sorted(unused_agents))}")
    if unused_skills:
        print(f"  [WARNING] Unused skills in these scenarios: {', '.join(sorted(unused_skills))}")

    print("\n" + "="*80)
    print("[SUCCESS] Analysis Complete!")
    print("="*80)


if __name__ == '__main__':
    main()
