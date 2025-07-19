# Configuration Files for OpenMAS 0.3.0

## Task Overview
Create and configure all necessary configuration files for OpenMAS 0.3.0, adapting from the 0.2.0 versions where appropriate.

## Tasks

1. Project Configuration
   - Create `pyproject.toml` with updated dependencies, version, and project info
   - Configure Poetry for dependency management
   - Setup proper Python packaging configuration

2. Code Quality Tools
   - Configure `.flake8` for linting with appropriate rules
   - Setup `mypy.ini` for static type checking
   - Create `.pre-commit-config.yaml` for pre-commit hooks
   - Configure Black, isort, and other formatting tools

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
black = "^23.3.0"
isort = "^5.12.0"
mypy = "^1.3.0"
flake8 = "^6.0.0"
tox = "^4.6.0"
pre-commit = "^3.3.2"
mkdocs = "^1.4.3"
mkdocs-material = "^9.1.15"
mkdocstrings = "^0.22.0"

[tool.poetry.scripts]
openmas = "openmas.cli:main"

[tool.black]
line-length = 88
target-version = ["py38"]
include = '\.pyi?$'

[tool.isort]
profile = "black"
line_length = 88
multi_line_output = 3

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
    flake8>=6.0.0
    black>=23.3.0
    isort>=5.12.0
commands =
    flake8 src/openmas tests
    black --check src/openmas tests
    isort --check-only src/openmas tests

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

[flake8]
max-line-length = 88
extend-ignore = E203
exclude = .git,__pycache__,build,dist,.tox
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
    - name: Lint with flake8, black, and isort
      run: |
        poetry run flake8 src/openmas tests
        poetry run black --check src/openmas tests
        poetry run isort --check-only src/openmas tests
```

## Success Criteria
- All configuration files properly created and configured
- Poetry, pytest, tox, flake8, mypy, and other tools properly configured
- CI/CD workflows setup for GitHub Actions
- Documentation generation configured with MkDocs
- Code quality tools properly integrated
