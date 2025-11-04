#!/usr/bin/env python3
"""
ZETA - The most accessible AI terminal agent for learning and building.
A friendly AI terminal agent for non-technical users.
"""

import os
import json
import subprocess
import re
import uuid
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from rich.table import Table
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

# Initialize Rich console
console = Console()

# Constants
# Use home directory for log file to avoid permission issues
LOG_FILE = Path.home() / ".zeta_log.md"
CONFIG_FILE = Path.home() / ".zeta_config.json"

# LLM Provider Configuration (supports cloud APIs like Gemini, Claude, OpenAI)
# Set via environment variables or config file:
# - ZETA_PROVIDER: "openai", "anthropic", "google", "ollama" (default)
# - OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY for respective providers
# - ZETA_MODEL: model name (default varies by provider)
LLM_PROVIDER = os.getenv("ZETA_PROVIDER", "ollama").lower()


def load_config():
    """Load configuration from file if it exists."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # Set environment variables from config
                for key, value in config.items():
                    if value and key not in os.environ:  # Don't override existing env vars
                        os.environ[key] = str(value)
                return config
        except Exception:
            pass
    return {}


def save_config(config: Dict[str, Any]):
    """Save configuration to file, including API keys."""
    try:
        # Save provider, model, and API keys (needed for persistence)
        full_config = {
            "ZETA_PROVIDER": config.get("ZETA_PROVIDER"),
            "ZETA_MODEL": config.get("ZETA_MODEL"),
            # Save API keys from environment (they're set before calling save_config)
            "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY", ""),
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
            "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY", "")
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(full_config, f, indent=2)
    except Exception:
        pass


def is_configured() -> bool:
    """Check if ZETA is properly configured."""
    # Always try loading config first
    load_config()
    
    provider = os.getenv("ZETA_PROVIDER", "").lower()
    
    if not provider:
        return False
    
    if provider == "ollama":
        # For Ollama, just check if it's available
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    # For cloud providers, check if API key is set
    if provider == "google":
        return bool(os.getenv("GOOGLE_API_KEY"))
    elif provider == "openai":
        return bool(os.getenv("OPENAI_API_KEY"))
    elif provider == "anthropic":
        return bool(os.getenv("ANTHROPIC_API_KEY"))
    
    return False


class AgentState(TypedDict):
    """State for the LangGraph agent."""
    messages: List[Any]


class ZetaTools:
    """Collection of tools available to ZETA."""
    
    # Track confirmed files in current session to avoid repeated prompts
    _confirmed_files = set()
    
    @staticmethod
    @tool
    def read_file(file_path: str) -> str:
        """Read the contents of a file. Returns file content as string."""
        try:
            path = Path(file_path)
            if not path.exists():
                return f"Error: File '{file_path}' does not exist."
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    @staticmethod
    def write_file(file_path: str, content: str, confirm: bool = True) -> str:
        """Write content to a file. Creates parent directories if needed."""
        path = Path(file_path)
        existing = path.exists()
        
        if confirm:
            # If we already confirmed this file in this session, skip confirmation
            if file_path not in ZetaTools._confirmed_files:
                action = "modify" if existing else "create"
                if not Confirm.ask(f"\n[bold yellow]Would you like me to {action} '{file_path}'?[/bold yellow]"):
                    return f"User declined to {action} '{file_path}'"
                # Mark as confirmed
                ZetaTools._confirmed_files.add(file_path)
            # If already confirmed, proceed silently (within same session)
        
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully wrote {len(content)} characters to '{file_path}'"
        except Exception as e:
            return f"Error writing file: {str(e)}"
    
    @staticmethod
    def reset_confirmed_files():
        """Reset confirmed files tracker (call at start of new task)."""
        ZetaTools._confirmed_files.clear()
    
    @staticmethod
    @tool
    def run_command(command: str) -> str:
        """Run a shell command and return its output."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return result.stdout if result.stdout else "Command executed successfully."
            else:
                return f"Error: {result.stderr or 'Command failed'}"
        except subprocess.TimeoutExpired:
            return "Error: Command timed out after 30 seconds."
        except Exception as e:
            return f"Error running command: {str(e)}"
    
    @staticmethod
    @tool
    def list_files(directory: str = ".") -> str:
        """List files and directories in a given path."""
        try:
            path = Path(directory)
            if not path.exists():
                return f"Error: Directory '{directory}' does not exist."
            items = []
            for item in sorted(path.iterdir()):
                if item.is_dir():
                    items.append(f"[DIR] {item.name}/")
                else:
                    items.append(f"[FILE] {item.name}")
            return "\n".join(items) if items else "Directory is empty."
        except Exception as e:
            return f"Error listing directory: {str(e)}"


