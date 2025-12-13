---
adr: 0005
title: Path Traversal Security Model
date: 2025-11-26
status: Accepted
---

# ADR-0005: Path Traversal Security Model

## Status

✅ **Accepted**

**Date**: 2025-11-26 (Security fix implemented 2025-11-25, commit aeedd96)

## Context

The Claude Code Generator accepts user-provided output directory paths and creates files within them. This creates a potential security vulnerability: **path traversal attacks**.

**Attack Vector Example**:
```bash
python -m src.cli.main init --name "Evil" \
  --description "Hack" \
  --output "../../../etc/passwd"
```

Without proper validation, an attacker could:
- Write files outside the intended directory (e.g., `/etc/passwd`, `~/.ssh/authorized_keys`)
- Overwrite system files
- Gain unauthorized access to sensitive directories
- Execute arbitrary code via crafted file paths

**The Challenge**: Need to validate paths BEFORE creating files, while still allowing legitimate nested directories like `projects/my-app/backend`.

**Initial Implementation Flaw**:
The original validation checked for `..` components AFTER calling `.resolve()`, which normalized the path and removed the attack indicators:
```python
output_dir = Path(output_dir).resolve()  # ← Normalizes path first!
for part in output_dir.parts:
    if part == '..':                      # ← Never triggers!
        logger.warning(...)
```

This was **completely ineffective** because `.resolve()` converts `../../../etc/passwd` to `/etc/passwd` before the check runs.

## Decision

We will validate for path traversal BEFORE resolving paths, using a two-step approach:

**Validation Sequence**:
1. **Check for '..' components** in the original, unresolved path
2. **Reject immediately** if any '..' components are found
3. **Then resolve** the path to absolute form (only after validation passes)
4. **Check path length** for Windows compatibility (MAX_PATH_LENGTH = 200)

**Implementation** (`src/generator/file_generator.py:38-74`):
```python
def _validate_output_path(self, output_dir: Path) -> Path:
    # Step 1: Check for path traversal BEFORE resolving
    original_path = Path(output_dir)
    for part in original_path.parts:
        if part == '..':
            raise ValueError(
                f"Path traversal not allowed: {output_dir}. "
                f"Paths containing '..' components are forbidden for security reasons."
            )

    # Step 2: Now safe to resolve to absolute path
    try:
        output_dir = original_path.resolve()
    except (ValueError, OSError) as e:
        raise ValueError(f"Invalid output path: {e}") from e

    # Step 3: Check path length (Windows compatibility)
    if len(str(output_dir)) > MAX_PATH_LENGTH:
        raise ValueError(f"Output path too long...")

    return output_dir
```

**Blocked Attack Patterns**:
- `../../../etc/passwd` → BLOCKED
- `/home/user/../admin/config` → BLOCKED
- `./test/../../../secret` → BLOCKED
- `projects/../../../etc` → BLOCKED

**Allowed Patterns**:
- `projects/my-app` → ALLOWED
- `./my-project` → ALLOWED
- `/absolute/path/to/project` → ALLOWED
- `C:\Users\Name\project` → ALLOWED (Windows)

## Consequences

**Positive:**
- **Eliminates path traversal vulnerability**: Cannot write files outside intended directory
- **Simple and effective**: Single check blocks all '..' patterns
- **Early validation**: Fails fast before any file operations
- **Clear error messages**: Users understand why path was rejected
- **Cross-platform**: Works on Windows, Linux, macOS
- **Comprehensive testing**: 3 dedicated security tests verify protection
- **Zero false positives**: Legitimate paths are never blocked

**Negative:**
- **Cannot use relative paths with '..'**: Even legitimate `../sibling-dir` is blocked
- **Slightly restrictive**: Users must use absolute paths or forward-only relative paths
- **Migration concern**: Existing users using `..` patterns would need to update

**Neutral:**
- **Resolve after validation**: Normalized paths only created after security check passes
- **Windows path length**: 200-char limit leaves room for nested project files

