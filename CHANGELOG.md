# Changelog

All notable changes to ZETA CLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-XX

### Added
- Initial release of ZETA CLI
- Ask → Act → Explain flow with smart clarification
- Teaching mode (`--teach` flag and `zeta teach` command)
- Critic mode (`--critic` flag) for code review
- Core tools: ReadFile, WriteFile, RunCommand, ListFiles
- Learning log (`zeta_log.md`) tracking
- Comprehensive test suite (92 tests, 85% coverage)
- Performance benchmarks
- Usage examples and demos
- CI/CD with GitHub Actions
- Pre-commit hooks for code quality

### Features
- Local-first AI using Ollama and MiniMax M2 model
- Safe file operations with user confirmation
- Plain English explanations for all actions
- Interactive learning sessions
- Code review with scoring (1-10) and suggestions

### Documentation
- Complete README with installation and usage
- Product Requirements Document (PRD.md)
- Project Report (PROJECT_REPORT.md)
- Examples directory with demo scripts

### Testing
- Unit tests for all components
- Integration tests for workflows
- CLI tests for command-line interface
- Error handling tests
- Performance benchmarks

## [1.0.1] - 2025-01-XX

### Fixed
- Fixed syntax error in system prompt (triple quotes escaping issue)
- Package now installs and runs correctly without syntax errors

## [Unreleased]

### Planned
- Support for additional file types
- Enhanced critic mode with more detailed analysis
- Export learning log to different formats
- Plugin system for custom tools
- Web UI option

