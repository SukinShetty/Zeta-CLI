# Contributing to ZETA CLI

Thank you for your interest in contributing to ZETA CLI! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear, descriptive title
- Steps to reproduce the bug
- Expected behavior
- Actual behavior
- Your environment (OS, Python version, ZETA version)
- Any relevant error messages or logs

### Suggesting Features

Feature suggestions are welcome! Please open an issue with:
- A clear description of the feature
- Use cases and examples
- Why this feature would be useful

### Pull Requests

1. **Fork the repository** and clone your fork
2. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

3. **Make your changes**:
   - Follow the existing code style
   - Add tests for new features
   - Update documentation as needed
   - Ensure all tests pass

4. **Commit your changes**:
   ```bash
   git commit -m "Description of your changes"
   ```
   Use clear, descriptive commit messages.

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request**:
   - Provide a clear description of your changes
   - Reference any related issues
   - Ensure CI checks pass

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip or uv

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/SukinShetty/Zeta-CLI.git
   cd Zeta-CLI
   ```

2. Install in development mode:
   ```bash
   pip install -e .[test]
   ```

   Or with uv:
   ```bash
   uv pip install -e .[test]
   ```

3. Install pre-commit hooks (optional but recommended):
   ```bash
   pip install pre-commit
   pre-commit install
   ```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=zeta --cov-report=term-missing

# Run specific test file
pytest tests/test_tools.py -v
```

### Code Style

We follow PEP 8 style guidelines. The project uses:
- **black** for code formatting
- **isort** for import sorting
- **flake8** for linting

Run code quality checks:
```bash
# Format code
black zeta.py tests/

# Sort imports
isort zeta.py tests/

# Lint
flake8 zeta.py tests/
```

Or use pre-commit hooks (they run automatically before commits).

### Project Structure

```
zeta_cli/
├── zeta.py          # Main CLI application
├── setup.py         # Package configuration
├── tests/           # Test suite
│   ├── test_tools.py
│   ├── test_agent.py
│   ├── test_cli.py
│   └── ...
├── examples/        # Usage examples
└── scripts/         # Utility scripts
```

## Areas for Contribution

We welcome contributions in these areas:

- **Documentation**: Improve README, add examples, fix typos
- **Testing**: Increase test coverage, add edge cases
- **Features**: New tools, better error handling, UI improvements
- **Performance**: Optimize code, reduce latency
- **Compatibility**: Support for more platforms, Python versions
- **Bug Fixes**: Fix reported issues

## Commit Message Guidelines

Use clear, descriptive commit messages:

- **Feature**: `feat: add support for custom model names`
- **Fix**: `fix: resolve file permission error on Windows`
- **Docs**: `docs: update installation instructions`
- **Test**: `test: add tests for file overwrite logic`
- **Refactor**: `refactor: simplify tool execution flow`

## Questions?

If you have questions, feel free to:
- Open an issue for discussion
- Check existing issues and discussions

Thank you for contributing to ZETA CLI! 🚀

