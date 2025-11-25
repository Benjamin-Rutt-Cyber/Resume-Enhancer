#!/usr/bin/env python
"""Test script to validate new templates"""

from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, 'src')

from generator.file_generator import FileGenerator
from generator.analyzer import ProjectConfig


def test_saas_web_app():
    """Test SaaS Web App generation with new templates"""
    templates_dir = Path('templates')
    generator = FileGenerator(templates_dir, api_key=None)

    config = ProjectConfig(
        project_name='Test Validation',
        project_slug='test-validation',
        project_type='saas-web-app',
        description='Testing new templates',
        backend_framework='python-fastapi',
        frontend_framework='react-typescript',
        database='postgresql',
        features=['authentication']
    )

    output_dir = Path('test-output/test-validation')

    try:
        result = generator.generate_project(config, output_dir, overwrite=True)

        # Check what was generated
        commands = list((output_dir / '.claude' / 'commands').glob('*.md'))
        docs = list((output_dir / 'docs').glob('*.md')) if (output_dir / 'docs').exists() else []

        print('[OK] SUCCESS - SaaS Web App')
        print(f'Commands generated: {len(commands)}')
        for cmd in sorted(commands):
            print(f'  - {cmd.name}')

        print(f'\nDocs generated: {len(docs)}')
        for doc in sorted(docs):
            print(f'  - {doc.name}')

        return True

    except Exception as e:
        print(f'[ERROR] {e}')
        import traceback
        traceback.print_exc()
        return False


def test_hardware_iot():
    """Test Hardware IoT generation with new templates"""
    templates_dir = Path('templates')
    generator = FileGenerator(templates_dir, api_key=None)

    config = ProjectConfig(
        project_name='IoT Test',
        project_slug='iot-test',
        project_type='hardware-iot',
        description='Testing IoT templates',
        platform='pico-w',
        language='micropython',
        connectivity='mqtt',
        cloud='custom-backend',
        features=['sensors', 'wifi', 'ota_updates']
    )

    output_dir = Path('test-output/iot-test')

    try:
        result = generator.generate_project(config, output_dir, overwrite=True)

        # Check what was generated
        commands = list((output_dir / '.claude' / 'commands').glob('*.md'))
        docs = list((output_dir / 'docs').glob('*.md')) if (output_dir / 'docs').exists() else []

        print('\n[OK] SUCCESS - Hardware IoT')
        print(f'Commands generated: {len(commands)}')
        for cmd in sorted(commands):
            print(f'  - {cmd.name}')

        print(f'\nDocs generated: {len(docs)}')
        for doc in sorted(docs):
            print(f'  - {doc.name}')

        return True

    except Exception as e:
        print(f'[ERROR] {e}')
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print('Testing new templates...\n')
    print('=' * 60)

    results = []
    results.append(test_saas_web_app())
    results.append(test_hardware_iot())

    print('\n' + '=' * 60)
    print(f'\nResults: {sum(results)}/{len(results)} tests passed')

    if all(results):
        print('[SUCCESS] All template tests passed!')
        sys.exit(0)
    else:
        print('[WARNING] Some tests failed')
        sys.exit(1)
