# ZETA CLI

**ZETA — The most accessible AI terminal agent for learning and building.**

ZETA CLI is a friendly AI terminal agent designed to help you learn coding and build projects. It supports multiple LLM providers (OpenAI, Anthropic, Google Gemini, and local Ollama) and provides an intuitive interface for terminal operations.

## Key Features

- **Multi-Provider Support**: Works with OpenAI, Anthropic Claude, Google Gemini, or local Ollama
- **Smart Clarification**: Detects vague inputs and asks helpful clarifying questions
- **Teaching Mode**: Detailed explanations with definitions for beginners
- **Safe Operations**: Never modifies files without confirmation
- **Learning Log**: Tracks your coding journey automatically
- **Code Review**: Optional critic mode for code quality checks

## Installation

ZETA CLI is published on PyPI. Install it with:

```bash
pip install zeta-cli
```

### Configuration

On first run, ZETA will prompt you to set up your preferred AI provider:

```bash
zeta setup
```

This interactive wizard helps you configure:
- **Google Gemini** (FREE tier available) - Recommended for beginners
- **OpenAI** (GPT-4, GPT-3.5)
- **Anthropic Claude**
- **Ollama** (Local, requires Ollama installed)

## Quick Start

Run ZETA with a task:

```bash
zeta run "create a hello world program"
```

ZETA will:
1. Ask clarifying questions if needed
2. Create the files
3. Explain what was done
4. Offer to teach you how it works

### Examples

```bash
# Basic usage
zeta run "make a to-do app"

# With teaching mode (detailed explanations)
zeta run "create a calculator" --teach

# With code review
zeta run "write a Python script" --critic

# View your learning log
zeta log
```

## Usage

### Commands

- `zeta run "task"` - Execute a task
- `zeta run "task" --teach` - Enable teaching mode
- `zeta run "task" --critic` - Enable code review
- `zeta log` - View learning history
- `zeta setup` - Configure AI provider
- `zeta --help` - Show help

### Teaching Mode

Get detailed explanations of coding concepts:

```bash
zeta run "create a button" --teach
```

ZETA will explain:
- What HTML is ("the skeleton of a webpage")
- How elements work
- Why certain code patterns are used

### Critic Mode

Review code for quality, security, and best practices:

```bash
zeta run "write a function" --critic
```

ZETA provides:
- Code quality scores (1-10)
- Bug detection
- Style suggestions
- Security recommendations

## Requirements

- Python 3.8 or higher
- One of the following:
  - Google Gemini API key (free tier available)
  - OpenAI API key
  - Anthropic API key
  - Ollama installed locally

## Configuration

Configuration is stored in `~/.zeta_config.json`. Run `zeta setup` to configure your provider and API keys.

### Environment Variables

You can also set these environment variables:

```bash
# Provider selection
export ZETA_PROVIDER=google  # or openai, anthropic, ollama

# API keys
export GOOGLE_API_KEY=your_key_here
export OPENAI_API_KEY=your_key_here
export ANTHROPIC_API_KEY=your_key_here

# Model selection (optional)
export ZETA_MODEL=gemini-1.5-flash
```

## Features

### Smart Task Handling

ZETA detects vague requests and asks clarifying questions:

```bash
$ zeta run "make a chatbot"

🤔 I need a bit more information!

What kind of chatbot would you like?
  1. A simple terminal-based chatbot
  2. A web-based chatbot with HTML interface
  3. A Python script chatbot

Choose an option [1]:
```

### Safe File Operations

ZETA never modifies files without confirmation:

```bash
Would you like me to create 'app.py'? [y/n]: y
✓ Successfully created app.py
```

### Learning Log

All interactions are saved to `~/.zeta_log.md`:

```markdown
## 2024-01-15 14:30:22

**Action:** User task: make a to-do app

**Explanation:** Created a simple HTML to-do app with JavaScript...

**Lesson:** HTML provides structure, CSS makes it pretty, and JavaScript makes it interactive.
```

## Troubleshooting

### Command Not Found (Windows)

If `zeta` command is not found on Windows:

```powershell
# Use Python module instead
python -m zeta run "task"
```

### Provider Connection Issues

If you encounter connection errors:

1. Verify your API key is set correctly
2. Check your internet connection (for cloud providers)
3. For Ollama, ensure it's running: `ollama serve`
4. Run `zeta setup` to reconfigure

### Model Not Found

If a model isn't recognized:

1. For Google Gemini, use `gemini-1.5-flash` or `gemini-1.5-pro`
2. For OpenAI, use `gpt-4o-mini` or `gpt-4`
3. For Ollama, ensure the model is pulled: `ollama pull llama3.2`

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and contribution guidelines.

### Running Tests

```bash
# Install development dependencies
pip install -e .[test]

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=zeta --cov-report=term-missing
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Links

- **PyPI Package**: https://pypi.org/project/zeta-cli/
- **GitHub Repository**: https://github.com/SukinShetty/Zeta-CLI
- **Issues**: https://github.com/SukinShetty/Zeta-CLI/issues

## Acknowledgments

Built with:
- [LangChain](https://www.langchain.com/) and [LangGraph](https://github.com/langchain-ai/langgraph)
- [Rich](https://github.com/Textualize/rich) for beautiful terminal output
- [Click](https://click.palletsprojects.com/) for CLI framework

---

**Happy Coding! 🚀**
