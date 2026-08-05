"""Technology stack detector tool."""

import structlog

from .base import BaseTool, ToolResult

logger = structlog.get_logger()


class TechDetector(BaseTool):
    """Detect technology stack from repository files."""

    name = "tech_detector"
    description = "Detect technology stack from repository files"

    # File extension to language mapping
    EXT_TO_LANG = {
        ".py": "Python",
        ".ipynb": "Python",
        ".js": "JavaScript",
        ".jsx": "JavaScript",
        ".ts": "TypeScript",
        ".tsx": "TypeScript",
        ".go": "Go",
        ".rs": "Rust",
        ".java": "Java",
        ".kt": "Kotlin",
        ".cs": "C#",
        ".cpp": "C++",
        ".c": "C",
        ".h": "C",
        ".rb": "Ruby",
        ".php": "PHP",
        ".swift": "Swift",
        ".scala": "Scala",
        ".r": "R",
        ".m": "Objective-C",
        ".groovy": "Groovy",
    }

    # Config file to language/framework mapping
    CONFIG_INDICATORS = {
        "package.json": ("Node.js", "JavaScript"),
        "package-lock.json": ("Node.js", "JavaScript"),
        "yarn.lock": ("Node.js", "JavaScript"),
        "requirements.txt": ("Python", "Python"),
        "setup.py": ("Python", "Python"),
        "Pipfile": ("Python", "Python"),
        "Gemfile": ("Ruby", "Ruby"),
        "Cargo.toml": ("Rust", "Rust"),
        "pom.xml": ("Java", "Java"),
        "build.gradle": ("Java", "Java"),
        "Dockerfile": ("Docker", "Infrastructure"),
        "docker-compose.yml": ("Docker", "Infrastructure"),
        ".github/workflows": ("GitHub Actions", "CI/CD"),
        "Makefile": ("Make", "Build"),
        "cmake": ("CMake", "Build"),
    }

    def execute(self, input_data: dict) -> ToolResult:
        """Detect tech stack from files.

        Args:
            input_data: Must contain 'files' (list of file paths)

        Returns:
            ToolResult with detected technologies
        """
        files = input_data.get("files", [])

        if not files:
            logger.warning("tech_detector_no_files")
            return ToolResult(
                success=True,
                data={
                    "primary_language": "Unknown",
                    "all_languages": [],
                    "frameworks": [],
                },
            )

        try:
            result = self._detect_tech(files)
            return ToolResult(success=True, data=result)

        except Exception as e:
            logger.error("tech_detector_error", error=str(e))
            return ToolResult(success=False, data={}, error=str(e))

    def _detect_tech(self, files: list[str]) -> dict:
        """Detect technologies from file list.

        Args:
            files: List of file paths

        Returns:
            Dict with detected languages and frameworks
        """
        # Filter out vendor/build directories
        filtered_files = [f for f in files if not self._should_skip_file(f)]

        languages = set()
        frameworks = set()

        # Detect by file extension
        for filepath in filtered_files:
            for ext, lang in self.EXT_TO_LANG.items():
                if filepath.endswith(ext):
                    languages.add(lang)

        # Detect by config files and indicators (match substrings so directories
        # like `.github/workflows/ci.yml` are recognized)
        tools = set()
        for filepath in filtered_files:
            filepath_lower = filepath.lower()
            for config_file, (framework, lang) in self.CONFIG_INDICATORS.items():
                indicator = config_file.lower()
                if indicator in filepath_lower or filepath_lower.endswith(indicator):
                    # Add language when the mapping provides one and it's not a CI marker
                    if lang and lang not in ("CI/CD", "Infrastructure"):
                        languages.add(lang)
                    # Add framework when it's a concrete framework/stack
                    if framework and framework not in (
                        "Docker",
                        "Infrastructure",
                        "CI/CD",
                        "Build",
                    ):
                        frameworks.add(framework)
                    # Treat CI systems as tools
                    if framework in (
                        "GitHub Actions",
                        "Travis CI",
                        "CircleCI",
                        "GitLab CI",
                        "Jenkins",
                    ):
                        tools.add(framework)

        # Determine primary language (most common by file count)
        primary = "Unknown"
        language_counts: dict[str, int] = {}
        for filepath in filtered_files:
            for ext, lang in self.EXT_TO_LANG.items():
                if filepath.lower().endswith(ext):
                    language_counts[lang] = language_counts.get(lang, 0) + 1

        if language_counts:
            primary = max(language_counts.items(), key=lambda item: (item[1], item[0]))[0]

        all_languages = sorted(languages)
        all_frameworks = sorted(frameworks)
        all_tools = sorted(tools)

        logger.info(
            "tech_detected",
            primary_lang=primary,
            languages_count=len(all_languages),
            frameworks_count=len(all_frameworks),
        )

        return {
            "primary_language": primary,
            "all_languages": all_languages,
            "frameworks": all_frameworks,
            "tools": all_tools,
        }

    @staticmethod
    def _should_skip_file(filepath: str) -> bool:
        """Check if file should be skipped.

        Args:
            filepath: File path

        Returns:
            True if file should be skipped
        """
        normalized = filepath.replace("\\", "/")
        skip_patterns = [
            "node_modules/",
            "vendor/",
            "dist/",
            "build/",
            ".git/",
            "__pycache__/",
            ".venv/",
            "venv/",
        ]

        return any(pattern in normalized for pattern in skip_patterns)