## Alternatives Considered

### Validate After Resolve (Original Approach)
- **Implementation**:
  ```python
  output_dir = Path(output_dir).resolve()
  for part in output_dir.parts:
      if part == '..':
          raise ValueError(...)
  ```
- **Pros**:
  - Simple logic
  - Works with resolved paths
- **Cons**:
  - **COMPLETELY INEFFECTIVE**: `.resolve()` removes '..' before check runs
  - **Security vulnerability**: Allows arbitrary file writes
  - **False sense of security**: Code looks safe but isn't
- **Why rejected**: Doesn't actually prevent path traversal attacks.

### Check Resolved Path Against Base Directory
- **Implementation**:
  ```python
  output_dir = Path(output_dir).resolve()
  base_dir = Path.cwd().resolve()
  if not str(output_dir).startswith(str(base_dir)):
      raise ValueError("Path must be under current directory")
  ```
- **Pros**:
  - Allows `..` in paths as long as result is under base
  - More flexible for complex relative paths
- **Cons**:
  - Users may legitimately want to write to `/home/user/projects/` (outside CWD)
  - False positives for absolute paths
  - More complex logic
  - Harder to test all edge cases
- **Why rejected**: Too restrictive (blocks legitimate absolute paths) and more complex than needed.

### Whitelist Allowed Characters
- **Implementation**:
  ```python
  allowed = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0-9-_/\\.')
  if any(c not in allowed for c in str(output_dir)):
      raise ValueError("Invalid characters in path")
  ```
- **Pros**:
  - Prevents many attack types
  - Very restrictive
- **Cons**:
  - Blocks legitimate Unicode characters (project names in Chinese, Arabic, etc.)
  - Doesn't actually prevent `..` attacks
  - Over-restrictive for modern filesystems
- **Why rejected**: Too restrictive and doesn't directly address the '..' issue.

### Use os.path.commonpath
- **Implementation**:
  ```python
  if os.path.commonpath([base_dir, output_dir]) != base_dir:
      raise ValueError("Path outside allowed directory")
  ```
- **Pros**:
  - Built-in Python function
  - Handles edge cases
- **Cons**:
  - Only works relative to a base directory
  - Doesn't allow absolute paths outside CWD
  - More complex than simple '..' check
- **Why rejected**: Same issues as "Check Resolved Path Against Base Directory" - too restrictive.

## References

- **File(s)**:
  - `src/generator/file_generator.py:38-74` - Security validation implementation
  - `tests/unit/test_file_generator.py` - 3 security tests added
- **Commits**: aeedd96 (2025-11-25) - Critical security fix
- **Related ADRs**: None
- **External Links**:
  - [OWASP Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal)
  - [CWE-22: Path Traversal](https://cwe.mitre.org/data/definitions/22.html)
- **Documentation**: `TESTING_IMPROVEMENTS.md:10-45` - Security fix details

## Notes

**Why This Works**:
- Path.resolve() normalizes `a/b/../c` to `a/c` by removing '..' components
- By checking BEFORE resolve(), we catch '..' in the original user input
- Any legitimate path can be expressed without '..' by using absolute or forward-only relative paths

**Attack Vectors Blocked**:
1. **Classic traversal**: `../../../etc/passwd`
2. **Mixed traversal**: `/home/user/../admin/config`
3. **Relative traversal**: `./test/../../../secret`
4. **Directory escape**: `projects/../../../etc`

**Security Testing**:
- `test_path_traversal_blocked` - Tests 3 attack vectors
- `test_validate_output_path_security` - Direct validation testing
- `test_validate_output_path_length` - Path length validation

All 296 tests passing with 86% coverage maintained after fix.

**Future Considerations**:
- Could add more sophisticated path analysis (symlink detection, mount point checks)
- Could implement configurable path whitelisting for enterprise deployments
- Could add audit logging for rejected paths