class ZetaLogger:
    """Handles logging to zeta_log.md."""
    
    @staticmethod
    def init_log():
        """Initialize log file if it doesn't exist."""
        global LOG_FILE
        log_path = Path(LOG_FILE)
        try:
            if not log_path.exists():
                # Ensure parent directory exists
                log_path.parent.mkdir(parents=True, exist_ok=True)
                with open(log_path, 'w', encoding='utf-8') as f:
                    f.write("# ZETA Learning Log\n\n")
                    f.write("Welcome to ZETA! This log tracks your coding journey.\n\n")
                    f.write("---\n\n")
        except (PermissionError, IOError) as e:
            # If can't write to home directory, try current directory
            try:
                alt_log = Path("zeta_log.md")
                if not alt_log.exists():
                    with open(alt_log, 'w', encoding='utf-8') as f:
                        f.write("# ZETA Learning Log\n\n")
                        f.write("Welcome to ZETA! This log tracks your coding journey.\n\n")
                        f.write("---\n\n")
                # Update LOG_FILE to use alternative
                LOG_FILE = alt_log
            except:
                # If both fail, logging is disabled - continue without it
                pass
    
    @staticmethod
    def log(action: str, explanation: str, lesson: Optional[str] = None):
        """Log an action and explanation."""
        try:
            ZetaLogger.init_log()
            log_path = Path(LOG_FILE)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f"## {timestamp}\n\n")
                f.write(f"**Action:** {action}\n\n")
                f.write(f"**Explanation:** {explanation}\n\n")
                if lesson:
                    f.write(f"**Lesson:** {lesson}\n\n")
                f.write("---\n\n")
        except (PermissionError, IOError):
            # If logging fails, just continue - don't break the app
            pass
    
    @staticmethod
    def show_log():
        """Display the log file."""
        global LOG_FILE
        log_path = Path(LOG_FILE)
        # Try home directory first, then current directory
        if not log_path.exists():
            alt_log = Path("zeta_log.md")
            if alt_log.exists():
                log_path = alt_log
            else:
                console.print("[yellow]No log entries yet. Start using ZETA to see your learning journey![/yellow]")
                return
        
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                content = f.read()
            console.print(Markdown(content))
        except (PermissionError, IOError) as e:
            console.print(f"[yellow]Could not read log file: {e}[/yellow]")


class ZetaAgent:
    """Main agent that handles conversations and actions."""
    
    def __init__(self, teach_mode: bool = False, critic_mode: bool = False):
        self.teach_mode = teach_mode
        self.critic_mode = critic_mode
        self.llm = self._create_llm()
        self.tools = [
            ZetaTools.read_file,
            ZetaTools.write_file,
            ZetaTools.run_command,
            ZetaTools.list_files
        ]
        self.setup_agent()
    
    def _create_llm(self):
        """Create LLM instance based on configured provider."""
        # Load config from file first
        load_config()
        
        # Read provider at runtime, not import time
        provider = os.getenv("ZETA_PROVIDER", "ollama").lower()
        model_name = os.getenv("ZETA_MODEL", "")
        
        if provider == "openai":
            try:
                from langchain_openai import ChatOpenAI
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    console.print("[red]Error: OPENAI_API_KEY not set. Set it with:[/red]")
                    console.print("[yellow]  $env:OPENAI_API_KEY='your-key-here'[/yellow]")
                    raise ValueError("OPENAI_API_KEY not found")
                return ChatOpenAI(
                    model=model_name or "gpt-4o-mini",
                    temperature=0.7,
                    api_key=api_key
                )
            except ImportError:
                console.print("[red]Error: langchain-openai not installed.[/red]")
                console.print("[yellow]Install with: pip install langchain-openai[/yellow]")
                raise
        
        elif provider == "anthropic":
            try:
                from langchain_anthropic import ChatAnthropic
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    console.print("[red]Error: ANTHROPIC_API_KEY not set.[/red]")
                    console.print("[yellow]  $env:ANTHROPIC_API_KEY='your-key-here'[/yellow]")
                    raise ValueError("ANTHROPIC_API_KEY not found")
                return ChatAnthropic(
                    model=model_name or "claude-3-5-sonnet-20241022",
                    temperature=0.7,
                    api_key=api_key
                )
            except ImportError:
                console.print("[red]Error: langchain-anthropic not installed.[/red]")
                console.print("[yellow]Install with: pip install langchain-anthropic[/yellow]")
                raise
        
        elif provider == "google":
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                api_key = os.getenv("GOOGLE_API_KEY")
                if not api_key:
                    console.print("[red]Error: GOOGLE_API_KEY not set.[/red]")
                    console.print("[yellow]Run: zeta setup[/yellow]")
                    raise ValueError("GOOGLE_API_KEY not found")
                
                # Use correct Google Gemini model names for Google AI Studio API
                # Valid models WITHOUT -latest suffix: gemini-1.5-flash, gemini-1.5-pro
                models_to_try = []
                if model_name:
                    # Remove -latest suffix if present (not valid in API)
                    clean_name = model_name.replace("-latest", "")
                    models_to_try.append(clean_name)
                
                # Add valid model names in order of preference (NO -latest suffix)
                valid_models = [
                    "gemini-1.5-flash",  # Fastest, free tier - NO -latest suffix
                    "gemini-1.5-pro",    # More capable - NO -latest suffix
                    "gemini-pro"         # Legacy fallback
                ]
                
                # Add valid models if not already in list
                for valid_model in valid_models:
                    if valid_model not in models_to_try:
                        models_to_try.append(valid_model)
                
                # Try each model - create instance
                for model in models_to_try:
                    try:
                        llm = ChatGoogleGenerativeAI(
                            model=model,
                            temperature=0.7,
                            google_api_key=api_key
                        )
                        # Return first successful instance creation
                        return llm
                    except Exception:
                        # Continue to next model if this one fails
                        continue
                
                # Final fallback - use gemini-1.5-flash (NO -latest suffix)
                return ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash",
                    temperature=0.7,
                    google_api_key=api_key
                )
            except ImportError:
                console.print("[red]Error: langchain-google-genai not installed.[/red]")
                console.print("[yellow]Run: pip install langchain-google-genai[/yellow]")
                raise
        
        else:  # Default: Ollama (local)
            try:
                from langchain_ollama import OllamaLLM
                model = model_name or os.getenv("ZETA_MODEL", "llama3.2:latest")
                return OllamaLLM(
                    model=model,
                    temperature=0.7,
                    timeout=120.0,
                    base_url="http://localhost:11434"
                )
            except ImportError:
                console.print("[red]Error: langchain-ollama not installed.[/red]")
                console.print("[yellow]Install with: pip install langchain-ollama[/yellow]")
                raise
    
    def setup_agent(self):
        """Set up the LangGraph agent."""
        def agent_node(state: AgentState):
            messages = state["messages"]
            
            # Build system prompt
            system_prompt = self._build_system_prompt()
            
            # Add system message
            full_messages = [SystemMessage(content=system_prompt)] + messages
            
            # Get response from LLM
            response = self.llm.invoke(full_messages)
            
            return {"messages": [AIMessage(content=response.content if hasattr(response, 'content') else str(response))]}
        
        # Create graph
        workflow = StateGraph(AgentState)
        workflow.add_node("agent", agent_node)
        workflow.set_entry_point("agent")
        workflow.add_edge("agent", END)
        
        self.graph = workflow.compile()
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt based on mode."""
        base_prompt = """You are ZETA, the most accessible AI terminal agent for learning and building. A friendly AI terminal agent designed for non-technical users.

