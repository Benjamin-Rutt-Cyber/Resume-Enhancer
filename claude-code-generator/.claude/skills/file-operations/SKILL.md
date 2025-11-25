---
name: file-operations
description: Expert knowledge in cross-platform file and directory operations using Python's pathlib, os, and shutil modules. Use this skill when creating files and directories, handling file permissions, implementing atomic writes, managing file paths across platforms, copying/moving files, or handling file system errors. This skill provides patterns for robust, secure file operations.
allowed-tools: [Read, Write, Bash]
---

# File Operations Skill

Comprehensive knowledge for safe, cross-platform file and directory operations in Python.

## Path Handling with pathlib

### Basic Path Operations

```python
from pathlib import Path

# Create Path objects
path = Path('some/directory')
file_path = Path('file.txt')
absolute_path = Path('/absolute/path')

# Home directory
home = Path.home()  # ~/
config = Path.home() / '.config' / 'myapp'

# Current directory
cwd = Path.cwd()

# Join paths (cross-platform)
full_path = Path('dir') / 'subdir' / 'file.txt'

# Get parts
path = Path('/home/user/project/src/main.py')
path.parent  # /home/user/project/src
path.name    # main.py
path.stem    # main
path.suffix  # .py
path.parts   # ('/', 'home', 'user', 'project', 'src', 'main.py')
```

### Path Queries

```python
path = Path('some/file.txt')

# Existence
path.exists()      # File or directory exists
path.is_file()     # Is a file
path.is_dir()      # Is a directory
path.is_symlink()  # Is a symbolic link

# Absolute vs Relative
path.is_absolute()  # Is absolute path
path.resolve()      # Get absolute path

# Permissions (Unix)
path.is_readable()
path.is_writable()
path.is_executable()
```

### Path Manipulation

```python
path = Path('/home/user/file.txt')

# Resolve to absolute
abs_path = path.resolve()

# Relative to another path
rel_path = path.relative_to('/home')  # user/file.txt

# Change extension
new_path = path.with_suffix('.md')  # /home/user/file.md

# Change name
new_path = path.with_name('other.txt')  # /home/user/other.txt

# Change stem
new_path = path.with_stem('newname')  # /home/user/newname.txt
```

## Directory Operations

### Creating Directories

```python
from pathlib import Path

# Create directory
path = Path('new_directory')
path.mkdir()  # Raises FileExistsError if exists

# Create with parents
path = Path('parent/child/grandchild')
path.mkdir(parents=True)  # Creates all intermediate directories

# Create if doesn't exist
path.mkdir(exist_ok=True)  # No error if already exists

# With permissions (Unix)
path.mkdir(mode=0o755)  # rwxr-xr-x

# Best practice: Create with parents and exist_ok
def create_directory(path: Path) -> Path:
    """Safely create directory."""
    path.mkdir(parents=True, exist_ok=True)
    return path
```

### Listing Directory Contents

```python
# List all items
for item in Path('.').iterdir():
    print(item)

# List only files
for file in Path('.').iterdir():
    if file.is_file():
        print(file)

# List specific pattern
for py_file in Path('.').glob('*.py'):
    print(py_file)

# Recursive glob
for py_file in Path('.').rglob('*.py'):  # ** pattern
    print(py_file)

# Filter with conditions
py_files = [f for f in Path('.').rglob('*.py') if f.is_file()]

# Get sorted list
files = sorted(Path('.').glob('*.txt'))
```

### Deleting Directories

```python
import shutil

# Remove empty directory
Path('empty_dir').rmdir()  # Raises OSError if not empty

# Remove directory and contents
shutil.rmtree('directory_with_contents')

# Safe removal
def remove_directory(path: Path):
    """Safely remove directory."""
    if path.exists() and path.is_dir():
        shutil.rmtree(path)
```

## File Operations

### Reading Files

```python
path = Path('file.txt')

# Read entire file as string
content = path.read_text(encoding='utf-8')

# Read as bytes
data = path.read_bytes()

# Read lines
lines = path.read_text().splitlines()

# Read with context manager
with path.open('r', encoding='utf-8') as f:
    for line in f:
        process(line)

# Read JSON
import json
data = json.loads(path.read_text())

# Read YAML
import yaml
data = yaml.safe_load(path.read_text())
```

