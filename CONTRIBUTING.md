# Contributing to DriveGuard

First off, thank you for considering contributing to DriveGuard! 🎉

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)

## Code of Conduct

This project and everyone participating in it is governed by a simple principle: **Be respectful and constructive**.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce**
- **Provide specific examples**
- **Describe the behavior you observed and what you expected**
- **Include screenshots if relevant**
- **Note your environment** (OS, Python version, etc.)

**Template:**
```markdown
**Description:**
Brief description of the bug

**Steps to Reproduce:**
1. Step one
2. Step two
3. ...

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Environment:**
- OS: [e.g., Windows 11, macOS 13]
- Python Version: [e.g., 3.9.7]
- DriveGuard Version: [e.g., 1.9.1]

**Additional Context:**
Any other relevant information
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description** of the suggested enhancement
- **Explain why this enhancement would be useful**
- **List examples** of how it would be used

### Pull Requests

- Fill in the required template
- Follow the coding standards
- Include appropriate test coverage
- Update documentation as needed
- End all files with a newline

## Development Setup

### Prerequisites

- Python 3.7 or higher
- Git
- Google Drive API credentials (for testing)

### Setup Steps

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/driveguard.git
   cd driveguard
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

4. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=driveguard tests/

# Run specific test file
python -m pytest tests/test_backup_manager.py
```

## Pull Request Process

1. **Update documentation** - Ensure README.md and relevant docs are updated
2. **Add tests** - New features should include tests
3. **Update CHANGELOG** - Add entry describing your changes
4. **Follow commit conventions** - Use clear, descriptive commit messages
5. **Request review** - Once ready, request review from maintainers

### Commit Message Guidelines

Format: `type(scope): subject`

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(backup): add incremental backup support
fix(resume): correct state file corruption handling
docs(readme): update installation instructions
test(manager): add tests for multi-threading
```

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters
- Use meaningful variable and function names

### Code Structure

```python
# Good
def download_file(file_id, destination_path):
    """
    Download a file from Google Drive.
    
    Args:
        file_id (str): The Google Drive file ID
        destination_path (str): Local path to save the file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Implementation
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

# Bad
def dl(id, path):
    # Download file
    # ... code ...
```

### Documentation

- All public functions must have docstrings
- Use Google-style docstrings
- Include type hints where applicable
- Comment complex logic

### Example:

```python
from typing import Optional, List, Dict

def process_files(
    files: List[Dict[str, str]], 
    backup_folder_id: str,
    max_workers: Optional[int] = None
) -> Dict[str, int]:
    """
    Process a batch of files for backup.
    
    Args:
        files: List of file dictionaries with 'id' and 'name' keys
        backup_folder_id: Google Drive ID of backup destination folder
        max_workers: Maximum number of concurrent workers. If None, auto-detects
        
    Returns:
        Dictionary with 'success' and 'failed' counts
        
    Raises:
        ValueError: If files list is empty
        HttpError: If API request fails
    """
    if not files:
        raise ValueError("Files list cannot be empty")
    
    # Implementation...
    return {'success': 10, 'failed': 0}
```

## Testing Guidelines

### Test Structure

```python
import pytest
from driveguard import BackupManager

class TestBackupManager:
    """Test suite for BackupManager class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.manager = BackupManager(service=mock_service)
    
    def test_download_file_success(self):
        """Test successful file download."""
        result = self.manager.download_file('file123', '/tmp/test.txt')
        assert result is True
    
    def test_download_file_rate_limit(self):
        """Test handling of rate limit error."""
        # Mock rate limit response
        with pytest.raises(RateLimitError):
            self.manager.download_file('file123', '/tmp/test.txt')
```

### Test Coverage

- Aim for >80% code coverage
- Test both success and failure cases
- Test edge cases and boundary conditions
- Mock external API calls

### Running Specific Tests

```bash
# Test specific file
pytest tests/test_backup_manager.py

# Test specific function
pytest tests/test_backup_manager.py::test_download_file_success

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=driveguard --cov-report=html
```

## Code Review Process

All submissions require review. We use GitHub pull requests for this purpose.

### Review Checklist

- [ ] Code follows project style guidelines
- [ ] Tests pass locally
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] No unnecessary dependencies added
- [ ] Commit messages are clear
- [ ] No conflicts with main branch

## Getting Help

- 💬 [GitHub Discussions](https://github.com/yourusername/driveguard/discussions) - Ask questions
- 🐛 [GitHub Issues](https://github.com/yourusername/driveguard/issues) - Report bugs
- 📧 Email maintainers for private concerns

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- Special thanks in documentation

---

Thank you for contributing to DriveGuard! 🚀