Your personality:
- Patient, encouraging, and educational
- Never use jargon without explaining it
- Always explain what you're doing in plain English
- Ask clarifying questions when tasks are vague
- End responses with questions to encourage learning

Available tools (call them using TOOL_CALL format):
- read_file(file_path="path/to/file"): Read a file
- write_file(file_path="path/to/file", content="file content"): Write/create a file
- run_command(command="shell command"): Execute shell commands
- list_files(directory="path/to/dir"): List directory contents

When you need to use a tool, format it exactly like this:
TOOL_CALL: tool_name(param1="value1", param2="value2")

For multiline content (like file content), use triple quotes:
TOOL_CALL: write_file(file_path="app.py", content=\"""multiline
content
here\""")

Important rules:
1. ALWAYS ACT - use tools to create files, run commands, etc. Do NOT ask questions unless the task is completely unclear.
2. If the user wants something created, CREATE IT IMMEDIATELY using tools. Do not ask "what should I create?" - just create it.
3. After every action, explain what was done in simple terms
4. If in teaching mode, provide detailed explanations with definitions
5. Use friendly, encouraging language like "Great choice!", "Nice!", "Let's do this!"
6. If you need to create or modify files, use the write_file tool. The system will ask for confirmation automatically.
7. CRITICAL: When user asks to create something, CREATE IT. Do not ask more questions - just create files and execute commands.
"""
        
        if self.teach_mode:
            base_prompt += """
TEACHING MODE ENABLED:
- Provide detailed explanations for every concept
- Define technical terms (e.g., "HTML is the skeleton of a webpage")
- Break down complex ideas into simple steps
- Use analogies when helpful
"""
        
        if self.critic_mode:
            base_prompt += """
CRITIC MODE ENABLED:
- Review all code for bugs, style, and security
- Provide a score from 1-10
- Suggest fixes if score is below 8
- Explain each issue clearly
"""
        
        return base_prompt
    
    def ask_clarifying_question(self, vague_task: str) -> Optional[str]:
        """Detect vague tasks and ask clarifying questions."""
        prompt = f"""The user said: "{vague_task}"

This task is vague. Generate 3-5 numbered options to clarify what they want.
Format: Return ONLY a JSON object with this structure:
{{
    "question": "What kind of [thing] would you like?",
    "options": [
        "Option 1 description",
        "Option 2 description",
        "Option 3 description"
    ]
}}

Return ONLY the JSON, no other text."""
        
        try:
            response = self.llm.invoke(prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Try to extract JSON
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                data = json.loads(json_str)
                return data
        except Exception as e:
            console.print(f"[red]Error generating clarifying question: {e}[/red]")
        
        return None
    
    def explain_action(self, action: str, result: str, teach_mode: bool = False) -> str:
        """Generate an explanation for an action."""
        prompt = f"""The following action was performed:
Action: {action}
Result: {result}

Generate a friendly, plain English explanation of what happened.
{"Include detailed explanations and definitions if this is teaching mode." if teach_mode else "Keep it concise but informative."}
Use encouraging language. End with a question to encourage learning."""
        
        try:
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception:
            return f"Completed: {action}. {result}"
    
    def critic_review(self, code: str, file_path: str) -> Dict[str, Any]:
        """Review code using critic mode."""
        # Determine language from file extension
        ext = Path(file_path).suffix
        lang_map = {'.py': 'python', '.js': 'javascript', '.html': 'html', 
                   '.css': 'css', '.ts': 'typescript', '.jsx': 'javascript', '.tsx': 'typescript'}
        lang = lang_map.get(ext, 'code')
        
        prompt = f"""Review this {lang} code from '{file_path}':

```{lang}
{code}
```

Provide a JSON response with:
{{
    "score": <1-10>,
    "issues": ["issue1", "issue2"],
    "suggestions": ["suggestion1", "suggestion2"],
    "explanation": "Overall assessment"
}}

Return ONLY the JSON."""
        
        try:
            response = self.llm.invoke(prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
        except Exception as e:
            console.print(f"[yellow]Critic review failed: {e}[/yellow]")
        
        return {"score": 5, "issues": [], "suggestions": [], "explanation": "Could not complete review."}
    
    def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Execute a tool and return the result."""
        if tool_name == "read_file":
            # read_file is decorated with @tool, access underlying function via func attribute
            return ZetaTools.read_file.func(args.get("file_path", ""))
        elif tool_name == "write_file":
            return ZetaTools.write_file(
                args.get("file_path", ""),
                args.get("content", ""),
                confirm=True
            )
        elif tool_name == "run_command":
            # run_command is decorated with @tool
            return ZetaTools.run_command.func(args.get("command", ""))
        elif tool_name == "list_files":
            # list_files is decorated with @tool
            return ZetaTools.list_files.func(args.get("directory", "."))
        else:
            return f"Unknown tool: {tool_name}"
    
    def parse_tool_calls(self, response: str) -> List[Dict[str, Any]]:
        """Parse tool calls from LLM response."""
        tool_calls = []
        
        # Look for patterns like: TOOL_CALL: tool_name(...)
        # Handle multiline content with triple quotes
        pattern = r'TOOL_CALL:\s*(\w+)\s*\((.*?)\)'
        matches = list(re.finditer(pattern, response, re.DOTALL))
        
        for match in matches:
            tool_name = match.group(1)
            args_str = match.group(2).strip()
            
            # Parse arguments
            args = {}
            
            # Handle triple-quoted strings (multiline content)
            if '"""' in args_str or "'''" in args_str:
                # Find content parameter with triple quotes
                content_match = re.search(r'content=(?:"(?:""")|(?:\'\'\'))(.*?)(?:"""|\'\'\')', args_str, re.DOTALL)
                if content_match:
                    args['content'] = content_match.group(1)
                    # Remove content from args_str for other parsing
                    args_str = re.sub(r'content=(?:""".*?"""|\'\'\'.*?\'\'\')', '', args_str, flags=re.DOTALL)
            
            # Parse simple quoted arguments
            arg_pattern = r'(\w+)=["\']([^"\']*)["\']'
            for arg_match in re.finditer(arg_pattern, args_str):
                key = arg_match.group(1)
                value = arg_match.group(2)
                if key not in args:  # Don't overwrite multiline content
                    args[key] = value
            
            # Handle unquoted arguments (for directory="." type cases)
            simple_pattern = r'(\w+)=([^,)]+)'
            for arg_match in re.finditer(simple_pattern, args_str):
                key = arg_match.group(1).strip()
                value = arg_match.group(2).strip().strip('"\'')
                if key not in args:
                    args[key] = value
            
            if args:
                tool_calls.append({"tool": tool_name, "args": args})
        
        return tool_calls
    
    def process_task(self, task: str, max_iterations: int = 5) -> str:
        """Process a task using the agent with tool execution."""
        try:
            messages = [HumanMessage(content=task)]
            system_prompt = self._build_system_prompt()
            
            for iteration in range(max_iterations):
                # Get response from LLM
                full_messages = [SystemMessage(content=system_prompt)] + messages
                response = self.llm.invoke(full_messages)
                response_text = response.content if hasattr(response, 'content') else str(response)
                
                # Check for tool calls
                tool_calls = self.parse_tool_calls(response_text)
                
                if not tool_calls:
                    # No tool calls - check if LLM is asking about conflicts
                    # If so, tell it to just create/overwrite automatically
                    if "?" in response_text.lower() and ("file" in response_text.lower() or "conflict" in response_text.lower() or "overwrite" in response_text.lower() or "existing" in response_text.lower()):
                        # LLM is asking about file conflicts - force it to create
                        messages.append(AIMessage(content=response_text))
                        messages.append(HumanMessage(content="Just create the file. If it exists, overwrite it automatically. The system handles confirmation. Use write_file tool now. Do not ask questions - just create."))
                        continue  # Continue to force tool execution
                    
                    # No tool calls and no conflicts - return response
                    return response_text
                
                # Execute tools
                tool_results = []
                for tool_call in tool_calls:
                    tool_name = tool_call["tool"]
                    args = tool_call["args"]
                    
                    console.print(f"[dim]Executing: {tool_name}({', '.join(f'{k}={v[:20]}...' if len(str(v)) > 20 else f'{k}={v}' for k, v in args.items())})[/dim]")
                    
                    result = self.execute_tool(tool_name, args)
                    tool_results.append(f"{tool_name} result: {result}")
                
                # Add tool results to conversation
                messages.append(AIMessage(content=response_text))
                messages.append(HumanMessage(content="Tool results:\n" + "\n".join(tool_results)))
            
            # If we've done max iterations, return last response
            return response_text if 'response_text' in locals() else "I'm not sure how to help with that. Could you be more specific?"
            
        except Exception as e:
            error_msg = str(e)
            # Provide helpful error messages
            if "404" in error_msg or "not found" in error_msg.lower():
                return f"I encountered an error: The model might not be available. Try running `zeta setup` to configure a different model, or check your API key."
            elif "429" in error_msg or "quota" in error_msg.lower():
                return f"I encountered an error: API quota exceeded. Try running `zeta setup` to switch to a different provider (like Google Gemini with free tier)."
            elif "10061" in error_msg or "connection refused" in error_msg.lower():
                return f"I encountered an error: Cannot connect to Ollama server. Please start Ollama or run `zeta setup` to use a cloud API instead."
            else:
                return f"I encountered an error: {error_msg}. Try running `zeta setup` to reconfigure, or rephrasing your request."


def detect_vague_task(task: str) -> bool:
    """Detect if a task is too vague."""
    vague_keywords = ["make", "create", "build", "make a", "create a", "build a"]
    task_lower = task.lower()
    
    # Check if task is very short or contains vague keywords without specifics
    if len(task.split()) < 4:
        return True
    
    for keyword in vague_keywords:
        if keyword in task_lower:
            # Check if there's more detail after the keyword
            parts = task_lower.split(keyword, 1)
            if len(parts) > 1 and len(parts[1].strip().split()) < 3:
                return True
    
    return False


def show_welcome():
    """Display welcome message like Kimi CLI."""
    # Load config first
    load_config()
    
    # Get current directory
    current_dir = str(Path.cwd())
    
    # Generate session ID
    session_id = str(uuid.uuid4())
    
    # Get model/provider info - read at runtime
    provider = os.getenv("ZETA_PROVIDER", "ollama").lower()
    model_name = os.getenv("ZETA_MODEL", "")
    
    if provider == "ollama":
        model_status = f"[yellow]Ollama (local)[/yellow]"
        if model_name:
            model_status += f" - {model_name}"
        model_status += f"\n[dim]Send `zeta setup` to configure cloud APIs for faster responses[/dim]"
    elif provider == "openai":
        model_status = f"[green]OpenAI[/green] - {model_name or 'gpt-4o-mini'}"
    elif provider == "anthropic":
        model_status = f"[green]Anthropic Claude[/green] - {model_name or 'claude-3-5-sonnet-20241022'}"
    elif provider == "google":
        model_status = f"[green]Google Gemini[/green] - {model_name or 'gemini-1.5-flash'}"
    else:
        model_status = f"[yellow]not set[/yellow], send `zeta setup` to configure"
    
    # Welcome panel with tagline next to welcome message
    welcome_text = f"""[bold cyan]Welcome to ZETA CLI![/bold cyan] [dim]— The most accessible AI terminal agent for learning and building.[/dim]

Send `zeta --help` for help information.

[dim]Directory:[/dim] `{current_dir}`
[dim]Session:[/dim] `{session_id}`
[dim]Model:[/dim] {model_status}"""
    
    # Create panel
    console.print(Panel(
        welcome_text,
        border_style="cyan",
        padding=(1, 2),
        title="[bold cyan]ZETA[/bold cyan]"
    ))


@click.group()
@click.version_option(version="1.0.6")
def cli():
    """ZETA - The most accessible AI terminal agent for learning and building.
    
    A friendly AI terminal agent for non-technical users.
    
    Supports multiple LLM providers:
    - OpenAI (set OPENAI_API_KEY and ZETA_PROVIDER=openai)
    - Anthropic/Claude (set ANTHROPIC_API_KEY and ZETA_PROVIDER=anthropic)
    - Google/Gemini (set GOOGLE_API_KEY and ZETA_PROVIDER=google)
    - Ollama/Local (default, requires Ollama running)
    """
    pass


@cli.command()
@click.argument('task', required=False)
@click.option('--teach', is_flag=True, help='Enable teaching mode with detailed explanations')
@click.option('--critic', is_flag=True, help='Enable critic mode for code review')
def run(task: Optional[str], teach: bool, critic: bool):
    """Run ZETA with a task. If no task provided, starts interactive mode."""
    # Load configuration from file
    load_config()
    
    # Check if configured (like Kimi CLI's /setup prompt)
    if not is_configured():
        console.print("\n[yellow]⚠ ZETA is not configured yet![/yellow]")
        console.print("[cyan]Let's set it up quickly...[/cyan]\n")
        
        if Confirm.ask("[bold]Would you like to run setup now?[/bold]", default=True):
            # Call setup function directly
            _run_setup()
            # Reload config after setup
            load_config()
        else:
            console.print("\n[yellow]You can run 'zeta setup' later to configure ZETA.[/yellow]")
            console.print("[yellow]For now, ZETA will try to use Ollama (local).[/yellow]\n")
    
    show_welcome()
    
    if not task:
        task = Prompt.ask("\n[bold]What would you like to do?[/bold]")
    
    try:
        agent = ZetaAgent(teach_mode=teach, critic_mode=critic)
    except Exception as e:
        error_msg = str(e)
        if "not configured" in error_msg.lower() or "not set" in error_msg.lower():
            console.print("\n[red]Configuration Error[/red]")
            console.print("[yellow]Please run 'zeta setup' to configure ZETA.[/yellow]\n")
            return
        else:
            raise
    
    # Check if task is vague
    if detect_vague_task(task):
        console.print("\n[yellow]🤔[/yellow] [bold]I need a bit more information![/bold]\n")
        
        clarification = agent.ask_clarifying_question(task)
        if clarification:
            console.print(f"[bold]{clarification['question']}[/bold]\n")
            for i, option in enumerate(clarification['options'], 1):
                console.print(f"  [cyan]{i}.[/cyan] {option}")
            
            choice = Prompt.ask("\n[bold]Choose an option[/bold]", default="1")
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(clarification['options']):
                    task = clarification['options'][idx]
                    console.print(f"\n[green]Great choice![/green] Let's create: {task.lower()}.\n")
                else:
                    console.print("[yellow]Invalid choice. Using default option.[/yellow]")
            except ValueError:
                console.print("[yellow]Invalid input. Continuing with original task.[/yellow]")
    
    # Reset confirmed files for this new task (fresh start)
    ZetaTools.reset_confirmed_files()
    
    # Process the task
    console.print("\n[dim]Processing your request...[/dim]\n")
    
    # After clarification, make task explicitly action-oriented
    # Add instruction to ACT, not ask questions
    if "create" in task.lower() or "make" in task.lower() or "build" in task.lower():
        task = f"{task}. IMPORTANT: Use tools to create files or execute commands immediately. Do NOT ask questions - just create it."
    
    response = agent.process_task(task)
    
    # Check if response is just questions (not actual creation)
    question_keywords = ["what", "how", "would you", "could you", "which", "do you want", "should i"]
    has_questions = any(keyword in response.lower() for keyword in question_keywords) and "?" in response
    
    if has_questions and not any(keyword in response.lower() for keyword in ["created", "wrote", "executed", "made", "file", "tool"]):
        # LLM is asking questions instead of acting - force it to create
        console.print("[yellow]Creating that for you now...[/yellow]\n")
        task_with_action = f"Create {task.lower()} RIGHT NOW. Use write_file or run_command tools immediately. Do NOT ask any questions - just create files and execute commands."
        response = agent.process_task(task_with_action)
    
    # Display response
    console.print(Panel(Markdown(response), title="ZETA", border_style="cyan"))
    
    # If critic mode is enabled, review any created code files
    if critic:
        code_extensions = ['.py', '.js', '.html', '.css', '.ts', '.jsx', '.tsx']
        code_files = []
        for ext in code_extensions:
            code_files.extend(Path(".").glob(f"*{ext}"))
        
        if code_files:
            console.print("\n[bold yellow]🔍 Critic Mode: Reviewing code...[/bold yellow]\n")
            for code_file in code_files:
                try:
                    code = code_file.read_text(encoding='utf-8')
                    review = agent.critic_review(code, str(code_file))
                    
                    score = review.get("score", 5)
                    color = "green" if score >= 8 else "yellow" if score >= 6 else "red"
                    
                    console.print(f"\n[bold]{code_file.name}[/bold] - Score: [{color}]{score}/10[/{color}]")
                    console.print(f"[dim]{review.get('explanation', 'No explanation')}[/dim]")
                    
                    if score < 8:
                        issues = review.get("issues", [])
                        suggestions = review.get("suggestions", [])
                        if issues:
                            console.print("\n[bold red]Issues:[/bold red]")
                            for issue in issues:
                                console.print(f"  • {issue}")
                        if suggestions:
                            console.print("\n[bold green]Suggestions:[/bold green]")
                            for suggestion in suggestions:
                                console.print(f"  • {suggestion}")
                except Exception as e:
                    console.print(f"[yellow]Could not review {code_file}: {e}[/yellow]")
    
    # Check if task was actually completed successfully
    # Only ask "Would you like to learn?" if task was completed without errors
    response_lower = response.lower()
    
    # Check for error/problem indicators - don't ask "learn?" if ZETA is having problems
    error_indicators = ["trouble", "problem", "error", "failed", "can't", "cannot", "unable", "still having", "looks like", "having trouble"]
    has_errors = any(indicator in response_lower for indicator in error_indicators)
    
    # Check if response indicates successful creation
    creation_keywords = ["created", "wrote", "successfully", "completed", "done", "finished", "ready"]
    has_creation = any(keyword in response_lower for keyword in creation_keywords)
    
    # Check if files were actually created (look for file mentions and verify they exist)
    import re
    file_mentions = re.findall(r'[\w\-_]+\.(?:py|js|html|css|txt|json|md|ts|jsx|tsx)', response, re.IGNORECASE)
    files_exist = False
    if file_mentions:
        # Check if any mentioned files actually exist
        for file_name in file_mentions[:5]:  # Check first 5 files mentioned
            if Path(file_name).exists():
                files_exist = True
                break
    
    # Only ask about learning if task was completed successfully AND no errors/problems mentioned
    if (has_creation or files_exist) and not has_errors:
        # Log the interaction
        explanation = agent.explain_action("Task execution", response, teach_mode=teach)
        ZetaLogger.log(f"User task: {task}", explanation)
        
        # Ask if user wants to learn more (only after successful completion)
        console.print()  # Add spacing
        if Confirm.ask("[bold]Would you like to learn how this works?[/bold]", default=False):
            lesson_prompt = f"Explain how '{task}' works in simple terms suitable for beginners."
            lesson = agent.process_task(lesson_prompt)
            console.print(Panel(Markdown(lesson), title="Lesson", border_style="green"))
            ZetaLogger.log("Learning session", lesson, lesson=lesson)
    else:
        # Task might not be complete - just log without asking about learning
        explanation = agent.explain_action("Task execution", response, teach_mode=teach)
        ZetaLogger.log(f"User task: {task}", explanation)


def _run_setup():
    """Internal setup function (called by both CLI command and auto-setup)."""
    # Load existing config first
    load_config()
    
    console.print("\n[bold cyan]ZETA Setup Wizard[/bold cyan]\n")
    console.print("Let's configure ZETA to work with your preferred AI provider.\n")
    
    # Choose provider
    console.print("[bold]Choose your AI provider:[/bold]")
    console.print("  1. Google Gemini (FREE tier available) [cyan]Recommended[/cyan]")
    console.print("  2. OpenAI (GPT-4, GPT-3.5)")
    console.print("  3. Anthropic Claude")
    console.print("  4. Ollama (Local, requires Ollama installed)")
    
    choice = Prompt.ask("\n[bold]Enter choice (1-4)[/bold]", default="1")
    
    if choice == "1":
        # Google Gemini setup
        console.print("\n[bold]Setting up Google Gemini...[/bold]")
        console.print("Get your FREE API key: https://makersuite.google.com/app/apikey\n")
        
        api_key = Prompt.ask("[bold]Enter your Google API key[/bold]")
        if api_key:
            # Set environment variables
            os.environ["ZETA_PROVIDER"] = "google"
            os.environ["GOOGLE_API_KEY"] = api_key
            os.environ["ZETA_MODEL"] = "gemini-1.5-flash"  # Use valid model name (NO -latest suffix)
            
            config = {
                "ZETA_PROVIDER": "google",
                "ZETA_MODEL": "gemini-1.5-flash"
            }
            save_config(config)
            
            console.print("\n[green]✓ Configuration saved![/green]")
            
            # Check if package is installed
            try:
                import langchain_google_genai
                console.print("[green]✓ Google Gemini support is installed![/green]")
            except ImportError:
                console.print("\n[yellow]⚠ Installing Google Gemini support...[/yellow]")
                import subprocess
                result = subprocess.run(["pip", "install", "langchain-google-genai"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    console.print("[green]✓ Installation complete![/green]")
                else:
                    console.print("[yellow]⚠ Installation had issues. You may need to install manually:[/yellow]")
                    console.print("[yellow]  pip install langchain-google-genai[/yellow]")
    
    elif choice == "2":
        # OpenAI setup
        console.print("\n[bold]Setting up OpenAI...[/bold]")
        console.print("Get your API key: https://platform.openai.com/api-keys\n")
        
        api_key = Prompt.ask("[bold]Enter your OpenAI API key[/bold]")
        if api_key:
            os.environ["ZETA_PROVIDER"] = "openai"
            os.environ["OPENAI_API_KEY"] = api_key
            os.environ["ZETA_MODEL"] = "gpt-4o-mini"
            
            config = {
                "ZETA_PROVIDER": "openai",
                "ZETA_MODEL": "gpt-4o-mini"
            }
            save_config(config)
            
            console.print("\n[green]✓ Configuration saved![/green]")
            
            try:
                import langchain_openai
                console.print("[green]✓ OpenAI support is installed![/green]")
            except ImportError:
                console.print("\n[yellow]⚠ Installing OpenAI support...[/yellow]")
                import subprocess
                result = subprocess.run(["pip", "install", "langchain-openai"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    console.print("[green]✓ Installation complete![/green]")
                else:
                    console.print("[yellow]⚠ Installation had issues. You may need to install manually:[/yellow]")
                    console.print("[yellow]  pip install langchain-openai[/yellow]")
    
    elif choice == "3":
        # Anthropic setup
        console.print("\n[bold]Setting up Anthropic Claude...[/bold]")
        console.print("Get your API key: https://console.anthropic.com/\n")
        
        api_key = Prompt.ask("[bold]Enter your Anthropic API key[/bold]")
        if api_key:
            os.environ["ZETA_PROVIDER"] = "anthropic"
            os.environ["ANTHROPIC_API_KEY"] = api_key
            os.environ["ZETA_MODEL"] = "claude-3-haiku-20240307"
            
            config = {
                "ZETA_PROVIDER": "anthropic",
                "ZETA_MODEL": "claude-3-haiku-20240307"
            }
            save_config(config)
            
            console.print("\n[green]✓ Configuration saved![/green]")
            
            try:
                import langchain_anthropic
                console.print("[green]✓ Anthropic support is installed![/green]")
            except ImportError:
                console.print("\n[yellow]⚠ Installing Anthropic support...[/yellow]")
                import subprocess
                result = subprocess.run(["pip", "install", "langchain-anthropic"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    console.print("[green]✓ Installation complete![/green]")
                else:
                    console.print("[yellow]⚠ Installation had issues. You may need to install manually:[/yellow]")
                    console.print("[yellow]  pip install langchain-anthropic[/yellow]")
    
    elif choice == "4":
        # Ollama setup
        console.print("\n[bold]Setting up Ollama (Local)...[/bold]")
        console.print("Make sure Ollama is installed and running.\n")
        
        model = Prompt.ask("[bold]Enter model name[/bold]", default="llama3.2:latest")
        os.environ["ZETA_PROVIDER"] = "ollama"
        os.environ["ZETA_MODEL"] = model
        
        config = {
            "ZETA_PROVIDER": "ollama",
            "ZETA_MODEL": model
        }
        save_config(config)
        
        console.print("\n[green]✓ Configuration saved![/green]")
        console.print("\n[yellow]Note:[/yellow] Make sure Ollama is running before using ZETA!")
        console.print("[yellow]To start Ollama:[/yellow] Just run 'ollama' or start it from Start Menu")
    
    console.print("\n[bold green]✓ Setup complete! Try: zeta run \"say hello\"[/bold green]\n")


@cli.command()
def setup():
    """Interactive setup wizard to configure ZETA with any provider."""
    _run_setup()


@cli.command()
def teach():
    """Start an interactive teaching session."""
    console.print(Panel.fit(
        "[bold green]📚 Teaching Mode[/bold green]\n"
        "[dim]Learn coding concepts in detail[/dim]",
        border_style="green"
    ))
    
    agent = ZetaAgent(teach_mode=True)
    
    console.print("\n[bold]What would you like to learn about?[/bold]")
    console.print("[dim]Type 'exit' to end the session[/dim]\n")
    
    while True:
        topic = Prompt.ask("[bold cyan]You[/bold cyan]")
        if topic.lower() in ['exit', 'quit', 'q']:
            console.print("\n[green]Great learning session! Keep coding! 🚀[/green]")
            break
        
        response = agent.process_task(f"Explain '{topic}' in detail with definitions and examples for beginners.")
        console.print(Panel(Markdown(response), title="📖 Lesson", border_style="green"))
        
        ZetaLogger.log(f"Teaching: {topic}", response, lesson=response)


@cli.command()
def log():
    """View your ZETA learning log."""
    console.print(Panel.fit(
        "[bold yellow]📝 Learning Log[/bold yellow]",
        border_style="yellow"
    ))
    console.print()
    ZetaLogger.show_log()


if __name__ == "__main__":
    cli()