### Writing Files

```python
path = Path('file.txt')

# Write text
path.write_text('Hello, World!', encoding='utf-8')

# Write bytes
path.write_bytes(b'Binary data')

# Write with context manager
with path.open('w', encoding='utf-8') as f:
    f.write('Line 1\n')
    f.write('Line 2\n')

# Append to file
with path.open('a', encoding='utf-8') as f:
    f.write('Appended line\n')

# Write JSON
import json
path.write_text(json.dumps(data, indent=2))

# Write YAML
import yaml
path.write_text(yaml.dump(data))
```

### Atomic Writes

```python
from atomicwrites import atomic_write
from pathlib import Path

def write_file_atomic(path: Path, content: str):
    """Write file atomically (prevents corruption)."""
    with atomic_write(str(path), mode='w', overwrite=True) as f:
        f.write(content)

# Manual atomic write
import tempfile
import os

def atomic_write_manual(path: Path, content: str):
    """Atomic write without external library."""
    # Write to temp file
    temp_fd, temp_path = tempfile.mkstemp(dir=path.parent, text=True)
    try:
        with os.fdopen(temp_fd, 'w') as f:
            f.write(content)

        # Atomic rename
        os.replace(temp_path, path)
    except:
        # Clean up temp file on error
        try:
            os.unlink(temp_path)
        except:
            pass
        raise
```

## File Permissions

### Unix Permissions

```python
import os
import stat

path = Path('file.txt')

# Set permissions (Unix only)
if hasattr(os, 'chmod'):
    # Octal notation
    os.chmod(path, 0o644)  # rw-r--r--
    os.chmod(path, 0o755)  # rwxr-xr-x
    os.chmod(path, 0o600)  # rw-------

# Using stat constants
os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)  # 644

# Make executable
def make_executable(path: Path):
    """Add execute permission."""
    if hasattr(os, 'chmod'):
        current = path.stat().st_mode
        os.chmod(path, current | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

# Check permissions
def has_permission(path: Path, mode: str) -> bool:
    """Check if file has permission."""
    st_mode = path.stat().st_mode

    if mode == 'r':
        return bool(st_mode & stat.S_IRUSR)
    elif mode == 'w':
        return bool(st_mode & stat.S_IWUSR)
    elif mode == 'x':
        return bool(st_mode & stat.S_IXUSR)

    return False
```

## Copying and Moving

### Copy Operations

```python
import shutil

# Copy file
shutil.copy2('source.txt', 'dest.txt')  # Preserves metadata

# Copy file (basic)
shutil.copy('source.txt', 'dest.txt')  # Doesn't preserve metadata

# Copy to directory
shutil.copy2('file.txt', 'target_dir/')

# Copy entire directory tree
shutil.copytree('source_dir', 'dest_dir')

# Copy with filter
def ignore_files(dir, files):
    """Ignore certain files during copy."""
    return [f for f in files if f.endswith('.pyc')]

shutil.copytree('source', 'dest', ignore=ignore_files)

# Using pathlib
from pathlib import Path

def copy_file(src: Path, dst: Path):
    """Copy file using pathlib."""
    dst.write_bytes(src.read_bytes())
```

### Move Operations

```python
# Move file
shutil.move('source.txt', 'dest.txt')

# Move directory
shutil.move('source_dir', 'dest_dir')

# Rename (same directory)
Path('old_name.txt').rename('new_name.txt')

# Move with pathlib
src = Path('file.txt')
dst = Path('new_location/file.txt')
dst.parent.mkdir(parents=True, exist_ok=True)
src.rename(dst)
```

## Temporary Files and Directories

### Temporary Files

```python
import tempfile

# Temporary file (auto-deleted)
with tempfile.NamedTemporaryFile(mode='w', delete=True) as temp:
    temp.write('Temporary data')
    temp.flush()
    # Use temp.name for file path
    process_file(temp.name)
# File deleted here

# Temporary file (manual deletion)
temp = tempfile.NamedTemporaryFile(mode='w', delete=False)
try:
    temp.write('Data')
    temp_path = temp.name
    temp.close()
    # Use file
    process_file(temp_path)
finally:
    Path(temp_path).unlink()
```

### Temporary Directories

