# ZETA Test Suite

Comprehensive test suite for ZETA CLI application.

## Running Tests

### Install Test Dependencies

```bash
pip install -r requirements-test.txt
```

Or install with test extras:

```bash
pip install -e .[test]
```

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=zeta --cov-report=html
```

### Run Specific Test Files

```bash
pytest tests/test_tools.py
pytest tests/test_agent.py
pytest tests/test_cli.py
```

### Run Specific Test Classes

```bash
pytest tests/test_tools.py::TestReadFile
```

### Run Specific Tests

```bash
pytest tests/test_tools.py::TestReadFile::test_read_existing_file
```

## Test Structure

- **test_tools.py** - Tests for ZetaTools (read_file, write_file, run_command, list_files)
- **test_logger.py** - Tests for ZetaLogger
- **test_agent.py** - Tests for ZetaAgent
- **test_cli.py** - Tests for CLI commands
- **test_vague_detection.py** - Tests for vague task detection
- **test_integration.py** - Integration tests for full workflows
- **conftest.py** - Pytest fixtures and test utilities

## Test Coverage

The test suite covers:
- All tool functions
- Logger functionality
- Agent initialization and methods
- CLI commands
- Vague task detection
- Error handling
- Integration workflows

## Notes

- LLM calls are mocked to avoid requiring actual Ollama model
- File operations use temporary directories
- User input is mocked for interactive commands
- Tests are designed to run quickly (< 30 seconds total)

