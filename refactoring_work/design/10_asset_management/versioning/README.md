# Asset Versioning in OpenMAS

## Overview

This directory contains documentation about the asset versioning system in OpenMAS. Versioning ensures reproducibility, compatibility, and proper management of asset lifecycles throughout the framework.

## Versioning Principles

OpenMAS asset versioning follows these core principles:

1. **Explicit Versioning**: All assets must have explicit version identifiers
2. **Semantic Versioning**: Version numbers follow semantic versioning (MAJOR.MINOR.PATCH)
3. **Immutability**: Versioned assets are immutable; changes require a new version
4. **Compatibility Specifications**: Version requirements can specify compatibility ranges
5. **Version Resolution**: Clear rules determine how version requirements are resolved

## Version Syntax

OpenMAS uses standard semantic versioning with these components:

- **MAJOR**: Incremented for incompatible API changes
- **MINOR**: Incremented for backward-compatible functionality additions
- **PATCH**: Incremented for backward-compatible bug fixes
- **Pre-release**: Optional suffix for pre-release versions (e.g., `-alpha.1`)
- **Build metadata**: Optional build information (e.g., `+20230401`)

Examples of valid versions:
```
1.0.0
2.3.4
1.0.0-alpha.1
1.0.0-beta.2
1.0.0+20230401
1.0.0-alpha.1+20230401
```

## Version Requirements

Version requirements specify constraints on acceptable versions:

- **Exact Version**: `=1.2.3` - Exactly version 1.2.3
- **Greater Than**: `>1.2.3` - Any version greater than 1.2.3
- **Greater Than or Equal**: `>=1.2.3` - Version 1.2.3 or greater
- **Less Than**: `<1.2.3` - Any version less than 1.2.3
- **Less Than or Equal**: `<=1.2.3` - Version 1.2.3 or less
- **Compatible With**: `^1.2.3` - Any version from 1.2.3 up to but not including 2.0.0
- **Approximately Equal**: `~1.2.3` - Any version from 1.2.3 up to but not including 1.3.0
- **Range**: `>=1.2.3 <2.0.0` - Any version between 1.2.3 and 2.0.0 (excluding 2.0.0)

Examples in configuration:
```yaml
assets:
  model_asset:
    name: "example-model"
    version: "^1.2.3"  # Compatible with 1.2.3 up to 2.0.0
    
  embeddings:
    name: "text-embeddings"
    version: "~2.0.0"  # Compatible with 2.0.0 up to 2.1.0
    
  dataset:
    name: "training-data"
    version: ">=3.0.0 <4.0.0"  # Any 3.x.x version
```

## Version Resolution

When multiple version constraints apply, OpenMAS resolves them as follows:

1. **Intersection Rule**: The effective constraint is the intersection of all specified constraints
2. **Latest Compatible**: Within the constraint, the latest compatible version is selected
3. **Resolution Failure**: If constraints cannot be satisfied, resolution fails with clear error messages
4. **Overrides**: Explicit overrides can be specified for special cases

Example resolution process:
```
Constraint 1: ^1.2.0 (>=1.2.0 <2.0.0)
Constraint 2: >=1.3.0
Intersection: >=1.3.0 <2.0.0
Available versions: 1.2.0, 1.3.0, 1.3.1, 1.4.0, 2.0.0
Selected version: 1.4.0 (latest within constraint)
```

## Version Management

OpenMAS provides several mechanisms for version management:

### 1. Version Declaration

Assets declare their version in their definition:
```yaml
assets:
  example_asset:
    name: "example-asset"
    version: "1.2.3"
    # Other asset properties
```

### 2. Version Constraints

Components specify version constraints for required assets:
```yaml
components:
  example_component:
    required_assets:
      - name: "example-asset"
        version: "^1.2.0"
```

### 3. Version Compatibility

Assets can declare compatibility with other assets:
```yaml
assets:
  model_asset:
    name: "llm-model"
    version: "1.0.0"
    compatibility:
      - asset: "prompt-template"
        version: "^2.0.0"
```

### 4. Version Aliases

Named aliases for specific versions or version ranges:
```yaml
version_aliases:
  stable: "=1.2.3"
  latest: "^1.0.0"
  development: ">=1.0.0-alpha.1"
```

## Versioning Workflows

OpenMAS supports these common versioning workflows:

### 1. Development Cycle

1. Development starts on a new version with `-alpha` suffix
2. As features stabilize, progress to `-beta` suffix
3. For release candidates, use `-rc` suffix
4. Final release removes pre-release suffix
5. Patch releases increment the patch version

### 2. Compatibility Management

1. Backward-compatible changes increment MINOR version
2. Breaking changes increment MAJOR version
3. Bug fixes increment PATCH version
4. Components specify the widest compatible version range
5. Version resolution finds the optimal compatible version

### 3. Version Pinning

For reproducible environments:
1. Use exact version requirements (`=1.2.3`)
2. Generate version lock files specifying exact versions
3. Version resolution uses locked versions when available

## References

- [Asset Management Architecture](/10_asset_management/architecture.md)
- [Asset Types](/10_asset_management/types/README.md)
- [Configuration Schema](/03_configuration/unified_configuration_schema.md)
