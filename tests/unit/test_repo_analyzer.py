"""Tests for ingestion.parsers.repo_analyzer.RepoAnalyzer."""

import json

import pytest

from ingestion.parsers.repo_analyzer import RepoAnalyzer


@pytest.mark.unit
class TestRepoAnalyzer:
    """Unit tests for RepoAnalyzer."""

    @pytest.fixture
    def analyzer(self) -> RepoAnalyzer:
        return RepoAnalyzer()

    def test_github_actions_workflow_is_detected_as_ci_cd(self, analyzer: RepoAnalyzer) -> None:
        """RepoAnalyzer should detect GitHub Actions workflows as CI/CD evidence."""
        repo_data = {
            "name": "test-repo",
            "description": "Repository with a GitHub Actions workflow",
            "language": "Python",
            "file_structure": [
                ".github/workflows/build.yml",
                "main.py",
                "README.md",
            ],
            "readme_content": "# Test README",
            "pushed_at": "2026-07-28T00:00:00Z",
        }

        result = analyzer.parse(json.dumps(repo_data))

        assert result.metadata["has_ci"] is True
        assert any(
            skill in result.metadata["tech_stack"] for skill in ["GitHub Actions", "CI/CD"]
        ), f"Unexpected tech_stack: {result.metadata['tech_stack']}"
