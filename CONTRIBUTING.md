# Contributing Guide

## Automatic Versioning

This project uses automatic semantic versioning based on your commits and changes. The version number will be automatically updated when you make a commit, following these rules:

### Version Bumps

The version number (MAJOR.MINOR.PATCH) will be incremented based on the following rules:

1. **MAJOR version** (x.0.0) when you:
   - Include "BREAKING CHANGE:" in your commit message
   - Add an exclamation mark after the type (e.g., "feat!: ...")

2. **MINOR version** (0.x.0) when you:
   - Start your commit message with "feat:" (new feature)

3. **PATCH version** (0.0.x) when you:
   - Make any other changes to Python files (excluding tests)
   - Start your commit message with "fix:"

4. **No version bump** when you:
   - Only modify documentation files (.md, .rst, .txt)
   - Only modify test files

### Commit Message Format

To properly trigger version bumps, use the following commit message format:

```
type[(scope)][!]: subject

[body]

[BREAKING CHANGE: description]
```

Where `type` can be:
- `feat`: A new feature (minor version bump)
- `fix`: A bug fix (patch version bump)
- `docs`: Documentation only changes (no version bump)
- `test`: Adding missing tests (no version bump)
- `chore`: Maintenance tasks (case by case version bump)

Examples:

```
feat: add user authentication
```
> Bumps MINOR version (0.x.0)

```
fix: correct password hashing
```
> Bumps PATCH version (0.0.x)

```
feat!: change API response format
BREAKING CHANGE: response now returns JSON instead of XML
```
> Bumps MAJOR version (x.0.0)

```
docs: update README
```
> No version bump

### How It Works

1. When you make a commit, a pre-commit hook runs automatically
2. The hook analyzes your changes and commit message
3. Based on the analysis, it updates the version in `pyproject.toml`
4. The updated version file is automatically added to your commit

You don't need to do anything special - just write meaningful commit messages following the format above, and the versioning will be handled automatically! 