```python
# Temporary directory (auto-deleted)
with tempfile.TemporaryDirectory() as tmpdir:
    tmppath = Path(tmpdir)
    # Create files in tmppath
    (tmppath / 'file.txt').write_text('content')
# Directory and contents deleted here

# Manual temporary directory
tmpdir = tempfile.mkdtemp()
try:
    # Use directory
    pass
finally:
    import shutil
    shutil.rmtree(tmpdir)
```

## Error Handling

### File Operation Errors

```python
from pathlib import Path

def safe_read_file(path: Path) -> str:
    """Read file with error handling."""
    try:
        return path.read_text(encoding='utf-8')
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {path}")
    except PermissionError:
        raise PermissionError(f"Permission denied: {path}")
    except UnicodeDecodeError as e:
        raise ValueError(f"Invalid encoding in {path}: {e}")
    except Exception as e:
        raise RuntimeError(f"Error reading {path}: {e}")

def safe_write_file(path: Path, content: str):
    """Write file with error handling."""
    try:
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        path.write_text(content, encoding='utf-8')

    except PermissionError:
        raise PermissionError(
            f"Cannot write to {path}. Check permissions."
        )
    except OSError as e:
        if e.errno == 28:  # No space left
            raise OSError(f"No space left on device: {path}")
        raise RuntimeError(f"Error writing {path}: {e}")
```

## Security Considerations

### Path Traversal Prevention

```python
def is_safe_path(base_path: Path, target_path: Path) -> bool:
    """
    Check if target_path is within base_path.

    Prevents directory traversal attacks.
    """
    try:
        base = base_path.resolve()
        target = target_path.resolve()

        # Check if target is relative to base
        target.relative_to(base)
        return True
    except ValueError:
        # target is not relative to base
        return False

def safe_join(base_path: Path, user_provided_path: str) -> Path:
    """
    Safely join paths, preventing traversal.

    Raises:
        SecurityError: If path escapes base directory
    """
    target = base_path / user_provided_path
    target = target.resolve()

    if not is_safe_path(base_path, target):
        raise SecurityError(
            f"Path '{user_provided_path}' attempts to escape base directory"
        )

    return target

# Usage
base = Path('/safe/directory')
try:
    # Safe
    safe_join(base, 'subdir/file.txt')  # OK

    # Unsafe - raises SecurityError
    safe_join(base, '../../../etc/passwd')  # ERROR
except SecurityError as e:
    print(f"Security error: {e}")
```

## Cross-Platform Compatibility

### Path Separators

```python
from pathlib import Path
import os

# Use Path for cross-platform compatibility
path = Path('dir') / 'subdir' / 'file.txt'  # Works on all platforms

# Avoid string concatenation
bad_path = 'dir' + '/' + 'file.txt'  # Breaks on Windows

# If you must use strings
os.path.join('dir', 'subdir', 'file.txt')  # Cross-platform

# Converting between formats
posix_path = path.as_posix()  # Always uses /
```

### Line Endings

```python
# Write with platform line endings
with open('file.txt', 'w') as f:  # Uses \n on Unix, \r\n on Windows
    f.write('Line 1\n')
    f.write('Line 2\n')

# Read and normalize line endings
content = Path('file.txt').read_text()  # Normalizes to \n

# Explicit line ending
with open('file.txt', 'w', newline='\n') as f:  # Always use \n
    f.write('Line 1\n')
```

## Practical Patterns

### Backup Before Modify

```python
def modify_file_with_backup(path: Path, modifier_func):
    """Modify file with automatic backup."""
    backup_path = path.with_suffix(path.suffix + '.backup')

    # Create backup
    shutil.copy2(path, backup_path)

    try:
        # Modify file
        content = path.read_text()
        modified = modifier_func(content)
        path.write_text(modified)

        # Success - remove backup
        backup_path.unlink()

    except Exception as e:
        # Restore from backup
        shutil.copy2(backup_path, path)
        backup_path.unlink()
        raise RuntimeError(f"Error modifying file: {e}")
```

### Directory Structure Creation

