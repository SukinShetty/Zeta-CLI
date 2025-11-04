# ZETA CLI Examples

This directory contains example scripts and usage patterns for ZETA.

## Files

- **`basic_usage.py`** - Python comments showing common usage patterns
- **`demo_workflow.sh`** - Bash script demonstrating a typical workflow (Linux/Mac)
- **`demo_workflow.ps1`** - PowerShell script demonstrating a typical workflow (Windows)

## Quick Start Examples

### 1. Simple Task Execution

```bash
zeta run "create a hello world Python script"
```

### 2. Teaching Mode

Learn while ZETA works:

```bash
zeta run "make a calculator" --teach
```

### 3. Critic Mode

Review your code:

```bash
zeta run "create a Python script" --critic
```

### 4. Interactive Teaching Session

Start an interactive learning session:

```bash
zeta teach
```

Then ask questions like:
- "What is a function?"
- "How do I create a class?"
- "Explain loops in Python"

Type `exit` when done.

### 5. View Learning Log

See your learning history:

```bash
zeta log
```

## Real-World Examples

### Create a Simple Webpage

```bash
zeta run "create an HTML page with a title 'My First Page' and a paragraph about coding"
```

### Build a Python Script

```bash
zeta run "create a Python script that reads a CSV file and prints the first 5 rows"
```

### Create a CLI Tool

```bash
zeta run "create a command-line tool that lists all Python files in the current directory" --teach
```

### Review Existing Code

```bash
zeta run "review all my Python files for bugs and style issues" --critic
```

## Running Demo Scripts

### Linux/Mac

```bash
chmod +x examples/demo_workflow.sh
./examples/demo_workflow.sh
```

### Windows (PowerShell)

```powershell
.\examples\demo_workflow.ps1
```

## Tips

1. **Be Specific**: The more details you provide, the better ZETA can help
   - ❌ "make something"
   - ✅ "create a Python script that calculates factorial"

2. **Use Teaching Mode**: Always use `--teach` when learning something new

3. **Review Your Code**: Use `--critic` to get feedback on your code quality

4. **Ask Questions**: In teaching mode, ask "what is X?" or "how does Y work?"

5. **Check Your Log**: Regularly review `zeta log` to see what you've learned

