# 🛠️ **Agent Prompt: OpenMAS Ruff Migration Task**

## **Context & Objective**
You are tasked with migrating the OpenMAS 0.3.0 codebase from using separate `black`, `isort`, and `flake8` tools to using `ruff` as the unified linting and formatting solution. This migration must be comprehensive, tested, and maintain all existing quality standards.

## **Critical Project Context**
- **Project**: OpenMAS 0.3.0 - Multi-agent framework with reasoning agnosticism
- **Current State**: Uses black, isort, flake8 separately with specific configurations
- **Target State**: Unified ruff configuration maintaining same quality standards
- **Anti-Hallucination Requirement**: All changes must be tested and verified to work

## **Task Breakdown**

### **Task 1: Update Setup Documentation**
**File**: `refactoring_work/setup/project_setup/02_configuration_files.md`

**Required Changes**:
1. Replace all references to `black`, `isort`, `flake8` with `ruff`
2. Update configuration examples to use ruff's unified approach
3. Update command examples in the document
4. Update GitHub Actions workflow examples to use ruff
5. Update tox.ini examples to use ruff
6. Maintain the same quality standards (line length, ignore rules, etc.)

### **Task 2: Update Task Creation Protocol**
**File**: `refactoring_work/planning/TASK_CREATION_PROTOCOL.md`

**Required Changes**:
1. Update "Phase 2.5: Quality & Linting Enforcement" section
2. Replace all quality enforcement commands with ruff equivalents
3. Update quality checklist items to reference ruff instead of separate tools
4. Update violation detection and remediation sections
5. Ensure all anti-hallucination measures remain intact
6. Update command examples to use ruff

### **Task 3: Implement Ruff Configuration**
**Files to Update**:
- `pyproject.toml` - Add ruff configuration section
- `.pre-commit-config.yaml` - Replace black/isort/flake8 hooks with ruff
- `tox.ini` - Update lint environment to use ruff
- Remove: `.flake8` file (no longer needed)

**Configuration Requirements**:
- **Line length**: 120 (from current black config)
- **Import sorting**: black-compatible profile
- **Linting rules**: Equivalent to current flake8 rules (E203, W503 ignored)
- **Python version**: 3.10+ compatibility
- **Format**: Enable ruff formatting to replace black
- **Lint**: Enable comprehensive linting to replace flake8

### **Task 4: Test Implementation**
**Verification Steps**:
1. Run `ruff check src/openmas tests` - must pass
2. Run `ruff format src/openmas tests` - must work without errors
3. Run `pre-commit run --all-files` - must pass
4. Run `tox -e lint` - must pass
5. Verify no formatting/linting regressions introduced

## **Current Configuration Reference**

**From `.pre-commit-config.yaml`**:
```yaml
- repo: https://github.com/psf/black
  rev: 25.1.0
  hooks:
  - id: black
    language_version: python3.10
    args: ['--line-length=120']

- repo: https://github.com/pycqa/isort
  rev: 6.0.1
  hooks:
  - id: isort
    args: ['--profile=black', '--line-length=120']
```

**From `.flake8`**:
```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = 
    .git,
    __pycache__,
    .tox,
    .eggs,
    *.egg,
    build,
    dist,
    .venv,
    venv,
    env,
    0.2.0/
per-file-ignores =
    __init__.py:F401
    tests/*:F401,F841
```

## **Expected Ruff Configuration**
Add to `pyproject.toml`:
```toml
[tool.ruff]
line-length = 120
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "D", "UP", "N", "B", "SIM"]
ignore = ["E203", "W503"]
exclude = [
    ".git",
    "__pycache__",
    ".tox",
    ".eggs",
    "*.egg",
    "build",
    "dist",
    ".venv",
    "venv",
    "env",
    "0.2.0/",
]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]
"tests/*" = ["F401", "F841"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"

[tool.ruff.lint.isort]
profile = "black"
```

## **Quality Gates**
Before completing this task, you MUST verify:
1. ✅ All existing code passes `ruff check`
2. ✅ All existing code can be formatted with `ruff format` without changes
3. ✅ Pre-commit hooks work correctly
4. ✅ Tox lint environment passes
5. ✅ No quality regressions introduced
6. ✅ Documentation accurately reflects new tooling

## **Anti-Hallucination Requirements**
- **Test everything**: Don't assume configurations work - test them
- **Verify compatibility**: Ensure ruff rules match existing quality standards
- **Check all files**: Update ALL references to old tools
- **Run commands**: Actually execute the verification steps

## **Success Criteria**
- All three files updated correctly
- Ruff configuration implemented and tested
- All quality gates pass
- Documentation reflects new tooling
- No linting/formatting regressions
- Task Creation Protocol uses ruff commands

---

**Important**: This migration maintains the same quality standards while modernizing the toolchain. Test thoroughly to ensure no regressions are introduced.
