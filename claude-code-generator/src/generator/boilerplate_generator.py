"""
Boilerplate Code Generator

Generates starter code for different tech stacks based on project configuration.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

from jinja2 import TemplateError, TemplateNotFound, TemplateSyntaxError, UndefinedError

from .constants import DEFAULT_API_PORT, DEFAULT_FRONTEND_PORT
from .renderer import TemplateRenderer
from .analyzer import ProjectConfig

logger = logging.getLogger(__name__)


class BoilerplateGenerator:
    """Generates boilerplate code for projects."""

    def __init__(self, templates_dir: Path):
        """
        Initialize the boilerplate generator.

        Args:
            templates_dir: Path to templates directory
        """
        self.templates_dir = templates_dir
        self.boilerplate_dir = templates_dir / "boilerplate"
        self.renderer = TemplateRenderer(templates_dir)

    def generate_boilerplate(
        self, config: ProjectConfig, output_dir: Path
    ) -> Dict[str, List[Path]]:
        """
        Generate all boilerplate code for the project.

        Args:
            config: Project configuration
            output_dir: Directory to write generated code

        Returns:
            Dictionary mapping category to list of generated files
        """
        generated_files: Dict[str, List[Path]] = {
            "backend": [],
            "frontend": [],
            "config": [],
            "docs": [],
        }

        # Generate backend boilerplate
        if config.backend_framework:
            backend_files = self._generate_backend(config, output_dir)
            generated_files["backend"].extend(backend_files)

        # Generate frontend boilerplate
        if config.frontend_framework:
            frontend_files = self._generate_frontend(config, output_dir)
            generated_files["frontend"].extend(frontend_files)

        # Generate configuration files
        config_files = self._generate_config_files(config, output_dir)
        generated_files["config"].extend(config_files)

        return generated_files

    def _generate_backend(self, config: ProjectConfig, output_dir: Path) -> List[Path]:
        """Generate backend boilerplate code."""
        generated_files = []

        backend = config.backend_framework.lower()

        if backend in ["python-fastapi", "fastapi"]:
            generated_files.extend(self._generate_fastapi(config, output_dir))
        elif backend in ["node-express", "express"]:
            generated_files.extend(self._generate_express(config, output_dir))
        elif backend == "django":
            generated_files.extend(self._generate_django(config, output_dir))
        else:
            logger.warning(f"No boilerplate template for backend: {backend}")

        return generated_files

    def _generate_frontend(self, config: ProjectConfig, output_dir: Path) -> List[Path]:
        """Generate frontend boilerplate code."""
        generated_files = []

        frontend = config.frontend_framework.lower()

        if frontend in ["react", "react-typescript"]:
            generated_files.extend(self._generate_react(config, output_dir))
        elif frontend in ["nextjs", "next-js", "next.js"]:
            generated_files.extend(self._generate_nextjs(config, output_dir))
        elif frontend in ["vue", "vue-typescript"]:
            generated_files.extend(self._generate_vue(config, output_dir))
        elif frontend in ["nuxt", "nuxtjs", "nuxt3"]:
            generated_files.extend(self._generate_nuxt(config, output_dir))
        elif frontend in ["svelte", "sveltekit"]:
            generated_files.extend(self._generate_svelte(config, output_dir))
        elif frontend == "angular":
            generated_files.extend(self._generate_angular(config, output_dir))
        else:
            logger.warning(f"No boilerplate template for frontend: {frontend}")

        return generated_files

    def _generate_config_files(
        self, config: ProjectConfig, output_dir: Path
    ) -> List[Path]:
        """Generate configuration files (docker-compose, .env, etc.)."""
        generated_files = []

        # docker-compose.yml - generate for backend projects
        if config.backend_framework:
            docker_compose = self._render_template(
                "config/docker-compose.yml.j2", config, output_dir / "docker-compose.yml"
            )
            if docker_compose:
                generated_files.append(docker_compose)

        # Dockerfile for backend
        if config.backend_framework:
            dockerfile = self._render_template(
                f"config/Dockerfile-{config.backend_framework}.j2",
                config,
                output_dir / "Dockerfile",
            )
            if dockerfile:
                generated_files.append(dockerfile)

        # .env.example
        env_example = self._render_template(
            "config/.env.example.j2", config, output_dir / ".env.example"
        )
        if env_example:
            generated_files.append(env_example)

        # .gitignore
        gitignore = self._render_template(
            "config/.gitignore.j2", config, output_dir / ".gitignore"
        )
        if gitignore:
            generated_files.append(gitignore)

        # package.json or requirements.txt
        if config.frontend_framework:
            package_json = self._render_template(
                "config/package.json.j2", config, output_dir / "frontend" / "package.json"
            )
            if package_json:
                generated_files.append(package_json)

        if config.backend_framework and "python" in config.backend_framework.lower():
            requirements = self._render_template(
                "config/requirements.txt.j2",
                config,
                output_dir / "backend" / "requirements.txt",
            )
            if requirements:
                generated_files.append(requirements)

        return generated_files

    def _generate_fastapi(self, config: ProjectConfig, output_dir: Path) -> List[Path]:
        """Generate FastAPI project structure."""
        generated_files = []
        backend_dir = output_dir / "backend"

        templates = [
            ("python-fastapi/main.py.j2", backend_dir / "main.py"),
            ("python-fastapi/app/__init__.py.j2", backend_dir / "app" / "__init__.py"),
            (
                "python-fastapi/app/core/config.py.j2",
                backend_dir / "app" / "core" / "config.py",
            ),
            (
                "python-fastapi/app/core/__init__.py.j2",
                backend_dir / "app" / "core" / "__init__.py",
            ),
            (
                "python-fastapi/app/api/__init__.py.j2",
                backend_dir / "app" / "api" / "__init__.py",
            ),
            (
                "python-fastapi/app/api/routes/__init__.py.j2",
                backend_dir / "app" / "api" / "routes" / "__init__.py",
            ),
            (
                "python-fastapi/app/api/routes/health.py.j2",
                backend_dir / "app" / "api" / "routes" / "health.py",
            ),
            (
                "python-fastapi/app/models/__init__.py.j2",
                backend_dir / "app" / "models" / "__init__.py",
            ),
            (
                "python-fastapi/app/schemas/__init__.py.j2",
                backend_dir / "app" / "schemas" / "__init__.py",
            ),
        ]

        for template_path, output_path in templates:
            rendered = self._render_template(template_path, config, output_path)
            if rendered:
                generated_files.append(rendered)

        return generated_files

    def _generate_nextjs(self, config: ProjectConfig, output_dir: Path) -> List[Path]:
        """Generate Next.js project structure."""
        generated_files = []
        frontend_dir = output_dir / "frontend"

        templates = [
            ("nextjs/package.json.j2", frontend_dir / "package.json"),
            ("nextjs/tsconfig.json.j2", frontend_dir / "tsconfig.json"),
            ("nextjs/next.config.js.j2", frontend_dir / "next.config.js"),
            ("nextjs/.eslintrc.json.j2", frontend_dir / ".eslintrc.json"),
            ("nextjs/src/app/layout.tsx.j2", frontend_dir / "src" / "app" / "layout.tsx"),
            ("nextjs/src/app/page.tsx.j2", frontend_dir / "src" / "app" / "page.tsx"),
            (
                "nextjs/src/app/globals.css.j2",
                frontend_dir / "src" / "app" / "globals.css",
            ),
            (
                "nextjs/src/app/api/health/route.ts.j2",
                frontend_dir / "src" / "app" / "api" / "health" / "route.ts",
            ),
            (
                "nextjs/src/components/Header.tsx.j2",
                frontend_dir / "src" / "components" / "Header.tsx",
            ),
            ("nextjs/src/lib/utils.ts.j2", frontend_dir / "src" / "lib" / "utils.ts"),
            ("nextjs/public/.gitkeep.j2", frontend_dir / "public" / ".gitkeep"),
        ]

        for template_path, output_path in templates:
            rendered = self._render_template(template_path, config, output_path)
            if rendered:
                generated_files.append(rendered)

        return generated_files

    def _generate_react(self, config: ProjectConfig, output_dir: Path) -> List[Path]:
        """Generate React project structure."""
        generated_files = []
        frontend_dir = output_dir / "frontend"

        templates = [
            ("react/package.json.j2", frontend_dir / "package.json"),
            ("react/tsconfig.json.j2", frontend_dir / "tsconfig.json"),
            ("react/vite.config.ts.j2", frontend_dir / "vite.config.ts"),
            ("react/index.html.j2", frontend_dir / "index.html"),
            ("react/src/main.tsx.j2", frontend_dir / "src" / "main.tsx"),
            ("react/src/App.tsx.j2", frontend_dir / "src" / "App.tsx"),
            ("react/src/App.css.j2", frontend_dir / "src" / "App.css"),
            ("react/src/index.css.j2", frontend_dir / "src" / "index.css"),
            (
                "react/src/components/Header.tsx.j2",
                frontend_dir / "src" / "components" / "Header.tsx",
            ),
            ("react/src/lib/api.ts.j2", frontend_dir / "src" / "lib" / "api.ts"),
            ("react/public/vite.svg.j2", frontend_dir / "public" / "vite.svg"),
        ]

        for template_path, output_path in templates:
            rendered = self._render_template(template_path, config, output_path)
            if rendered:
                generated_files.append(rendered)

        return generated_files

    def _generate_vue(self, config: ProjectConfig, output_dir: Path) -> List[Path]:
        """Generate Vue.js project structure."""
        generated_files = []
        frontend_dir = output_dir / "frontend"

        templates = [
            ("vue/package.json.j2", frontend_dir / "package.json"),
            ("vue/vite.config.ts.j2", frontend_dir / "vite.config.ts"),
            ("vue/tsconfig.json.j2", frontend_dir / "tsconfig.json"),
            ("vue/tsconfig.node.json.j2", frontend_dir / "tsconfig.node.json"),
            ("vue/index.html.j2", frontend_dir / "index.html"),
            ("vue/src/main.ts.j2", frontend_dir / "src" / "main.ts"),
            ("vue/src/App.vue.j2", frontend_dir / "src" / "App.vue"),
            ("vue/src/router/index.ts.j2", frontend_dir / "src" / "router" / "index.ts"),
            ("vue/src/stores/counter.ts.j2", frontend_dir / "src" / "stores" / "counter.ts"),
            ("vue/src/components/Header.vue.j2", frontend_dir / "src" / "components" / "Header.vue"),
            ("vue/src/components/HelloWorld.vue.j2", frontend_dir / "src" / "components" / "HelloWorld.vue"),
            ("vue/src/views/HomeView.vue.j2", frontend_dir / "src" / "views" / "HomeView.vue"),
            ("vue/src/views/AboutView.vue.j2", frontend_dir / "src" / "views" / "AboutView.vue"),
            ("vue/src/assets/main.css.j2", frontend_dir / "src" / "assets" / "main.css"),
            ("vue/src/assets/base.css.j2", frontend_dir / "src" / "assets" / "base.css"),
            ("vue/public/.gitkeep.j2", frontend_dir / "public" / ".gitkeep"),
        ]

        for template_path, output_path in templates:
            rendered = self._render_template(template_path, config, output_path)
            if rendered:
                generated_files.append(rendered)

        return generated_files

    def _generate_nuxt(self, config: ProjectConfig, output_dir: Path) -> List[Path]:
        """Generate Nuxt.js project structure."""
        generated_files = []
        frontend_dir = output_dir / "frontend"

        templates = [
            ("nuxt/package.json.j2", frontend_dir / "package.json"),
            ("nuxt/nuxt.config.ts.j2", frontend_dir / "nuxt.config.ts"),
            ("nuxt/tsconfig.json.j2", frontend_dir / "tsconfig.json"),
            ("nuxt/app.vue.j2", frontend_dir / "app.vue"),
            ("nuxt/layouts/default.vue.j2", frontend_dir / "layouts" / "default.vue"),
            ("nuxt/components/Header.vue.j2", frontend_dir / "components" / "Header.vue"),
            ("nuxt/pages/index.vue.j2", frontend_dir / "pages" / "index.vue"),
            ("nuxt/pages/about.vue.j2", frontend_dir / "pages" / "about.vue"),
            ("nuxt/composables/useApi.ts.j2", frontend_dir / "composables" / "useApi.ts"),
            ("nuxt/.env.example.j2", frontend_dir / ".env.example"),
            ("nuxt/public/.gitkeep.j2", frontend_dir / "public" / ".gitkeep"),
        ]

        for template_path, output_path in templates:
            rendered = self._render_template(template_path, config, output_path)
            if rendered:
                generated_files.append(rendered)

        return generated_files

    def _generate_svelte(self, config: ProjectConfig, output_dir: Path) -> List[Path]:
        """Generate Svelte/SvelteKit project structure."""
        generated_files = []
        frontend_dir = output_dir / "frontend"

        templates = [
            ("svelte/package.json.j2", frontend_dir / "package.json"),
            ("svelte/svelte.config.js.j2", frontend_dir / "svelte.config.js"),
            ("svelte/vite.config.ts.j2", frontend_dir / "vite.config.ts"),
            ("svelte/tsconfig.json.j2", frontend_dir / "tsconfig.json"),
            ("svelte/src/app.html.j2", frontend_dir / "src" / "app.html"),
            ("svelte/src/app.css.j2", frontend_dir / "src" / "app.css"),
            ("svelte/src/routes/+layout.svelte.j2", frontend_dir / "src" / "routes" / "+layout.svelte"),
            ("svelte/src/routes/+page.svelte.j2", frontend_dir / "src" / "routes" / "+page.svelte"),
            ("svelte/src/routes/about/+page.svelte.j2", frontend_dir / "src" / "routes" / "about" / "+page.svelte"),
            ("svelte/src/lib/components/Header.svelte.j2", frontend_dir / "src" / "lib" / "components" / "Header.svelte"),
            ("svelte/.env.example.j2", frontend_dir / ".env.example"),
            ("svelte/static/.gitkeep.j2", frontend_dir / "static" / ".gitkeep"),
        ]

        for template_path, output_path in templates:
            rendered = self._render_template(template_path, config, output_path)
            if rendered:
                generated_files.append(rendered)

        return generated_files

    def _generate_angular(self, config: ProjectConfig, output_dir: Path) -> List[Path]:
        """Generate Angular project structure."""
        generated_files = []
        frontend_dir = output_dir / "frontend"

        templates = [
            ("angular/package.json.j2", frontend_dir / "package.json"),
            ("angular/angular.json.j2", frontend_dir / "angular.json"),
            ("angular/tsconfig.json.j2", frontend_dir / "tsconfig.json"),
            ("angular/tsconfig.app.json.j2", frontend_dir / "tsconfig.app.json"),
            ("angular/tsconfig.spec.json.j2", frontend_dir / "tsconfig.spec.json"),
            ("angular/proxy.conf.json.j2", frontend_dir / "proxy.conf.json"),
            ("angular/src/index.html.j2", frontend_dir / "src" / "index.html"),
            ("angular/src/main.ts.j2", frontend_dir / "src" / "main.ts"),
            ("angular/src/styles.css.j2", frontend_dir / "src" / "styles.css"),
            ("angular/src/app/app.component.ts.j2", frontend_dir / "src" / "app" / "app.component.ts"),
            ("angular/src/app/app.component.html.j2", frontend_dir / "src" / "app" / "app.component.html"),
            ("angular/src/app/app.component.css.j2", frontend_dir / "src" / "app" / "app.component.css"),
            ("angular/src/app/app.config.ts.j2", frontend_dir / "src" / "app" / "app.config.ts"),
            ("angular/src/app/app.routes.ts.j2", frontend_dir / "src" / "app" / "app.routes.ts"),
            ("angular/src/app/components/header/header.component.ts.j2", frontend_dir / "src" / "app" / "components" / "header" / "header.component.ts"),
            ("angular/src/app/pages/home/home.component.ts.j2", frontend_dir / "src" / "app" / "pages" / "home" / "home.component.ts"),
            ("angular/src/app/pages/about/about.component.ts.j2", frontend_dir / "src" / "app" / "pages" / "about" / "about.component.ts"),
            ("angular/src/environments/environment.ts.j2", frontend_dir / "src" / "environments" / "environment.ts"),
            ("angular/.env.example.j2", frontend_dir / ".env.example"),
        ]

        for template_path, output_path in templates:
            rendered = self._render_template(template_path, config, output_path)
            if rendered:
                generated_files.append(rendered)

        return generated_files

    def _generate_express(self, config: ProjectConfig, output_dir: Path) -> List[Path]:
        """Generate Express.js project structure."""
        generated_files = []
        backend_dir = output_dir / "backend"

        templates = [
            ("express/package.json.j2", backend_dir / "package.json"),
            ("express/tsconfig.json.j2", backend_dir / "tsconfig.json"),
            ("express/.eslintrc.json.j2", backend_dir / ".eslintrc.json"),
            ("express/src/index.ts.j2", backend_dir / "src" / "index.ts"),
            ("express/src/config/index.ts.j2", backend_dir / "src" / "config" / "index.ts"),
            ("express/src/routes/index.ts.j2", backend_dir / "src" / "routes" / "index.ts"),
            ("express/src/routes/health.ts.j2", backend_dir / "src" / "routes" / "health.ts"),
            (
                "express/src/controllers/healthController.ts.j2",
                backend_dir / "src" / "controllers" / "healthController.ts",
            ),
            (
                "express/src/middleware/errorHandler.ts.j2",
                backend_dir / "src" / "middleware" / "errorHandler.ts",
            ),
            (
                "express/src/middleware/logger.ts.j2",
                backend_dir / "src" / "middleware" / "logger.ts",
            ),
            ("express/src/utils/logger.ts.j2", backend_dir / "src" / "utils" / "logger.ts"),
            ("express/src/models/.gitkeep.j2", backend_dir / "src" / "models" / ".gitkeep"),
            ("express/.env.example.j2", backend_dir / ".env.example"),
        ]

        for template_path, output_path in templates:
            rendered = self._render_template(template_path, config, output_path)
            if rendered:
                generated_files.append(rendered)

        return generated_files

    def _generate_django(self, config: ProjectConfig, output_dir: Path) -> List[Path]:
        """Generate Django project structure."""
        generated_files = []
        backend_dir = output_dir / "backend"

        templates = [
            ("django/requirements.txt.j2", backend_dir / "requirements.txt"),
            ("django/manage.py.j2", backend_dir / "manage.py"),
            ("django/config/__init__.py.j2", backend_dir / "config" / "__init__.py"),
            ("django/config/settings.py.j2", backend_dir / "config" / "settings.py"),
            ("django/config/urls.py.j2", backend_dir / "config" / "urls.py"),
            ("django/config/wsgi.py.j2", backend_dir / "config" / "wsgi.py"),
            ("django/config/asgi.py.j2", backend_dir / "config" / "asgi.py"),
            ("django/apps/__init__.py.j2", backend_dir / "apps" / "__init__.py"),
            ("django/apps/core/__init__.py.j2", backend_dir / "apps" / "core" / "__init__.py"),
            ("django/apps/core/apps.py.j2", backend_dir / "apps" / "core" / "apps.py"),
            ("django/apps/core/models.py.j2", backend_dir / "apps" / "core" / "models.py"),
            ("django/apps/api/__init__.py.j2", backend_dir / "apps" / "api" / "__init__.py"),
            ("django/apps/api/apps.py.j2", backend_dir / "apps" / "api" / "apps.py"),
            ("django/apps/api/urls.py.j2", backend_dir / "apps" / "api" / "urls.py"),
            ("django/apps/api/views/__init__.py.j2", backend_dir / "apps" / "api" / "views" / "__init__.py"),
            ("django/apps/api/views/health.py.j2", backend_dir / "apps" / "api" / "views" / "health.py"),
            ("django/.env.example.j2", backend_dir / ".env.example"),
        ]

        for template_path, output_path in templates:
            rendered = self._render_template(template_path, config, output_path)
            if rendered:
                generated_files.append(rendered)

        return generated_files

    def _render_template(
        self, template_path: str, config: ProjectConfig, output_path: Path
    ) -> Optional[Path]:
        """
        Render a template and write to file.

        Args:
            template_path: Relative path to template in boilerplate directory
            config: Project configuration
            output_path: Path to write rendered content

        Returns:
            Path to rendered file, or None if template doesn't exist
        """
        full_template_path = self.boilerplate_dir / template_path

        if not full_template_path.exists():
            logger.warning(f"Template not found: {full_template_path}")
            return None

        try:
            # Prepare context from config
            context = self._prepare_context(config)

            # Render template using relative path from templates directory
            relative_template_path = f"boilerplate/{template_path}"
            content = self.renderer.render_template(relative_template_path, context)

            # Ensure parent directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write rendered content
            output_path.write_text(content, encoding="utf-8")

            logger.info(f"Generated: {output_path}")
            return output_path

        except (FileNotFoundError, TemplateNotFound) as e:
            logger.warning(f"Template not found: {template_path} - {e}")
            return None
        except (TemplateSyntaxError, UndefinedError) as e:
            logger.error(f"Template error in {template_path}: {e}")
            return None
        except (IOError, OSError) as e:
            logger.error(f"Failed to write file {output_path}: {e}")
            return None
        except TemplateError as e:
            logger.error(f"Error rendering {template_path}: {e}")
            return None

    def _prepare_context(self, config: ProjectConfig) -> Dict[str, Any]:
        """Prepare template context from project configuration."""
        # Check if authentication is in features
        has_auth = any('auth' in str(f).lower() for f in (config.features or []))

        return {
            "project_name": config.project_name,
            "project_slug": config.project_slug,
            "project_description": config.description,
            "backend_framework": config.backend_framework,
            "frontend_framework": config.frontend_framework,
            "database": config.database,
            "has_authentication": has_auth,
            "has_database": bool(config.database),
            "has_email": any('email' in str(f).lower() for f in (config.features or [])),
            "has_caching": any('cach' in str(f).lower() or 'redis' in str(f).lower() for f in (config.features or [])),
            "api_port": DEFAULT_API_PORT,
            "frontend_port": DEFAULT_FRONTEND_PORT,
        }
