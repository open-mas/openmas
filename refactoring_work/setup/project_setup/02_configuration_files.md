# Configuration Files for OpenMAS 0.3.0

## Task Overview
Create and configure all necessary configuration files for OpenMAS 0.3.0, adapting from the 0.2.0 versions where appropriate.

## Tasks

1. Project Configuration
   - Create `pyproject.toml` with updated dependencies, version, and project info
   - Configure Poetry for dependency management
   - Setup proper Python packaging configuration

2. Code Quality Tools
   - Configure `ruff` for unified linting and formatting
   - Setup `mypy.ini` for static type checking
   - Create `.pre-commit-config.yaml` for pre-commit hooks
   - Configure ruff with appropriate rules and formatting options

3. Testing Configuration
   - Create `pytest.ini` for test configuration
   - Setup `tox.ini` for multi-environment testing
   - Configure coverage reporting

4. Documentation
   - Configure `mkdocs.yml` for documentation generation
   - Setup appropriate documentation theme and plugins

5. CI/CD Configuration
   - Configure GitHub Actions workflows in `.github/workflows/`
   - Setup testing, linting, and publishing workflows

## Configuration Templates

### pyproject.toml Example

```toml
[tool.poetry]
name = "openmas"
version = "0.3.0"
description = "OpenMAS - Open Multi-Agent System Framework"
authors = ["OpenMAS Contributors"]
license = "MIT"
readme = "README.md"
repository = "https://github.com/openmas-ai/openmas"
documentation = "https://docs.openmas.ai"
packages = [{include = "openmas", from = "src"}]

[tool.poetry.dependencies]
python = "^3.8"
pydantic = "^2.0.0"
PyYAML = "^6.0"
requests = "^2.28.0"
typing-extensions = "^4.5.0"
jinja2 = "^3.1.2"
jsonschema = "^4.17.3"

[tool.poetry.group.dev.dependencies]
pytest = "^7.3.1"
pytest-cov = "^4.1.0"
ruff = "^0.1.0"
mypy = "^1.3.0"
tox = "^4.6.0"
pre-commit = "^3.3.2"
mkdocs = "^1.4.3"
mkdocs-material = "^9.1.15"
mkdocstrings = "^0.22.0"

[tool.poetry.scripts]
openmas = "openmas.cli:main"

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

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

### tox.ini Example

```ini
[tox]
isolated_build = True
envlist = py38, py39, py310, py311, lint, type, docs

[testenv]
deps =
    pytest>=7.3.1
    pytest-cov>=4.1.0
commands =
    pytest {posargs:tests} --cov=openmas --cov-report=xml

[testenv:lint]
deps =
    ruff>=0.1.0
commands =
    ruff check src/openmas tests
    ruff format --check src/openmas tests

[testenv:type]
deps =
    mypy>=1.3.0
    types-PyYAML
    types-requests
commands =
    mypy src/openmas tests

[testenv:docs]
deps =
    mkdocs>=1.4.3
    mkdocs-material>=9.1.15
    mkdocstrings>=0.22.0
commands =
    mkdocs build

# Ruff configuration is now in pyproject.toml under [tool.ruff]
# No separate .flake8 file needed
```

### GitHub Workflow Template

```yaml
name: Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10', '3.11']

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install poetry
        poetry install
    - name: Test with pytest
      run: |
        poetry run pytest tests/ --cov=openmas
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true

  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install poetry
        poetry install
    - name: Lint and format with ruff
      run: |
        poetry run ruff check src/openmas tests
        poetry run ruff format --check src/openmas tests
```

## Success Criteria
- All configuration files properly created and configured
- Poetry, pytest, tox, flake8, mypy, and other tools properly configured
- CI/CD workflows setup for GitHub Actions
- Documentation generation configured with MkDocs
- Code quality tools properly integrated
