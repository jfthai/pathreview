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

**Branch:** 14-github-actions-workflow-parser

**What you built:**
Added workflow-aware CI/CD detection across the ingestion and skill-extraction pipeline. `RepoAnalyzer.parse()` now treats `.github/workflows` entries as CI/CD evidence and includes `GitHub Actions` in `tech_stack`. `SkillExtractor` was extended to fold `repo_metadata["file_structure"]` and optional `workflows` content into its analysis so it can infer `GitHub Actions` / `CI/CD` skills from workflow filenames and YAML contents. Small updates were made to `agent/tools/tech_detector.py` to ensure `.github/workflows` is treated consistently.

**Tests added or updated:**
- `tests/unit/test_repo_analyzer.py`: new tests that verify `has_ci` and `tech_stack` include GitHub Actions when workflow paths are present.
- `tests/unit/test_skill_extractor.py`: updated to cover detection from `repo_metadata` (workflow filenames and simple YAML evidence).
- `tests/unit/test_tech_detector.py`: updated assertions for GitHub Actions detection from file lists.

**Self-review confirmation:** [X] make check passes  [X] make test-unit passes

**Draft PR feedback received from:** none


## Week 10 — Iteration & reflection

### Reviewer feedback

**Feedback received:** [ ] Yes  [X] No — still awaiting review

**Summary of feedback:**
[What did reviewers comment on? Or note that no review came in.]

**How you responded:**
[What changes did you make, or what did you reply? If no feedback,
leave blank.]

---

### Reflection

**What was harder than you expected?**
Working through the bug was harder than expected because the fix spanned multiple layers of the ingestion pipeline. The repository analyzer already detected workflows as CI/CD evidence, but the skill extractor and tech detector had to be aligned so workflow filenames and YAML content actually produced GitHub Actions / CI/CD skill output. That meant tracing metadata from RepoAnalyzer.parse() through SkillExtractor and ensuring the evidence format stayed consistent across tests.

**What did you learn about working in a large codebase?**
I learned that in a large codebase, the hard part is often understanding how data flows between modules rather than the individual implementation details. The ingestion metadata, parser outputs, and skill inference logic live in separate files (repo_analyzer.py, skill_extractor.py, and tech_detector.py), so I had to verify that the same concept of "GitHub Actions workflow evidence" was represented consistently in each layer. In contrast, my own projects tend to have tighter, more obvious boundaries.

**How did AI tools help — and where did they fall short?**
AI tools were helpful for identifying the relevant files and test locations quickly, especially when searching for workflows, RepoAnalyzer, and SkillExtractor. They were less useful for understanding the pipeline contract and subtle semantics of how repo_metadata gets passed into skill extraction, so I still had to read the code closely and reason about the end-to-end flow myself.

**What would you do differently if you started over?**
If I started over, I would map the ingestion-to-skill path first and add integration-style tests earlier. That means first confirming whether pipeline.py actually carries workflow content into SkillExtractor, and then writing tests that cover the end-to-end metadata flow instead of only unit tests in isolated modules.

**What are you most proud of from this module?**
I’m most proud of implementing a fix that closes a real semantic gap: GitHub Actions workflows now contribute to CI/CD skill detection instead of being ignored. This makes the tool more accurate for DevOps evidence and improves the value of the final repository analysis.