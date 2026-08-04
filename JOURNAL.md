## Week 7 — Issue selection

**Issue link:** https://github.com/ascherj/pathreview/issues/14

**Issue title:** Add support for parsing GitHub Actions workflow files to detect CI/CD skills 

**Tier:** [ ] Tier 1  [ ] Tier 2  [X] Tier 3

**Problem summary:**
The project currently misses evidence of DevOps and CI/CD experience when a repository includes GitHub Actions workflow files, because the ingestion pipeline does not parse those workflow files and the skill extractor does not infer related skills from them. As a result, a developer’s automation, testing, and deployment practices can be overlooked even when they are clearly demonstrated in the repo. A successful fix would add workflow-file parsing to the ingestion pipeline and surface inferred skills such as GitHub Actions, Docker, pytest, and deployment in the analysis output.

**Branch name:** 14-github-actions-workflow-parser

**Setup confirmation:** [X] App runs locally at localhost:5173

**Cohort ledger:** [X] Issue added to cohort ledger

**"Is this right for me?" checklist reasoning**
This issue is a good fit because it is about a missing capability in the repository-ingestion flow: GitHub Actions workflow files are not being parsed, so CI/CD-related evidence is missed and the resulting skill extraction is incomplete. The expected behavior is that workflow YAML files contribute to the analysis by surfacing skills such as GitHub Actions, Docker, pytest, and deployment in the final output.

The change appears to affect the ingestion and analysis pipeline rather than a single isolated function. The relevant code lives in the parser and skill-detection modules, especially ingestion/parsers/repo_analyzer.py, ingestion/parsers/skill_extractor.py, and agent/tools/tech_detector.py, with existing tests in tests/unit/test_skill_extractor.py to build on. This feels like a Tier 3 issue because it spans multiple modules and touches the end-to-end ingestion and skill inference path, but it is still realistic for this sprint because the affected code is relatively contained and the existing test structure gives a clear place to add coverage. I do not see any obvious blockers or dependencies from the issue description, so this looks achievable within the available time.

---

## Week 8 — Reproduction & solution planning

**Reproduction commit link:** https://github.com/jfthai/pathreview/commit/496523b1cfe6ad3e88a6baff43ebece52d108d16

**Reproduction summary:**
Code inspection of `ingestion/parsers/repo_analyzer.py` and `agent/tools/tech_detector.py` shows that `.github/workflows` is recognized as a CI/CD indicator from repository metadata, but workflow YAML files are not parsed or used to infer `GitHub Actions` / `CI/CD` skills. This means a repo can include GitHub Actions workflows and still miss workflow-related skill extraction.

**PLAN.md link:** ./PLAN.md

**Blockers or open questions:**
None at this time.

## Week 9 — Solution building & PR submission

### Check-in 1 (mid-week)

**Current progress:**
Implement plan step 1.

**Next steps:**
Step 2-4

**Blockers:**
n/a

---

### Check-in 2 (end of week)

**PR link:** [link to your submitted pull request]

**Branch:** [the branch name you worked on, e.g. `fix/123-short-description`]

**What you built:**
[1–3 sentences summarizing what your fix does and how it works]

**Tests added or updated:**
[Which test files did you touch? What do they cover?]

**Self-review confirmation:** [ ] make check passes  [ ] make test-unit passes

**Draft PR feedback received from:** [name or Slack handle, or "none"]