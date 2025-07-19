# Git Management and Versioning for OpenMAS 0.3.0

## Task Overview
Set up proper Git management and versioning for the OpenMAS 0.3.0 development process, ensuring a clean separation from the 0.2.0 codebase while preserving history and enabling reference to the previous version.

## Tasks

1. Branch Strategy
   - Create and configure the `030` branch
   - Set up branch protection rules
   - Configure merge requirements

2. Version Tagging
   - Define version tagging strategy
   - Set up automated version management
   - Configure release process

3. History Preservation
   - Ensure Git history is preserved when moving files to 0.2.0 subdirectory
   - Set up proper commit message patterns
   - Configure automatic changelog generation

4. Git Hooks and Workflows
   - Configure pre-commit hooks for code quality
   - Set up GitHub Actions for CI/CD
   - Configure automated testing on PR

## Branch Strategy

### Main Branches
- `main`: Production-ready code
- `030`: Development branch for version 0.3.0
- `030-feature-*`: Feature branches for specific 0.3.0 features

### Branch Flow
1. Create the `030` branch from `main`
2. Move all content to `0.2.0` subdirectory in a single commit
3. Set up new project structure in separate commits
4. For each feature, create a feature branch from `030`
5. Merge feature branches back to `030` when complete
6. When 0.3.0 is complete, merge `030` to `main`

### Git Commands
```bash
# Create the 030 branch
git checkout -b 030

# Move all files to 0.2.0 subdirectory (script will handle this)
./scripts/move_to_subdir.sh

# Add and commit the changes
git add .
git commit -m "chore: move 0.2.0 codebase to subdirectory"

# For feature development
git checkout -b 030-feature-<feature-name>
# ... make changes ...
git commit -m "feat: implement <feature>"
git push origin 030-feature-<feature-name>
# Create PR to merge back to 030
```

## Versioning Strategy

### Semantic Versioning
OpenMAS follows semantic versioning (MAJOR.MINOR.PATCH):
- MAJOR: 0 (pre-1.0 development)
- MINOR: 3 (significant new functionality)
- PATCH: 0 (initial release of 0.3 series)

### Version Management
- Version in `pyproject.toml`: `version = "0.3.0"`
- Version in `__init__.py`: `__version__ = "0.3.0"`
- Version in documentation: `0.3.0`

### Release Tags
```bash
# When ready to release 0.3.0
git tag -a v0.3.0 -m "OpenMAS 0.3.0"
git push origin v0.3.0
```

## Commit Message Guidelines

Follow the Conventional Commits specification:

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `build`: Changes that affect the build system or external dependencies
- `ci`: Changes to CI configuration files and scripts
- `chore`: Other changes that don't modify src or test files

Example:
```
feat(agent): add support for A2A protocol agent cards

Implements agent card generation and publishing for A2A protocol,
ensuring all capabilities are properly exposed through the agent card.

Refs: #123
```

## GitHub Workflows

### Pull Request Workflow
```yaml
name: Pull Request

on:
  pull_request:
    branches: [ main, 030 ]

jobs:
  quality:
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
    - name: Run linting
      run: |
        poetry run flake8 src/openmas tests
        poetry run black --check src/openmas tests
        poetry run isort --check-only src/openmas tests
        poetry run mypy src/openmas tests
    - name: Run tests
      run: |
        poetry run pytest tests/ --cov=openmas --cov-report=xml
```

### Release Workflow
```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
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
    - name: Build package
      run: poetry build
    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.PYPI_API_TOKEN }}
    - name: Create GitHub Release
      uses: softprops/action-gh-release@v1
      with:
        body_path: CHANGELOG.md
        files: |
          dist/*.whl
          dist/*.tar.gz
```

## Script to Move Files to 0.2.0 Directory

Create a script to move all files to the 0.2.0 subdirectory while preserving Git history:

```bash
#!/bin/bash
# scripts/move_to_subdir.sh
# Script to move all files to 0.2.0 subdirectory

set -e

# Create the 0.2.0 directory if it doesn't exist
mkdir -p 0.2.0

# Move all visible files and directories except .git to 0.2.0
find . -maxdepth 1 -not -path "./0.2.0" -not -path "./.git" -not -path "." | while read file; do
  git mv "$file" "0.2.0/"
done

# Move all hidden files and directories except .git to 0.2.0
find . -maxdepth 1 -name ".*" -not -path "./.git" -not -path "." | while read file; do
  git mv "$file" "0.2.0/"
done

echo "All files moved to 0.2.0 subdirectory"
```

## Success Criteria
- `030` branch created and configured
- All files properly moved to 0.2.0 subdirectory with preserved history
- Version information properly updated in all locations
- Git hooks and workflows properly configured
- Commit message guidelines established
- Release process defined
