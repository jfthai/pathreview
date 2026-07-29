## Solution plan

**Issue:** Add support for parsing GitHub Actions workflow files to detect CI/CD skills https://github.com/ascherj/pathreview/issues/14

### Understand
The root cause is that the repository ingestion and skill detection flow only checks for CI/CD by file-path presence and does not parse `.github/workflows/*.yml` contents or infer workflow-related skills from workflow files. Expected behavior is that a repo containing GitHub Actions workflows should be recognized as CI/CD-enabled and should surface skills like `GitHub Actions`, `CI/CD`, and related automation tooling. Actual behavior is that workflow files can be present, but the final analysis still misses CI/CD evidence and skill inference for those workflows.

### Map
Files and modules involved:
- `ingestion/parsers/repo_analyzer.py`
- `ingestion/parsers/skill_extractor.py`
- `agent/tools/tech_detector.py`
- `ingestion/pipeline.py` (for the repo metadata ingestion flow)
- `tests/unit/test_tech_detector.py`
- `tests/unit/test_skill_extractor.py`
- potentially new parser tests for repo metadata workflow detection

### Plan
1. Extend repository metadata analysis in `ingestion/parsers/repo_analyzer.py` so `.github/workflows` is treated as explicit CI/CD evidence and workflow files contribute to `tech_stack`.
2. Add workflow-aware detection in `ingestion/parsers/skill_extractor.py` and/or `agent/tools/tech_detector.py`, using workflow filenames and optionally parsed YAML content to infer `GitHub Actions` and `CI/CD` skills.
3. Add or update unit tests in `tests/unit/test_tech_detector.py`, `tests/unit/test_skill_extractor.py`, and a new parser test covering repo metadata workflow detection.
4. Run `pytest tests/unit/test_tech_detector.py tests/unit/test_skill_extractor.py` and a local ingestion sample via `ingestion/pipeline.py` or direct `RepoAnalyzer.parse()` calls to confirm the bug is reproducible and fixed.

### Inputs & outputs
Input:
- repository metadata containing `file_structure` or file list with `.github/workflows/*.yml`
- optional workflow YAML content passed through the skill extraction pipeline

Output:
- `has_ci` becomes true for repos with GitHub Actions workflows in `repo_analyzer.py`
- `tech_stack` includes `GitHub Actions` / `CI/CD` indicators in `repo_analyzer.py`
- detected skills include `GitHub Actions` and/or `CI/CD` in `skill_extractor.py` / `tech_detector.py`

### Risks & unknowns
- The ingestion pipeline in `ingestion/pipeline.py` may only pass repository metadata, not raw workflow file contents, so YAML parsing support might be limited.
- `agent/tools/tech_detector.py` already contains `.github/workflows` in `CONFIG_INDICATORS`, so changes must avoid duplicate CI/CD signals or inconsistent language/framework output.
- `repo_data` shape may vary between GitHub metadata, pipeline sources, and tests; verify `file_structure` handling in `RepoAnalyzer.parse()` and avoid assumptions about list vs string representations.

### Edge cases
- repository has `.github/workflows` directory but no YAML/workflow files present
- workflow files use non-standard names or are nested deeper than expected under `.github/workflows`
- repo contains other CI config files such as `.travis.yml`, `.circleci/`, or `gitlab-ci.yml` alongside GitHub Actions
- file structure is provided as a string, list, or nested object; detection should be case-insensitive and resilient

### Acceptance criteria
- A repository metadata ingestion path with `.github/workflows/*.yml` sets `has_ci` to true in `RepoAnalyzer.parse()`.
- `RepoAnalyzer.parse()` includes `GitHub Actions` or `CI/CD` in `tech_stack` when workflow files are present.
- Skill extraction detects `GitHub Actions` and/or `CI/CD` from workflow path or workflow content evidence.
- Unit tests cover the repo analyzer, tech detector, and skill extractor behavior for GitHub Actions workflow detection.
- The fix does not break existing CI/CD detection for `.travis.yml`, `.circleci/`, or `gitlab-ci.yml` paths.