```python
def create_project_structure(base_path: Path, structure: dict):
    """
    Create directory structure from nested dict.

    Args:
        base_path: Root directory
        structure: Dict mapping directories to subdirectories/files
                  {'dir1': {'subdir': {}, 'file.txt': 'content'}}
    """
    def create_recursive(path: Path, tree: dict):
        for name, content in tree.items():
            item_path = path / name

            if isinstance(content, dict):
                # It's a directory
                item_path.mkdir(parents=True, exist_ok=True)
                create_recursive(item_path, content)
            elif isinstance(content, str):
                # It's a file with content
                item_path.parent.mkdir(parents=True, exist_ok=True)
                item_path.write_text(content)
            else:
                # Empty file
                item_path.parent.mkdir(parents=True, exist_ok=True)
                item_path.touch()

    create_recursive(base_path, structure)

# Usage
structure = {
    '.claude': {
        'agents': {
            'api-agent.md': 'agent content'
        },
        'skills': {}
    },
    'src': {
        'main.py': 'print("Hello")'
    },
    'README.md': '# Project'
}

create_project_structure(Path('my-project'), structure)
```

### Clean Directory

```python
def clean_directory(path: Path, pattern: str = '*'):
    """Remove all files matching pattern from directory."""
    for item in path.glob(pattern):
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)
```

### File Size Operations

```python
def get_file_size(path: Path) -> int:
    """Get file size in bytes."""
    return path.stat().st_size

def get_directory_size(path: Path) -> int:
    """Get total size of directory and contents."""
    total = 0
    for item in path.rglob('*'):
        if item.is_file():
            total += item.stat().st_size
    return total

def format_size(size_bytes: int) -> str:
    """Format bytes as human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"

# Usage
size = get_file_size(Path('large_file.dat'))
print(f"Size: {format_size(size)}")
```

## Testing File Operations

```python
import pytest
import tempfile
from pathlib import Path

@pytest.fixture
def temp_dir():
    """Provide temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

def test_create_directory(temp_dir):
    """Test directory creation."""
    new_dir = temp_dir / 'test_dir'
    new_dir.mkdir()

    assert new_dir.exists()
    assert new_dir.is_dir()

def test_write_and_read_file(temp_dir):
    """Test file operations."""
    file_path = temp_dir / 'test.txt'
    content = 'Hello, World!'

    # Write
    file_path.write_text(content)

    # Read
    read_content = file_path.read_text()

    assert read_content == content
```

## Best Practices

1. **Always use pathlib for paths**
```python
# Good
path = Path('dir') / 'file.txt'

# Bad
path = 'dir' + '/' + 'file.txt'
```

2. **Use context managers for file operations**
```python
# Good
with path.open('r') as f:
    content = f.read()

# Less ideal (but okay for simple cases)
content = path.read_text()
```

3. **Create parent directories before writing**
```python
# Good
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(content)

# Bad (will fail if parent doesn't exist)
path.write_text(content)
```

4. **Handle file operation errors**
```python
# Good
try:
    content = path.read_text()
except FileNotFoundError:
    # Handle missing file
except PermissionError:
    # Handle permission denied
```

5. **Use atomic writes for critical files**
```python
# Good
atomic_write(path, content)

# Risky (can corrupt file if interrupted)
path.write_text(content)
```

## Quick Reference

**Path Creation:**
- `Path('dir/file.txt')` - Create Path
- `Path.home()` - Home directory
- `Path.cwd()` - Current directory

**Directory Operations:**
- `path.mkdir(parents=True, exist_ok=True)` - Create
- `path.rmdir()` - Remove empty
- `shutil.rmtree(path)` - Remove with contents
- `path.iterdir()` - List contents
- `path.glob('*.py')` - Pattern matching

**File Operations:**
- `path.read_text()` - Read as string
- `path.write_text(content)` - Write string
- `path.read_bytes()` - Read as bytes
- `path.write_bytes(data)` - Write bytes
- `path.unlink()` - Delete file

**Path Info:**
- `path.exists()`, `path.is_file()`, `path.is_dir()`
- `path.stat().st_size` - File size
- `path.parent`, `path.name`, `path.stem`, `path.suffix`

**Copy/Move:**
- `shutil.copy2(src, dst)` - Copy file
- `shutil.copytree(src, dst)` - Copy directory
- `shutil.move(src, dst)` - Move
- `path.rename(new_path)` - Rename

**Permissions (Unix):**
- `os.chmod(path, 0o644)` - Set permissions
- `path.stat().st_mode` - Get permissions
