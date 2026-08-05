import re
from dataclasses import dataclass


@dataclass
class SkillDetection:
    """Result of detecting a skill."""

    name: str
    category: str
    confidence: float
    evidence: list[str]


class SkillExtractor:
    """Extract skills from source code and documentation."""

    PYTHON_KEYWORDS = {
        "import",
        "from",
        "def",
        "class",
        "async",
        "await",
        "yield",
        "lambda",
        "with",
    }

    JS_TS_KEYWORDS = {
        "import",
        "export",
        "require",
        "const",
        "let",
        "var",
        "function",
        "async",
        "await",
        "class",
    }

    REACT_INDICATORS = {
        "import React",
        "useState",
        "useEffect",
        "useContext",
        "useReducer",
        "useCallback",
        "useMemo",
        "useRef",
        "createContext",
        "ReactDOM.render",
        ".jsx",
        ".tsx",
    }

    FRAMEWORKS = {
        "django": ("Python", 0.95),
        "flask": ("Python", 0.95),
        "fastapi": ("Python", 0.95),
        "sqlalchemy": ("Python", 0.85),
        "numpy": ("Python", 0.85),
        "pandas": ("Python", 0.85),
        "scikit-learn": ("Python", 0.85),
        "tensorflow": ("Python", 0.85),
        "pytorch": ("Python", 0.85),
        "express": ("JavaScript", 0.95),
        "next.js": ("JavaScript", 0.95),
        "react": ("JavaScript", 0.95),
        "vue": ("JavaScript", 0.95),
        "angular": ("JavaScript", 0.95),
        "svelte": ("JavaScript", 0.85),
        "webpack": ("JavaScript", 0.85),
        "vite": ("JavaScript", 0.85),
        "rollup": ("JavaScript", 0.85),
        "jest": ("JavaScript", 0.80),
        "mocha": ("JavaScript", 0.80),
    }

    DATABASES = {
        "postgresql": ("PostgreSQL", 0.95),
        "psycopg": ("PostgreSQL", 0.95),
        "psycopg2": ("PostgreSQL", 0.95),
        "mysql": ("MySQL", 0.95),
        "mongodb": ("MongoDB", 0.95),
        "redis": ("Redis", 0.90),
        "elasticsearch": ("Elasticsearch", 0.90),
        "dynamodb": ("DynamoDB", 0.90),
        "firebase": ("Firebase", 0.85),
        "cassandra": ("Cassandra", 0.85),
        "oracle": ("Oracle", 0.85),
    }

    TOOLS = {
        "docker": 0.95,
        "kubernetes": 0.95,
        "git": 0.90,
        "github": 0.90,
        "gitlab": 0.90,
        "aws": 0.90,
        "gcp": 0.90,
        "azure": 0.90,
        "ci/cd": 0.85,
        "jenkins": 0.85,
        "terraform": 0.85,
        "ansible": 0.85,
    }

    def extract_skills(
        self,
        text: str,
        filename: str | None = None,
        repo_metadata: dict | None = None,
    ) -> list[SkillDetection]:
        """
        Extract skills from source code or documentation text.

        Args:
            text: The source text to analyze
            filename: Optional filename for extension-based detection

        Returns:
            List of detected skills with confidence scores
        """
        detected_skills: dict[str, SkillDetection] = {}

        # If repository metadata is provided, fold in file-structure evidence
        # and explicit workflow contents (if available).
        combined_text = text or ""
        if isinstance(repo_metadata, dict):
            file_structure = repo_metadata.get("file_structure")
            if isinstance(file_structure, list):
                combined_text += " " + " ".join(file_structure)
                # If there are GitHub Actions workflow filenames, mark CI/CD
                workflow_files = [f for f in file_structure if ".github/workflows" in f.lower()]
                if workflow_files:
                    # Add explicit detections for GitHub Actions and CI/CD
                    detected_skills.setdefault(
                        "GitHub Actions",
                        SkillDetection(
                            name="GitHub Actions",
                            category="Tool",
                            confidence=0.9,
                            evidence=[f"Found workflow file(s): {', '.join(workflow_files)}"],
                        ),
                    )
                    detected_skills.setdefault(
                        "CI/CD",
                        SkillDetection(
                            name="CI/CD",
                            category="Tool",
                            confidence=0.85,
                            evidence=["Repository contains CI/CD workflow files"],
                        ),
                    )

            # If raw workflow contents are provided under `workflows`, try to
            # extract job names or triggers for stronger evidence.
            workflows = repo_metadata.get("workflows")
            if isinstance(workflows, dict):
                for wf_name, wf_content in workflows.items():
                    if isinstance(wf_content, str):
                        evidence = []
                        low = wf_content.lower()
                        if "jobs:" in low:
                            evidence.append("jobs: defined in workflow")
                        if "on:" in low:
                            evidence.append("on: triggers defined in workflow")
                        gha = detected_skills.get("GitHub Actions")
                        if evidence and gha:
                            gha.evidence.append(f"{wf_name}: " + ", ".join(evidence))
                            gha.confidence = min(0.99, gha.confidence + 0.03)
                        elif evidence:
                            detected_skills["GitHub Actions"] = SkillDetection(
                                name="GitHub Actions",
                                category="Tool",
                                confidence=0.92,
                                evidence=[f"{wf_name}: " + ", ".join(evidence)],
                            )

        # Use combined_text for downstream pattern matching
        text = combined_text

        # Detect languages first
        self._detect_languages(text, filename, detected_skills)

        # Detect frameworks and libraries
        self._detect_frameworks(text, detected_skills)

        # Detect React specifically
        self._detect_react(text, detected_skills)

        # Detect databases
        self._detect_databases(text, detected_skills)

        # Detect tools
        self._detect_tools(text, detected_skills)

        # Sort by confidence
        return sorted(
            detected_skills.values(),
            key=lambda x: x.confidence,
            reverse=True,
        )

    def _detect_languages(
        self,
        text: str,
        filename: str | None,
        skills_dict: dict,
    ) -> None:
        """Detect programming languages."""
        text_lower = text.lower()

        # Python detection
        python_evidence = []
        if ".py" in str(filename or "").lower():
            python_evidence.append("Python file extension (.py)")
        if re.search(r"\bimport\s+\w+", text):
            python_evidence.append("Python import statements")
        if re.search(r"\bdef\s+\w+\s*\(", text):
            python_evidence.append("Python function definitions")
        if re.search(r":\s*(int|str|float|bool|list|dict)", text):
            python_evidence.append("Python type annotations")
        if "requirements.txt" in text_lower:
            python_evidence.append("requirements.txt found")

        if python_evidence:
            skills_dict["Python"] = SkillDetection(
                name="Python",
                category="Language",
                confidence=min(0.95, 0.6 + len(python_evidence) * 0.1),
                evidence=python_evidence,
            )

        # JavaScript/TypeScript detection
        js_evidence = []
        if ".js" in str(filename or "").lower():
            js_evidence.append("JavaScript file extension (.js)")
        if ".ts" in str(filename or "").lower():
            js_evidence.append("TypeScript file extension (.ts)")
        # Detect imports/require and TypeScript indicators
        tl = text.lower()
        if re.search(r"\bimport\b", tl) or "require(" in tl:
            js_evidence.append("CommonJS or ES6 imports")
        # TypeScript-specific syntax indicators
        if re.search(r"\b(interface|type|namespace)\b", tl):
            js_evidence.append("TypeScript syntax")
        if "package.json" in text_lower:
            js_evidence.append("package.json found")

        if js_evidence:
            confidence = min(0.95, 0.6 + len(js_evidence) * 0.1)
            filename_lower = str(filename or "").lower()
            is_ts_syntax = any("typescript" in ev.lower() for ev in js_evidence)
            lang = "TypeScript" if is_ts_syntax or ".ts" in filename_lower else "JavaScript"
            skills_dict[lang] = SkillDetection(
                name=lang,
                category="Language",
                confidence=confidence,
                evidence=js_evidence,
            )

        # Other languages by extension
        extension_langs = {
            ".java": ("Java", 0.95),
            ".cpp": ("C++", 0.95),
            ".cs": ("C#", 0.95),
            ".go": ("Go", 0.95),
            ".rs": ("Rust", 0.95),
            ".rb": ("Ruby", 0.95),
            ".php": ("PHP", 0.95),
            ".swift": ("Swift", 0.95),
        }

        filename_lower = str(filename or "").lower()
        for ext, (lang, confidence) in extension_langs.items():
            if ext in filename_lower:
                skills_dict[lang] = SkillDetection(
                    name=lang,
                    category="Language",
                    confidence=confidence,
                    evidence=[f"{lang} file extension"],
                )

    def _detect_frameworks(self, text: str, skills_dict: dict) -> None:
        """Detect frameworks and libraries."""
        text_lower = text.lower()

        for framework, (category, confidence) in self.FRAMEWORKS.items():
            if framework in text_lower:
                display_name = framework.title()
                if display_name not in skills_dict:
                    skills_dict[display_name] = SkillDetection(
                        name=display_name,
                        category=category,
                        confidence=confidence,
                        evidence=[f"Found '{framework}' in content"],
                    )

    def _detect_react(self, text: str, skills_dict: dict) -> None:
        """Detect React specifically."""
        text_lower = text.lower()
        react_evidence = []

        for indicator in self.REACT_INDICATORS:
            if indicator.lower() in text_lower:
                react_evidence.append(indicator)

        if react_evidence:
            skills_dict["React"] = SkillDetection(
                name="React",
                category="Framework",
                confidence=min(0.99, 0.7 + len(react_evidence) * 0.05),
                evidence=react_evidence,
            )

    def _detect_databases(self, text: str, skills_dict: dict) -> None:
        """Detect databases."""
        text_lower = text.lower()

        for db, payload in self.DATABASES.items():
            display_name, confidence = payload
            if db in text_lower and display_name not in skills_dict:
                skills_dict[display_name] = SkillDetection(
                    name=display_name,
                    category="Database",
                    confidence=confidence,
                    evidence=[f"Found '{db}' reference in content"],
                )

    def _detect_tools(self, text: str, skills_dict: dict) -> None:
        """Detect tools and DevOps technologies."""
        text_lower = text.lower()

        # Dockerfile-style detection (FROM ... and EXPOSE or RUN patterns)
        dockerfile_evidence = (
            bool(re.search(r"^\s*from\s+[\w\d\-\./:]+", text, flags=re.MULTILINE | re.IGNORECASE))
            and "expose" in text_lower
        )
        docker_compose_evidence = "version:" in text_lower and "services:" in text_lower

        for tool, confidence in self.TOOLS.items():
            if not (
                tool in text_lower
                or (tool == "docker" and (dockerfile_evidence or docker_compose_evidence))
            ):
                continue

            display_name = tool.upper() if tool in ["ci/cd"] else tool.title()
            if display_name not in skills_dict:
                evidence = [f"Found '{tool}' reference in content"]
                if tool == "docker" and dockerfile_evidence:
                    evidence.append("Dockerfile-style instructions detected")
                if tool == "docker" and docker_compose_evidence:
                    evidence.append("Docker Compose file structure detected")
                skills_dict[display_name] = SkillDetection(
                    name=display_name,
                    category="Tool",
                    confidence=confidence,
                    evidence=evidence,
                )
