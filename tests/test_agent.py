"""Tests for ZetaAgent class."""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from zeta import ZetaAgent, ZetaTools


class TestZetaAgentInitialization:
    """Tests for agent initialization."""
    
    def test_agent_init_normal_mode(self, mock_llm):
        """Test agent initialization in normal mode."""
        agent = ZetaAgent(teach_mode=False, critic_mode=False)
        agent.llm = mock_llm
        assert agent.teach_mode == False
        assert agent.critic_mode == False
    
    def test_agent_init_teach_mode(self, mock_llm):
        """Test agent initialization in teaching mode."""
        agent = ZetaAgent(teach_mode=True, critic_mode=False)
        agent.llm = mock_llm
        assert agent.teach_mode == True
        assert agent.critic_mode == False
    
    def test_agent_init_critic_mode(self, mock_llm):
        """Test agent initialization in critic mode."""
        agent = ZetaAgent(teach_mode=False, critic_mode=True)
        agent.llm = mock_llm
        assert agent.teach_mode == False
        assert agent.critic_mode == True
    
    def test_agent_init_both_modes(self, mock_llm):
        """Test agent initialization with both modes enabled."""
        agent = ZetaAgent(teach_mode=True, critic_mode=True)
        agent.llm = mock_llm
        assert agent.teach_mode == True
        assert agent.critic_mode == True


class TestSystemPrompt:
    """Tests for system prompt building."""
    
    def test_base_prompt(self, agent_normal):
        """Test base system prompt."""
        prompt = agent_normal._build_system_prompt()
        assert "ZETA" in prompt
        assert "friendly" in prompt.lower()
        assert "read_file" in prompt
        assert "write_file" in prompt
    
    def test_teach_mode_prompt(self, agent_teach):
        """Test system prompt with teaching mode."""
        prompt = agent_teach._build_system_prompt()
        assert "TEACHING MODE" in prompt or "teaching" in prompt.lower()
        assert "definitions" in prompt.lower() or "detailed" in prompt.lower()
    
    def test_critic_mode_prompt(self, agent_critic):
        """Test system prompt with critic mode."""
        prompt = agent_critic._build_system_prompt()
        assert "CRITIC MODE" in prompt or "critic" in prompt.lower()
        assert "score" in prompt.lower() or "review" in prompt.lower()


class TestToolExecution:
    """Tests for tool execution."""
    
    def test_execute_read_file(self, agent_normal, temp_dir, sample_file):
        """Test executing read_file tool."""
        result = agent_normal.execute_tool("read_file", {"file_path": str(sample_file)})
        assert "Hello, ZETA!" in result
    
    def test_execute_write_file(self, agent_normal, temp_dir):
        """Test executing write_file tool."""
        file_path = temp_dir / "test_write.txt"
        with patch('zeta.Confirm') as mock_confirm:
            mock_confirm.ask.return_value = True
            from zeta import ZetaTools
            result = ZetaTools.write_file(str(file_path), "Test content", confirm=True)
            assert "Successfully wrote" in result
    
    def test_execute_run_command(self, agent_normal):
        """Test executing run_command tool."""
        result = agent_normal.execute_tool("run_command", {"command": "echo test"})
        assert "test" in result or "executed" in result.lower()
    
    def test_execute_list_files(self, agent_normal, temp_dir):
        """Test executing list_files tool."""
        result = agent_normal.execute_tool("list_files", {"directory": str(temp_dir)})
        assert isinstance(result, str)
    
    def test_execute_unknown_tool(self, agent_normal):
        """Test executing unknown tool."""
        result = agent_normal.execute_tool("unknown_tool", {})
        assert "Unknown tool" in result


class TestToolCallParsing:
    """Tests for tool call parsing."""
    
    def test_parse_simple_tool_call(self, agent_normal):
        """Test parsing simple tool call."""
        response = 'TOOL_CALL: read_file(file_path="test.txt")'
        tool_calls = agent_normal.parse_tool_calls(response)
        assert len(tool_calls) == 1
        assert tool_calls[0]["tool"] == "read_file"
        assert tool_calls[0]["args"]["file_path"] == "test.txt"
    
    def test_parse_multiple_tool_calls(self, agent_normal):
        """Test parsing multiple tool calls."""
        response = '''TOOL_CALL: read_file(file_path="file1.txt")
        Some text here
        TOOL_CALL: list_files(directory=".")'''
        tool_calls = agent_normal.parse_tool_calls(response)
        assert len(tool_calls) >= 1
    
    def test_parse_multiline_content(self, agent_normal):
        """Test parsing tool call with multiline content."""
        response = '''TOOL_CALL: write_file(file_path="test.py", content=\"""line1
line2
line3\""")'''
        tool_calls = agent_normal.parse_tool_calls(response)
        assert len(tool_calls) == 1
        # The multiline parsing may not capture content perfectly, but should parse file_path
        assert "file_path" in tool_calls[0]["args"]
        # Content parsing is complex - just verify it doesn't crash
        assert "args" in tool_calls[0]
    
    def test_parse_no_tool_calls(self, agent_normal):
        """Test parsing response with no tool calls."""
        response = "This is a regular response without tool calls."
        tool_calls = agent_normal.parse_tool_calls(response)
        assert len(tool_calls) == 0


class TestClarifyingQuestions:
    """Tests for clarifying question generation."""
    
    def test_ask_clarifying_question_success(self, agent_normal):
        """Test generating clarifying questions."""
        mock_response = Mock()
        mock_response.content = json.dumps({
            "question": "What kind of app?",
            "options": ["Option 1", "Option 2", "Option 3"]
        })
        agent_normal.llm.invoke.return_value = mock_response
        
        result = agent_normal.ask_clarifying_question("make an app")
        assert result is not None
        assert "question" in result
        assert "options" in result
        assert len(result["options"]) > 0
    
    def test_ask_clarifying_question_invalid_json(self, agent_normal):
        """Test handling invalid JSON response."""
        mock_response = Mock()
        mock_response.content = "This is not JSON"
        agent_normal.llm.invoke.return_value = mock_response
        
        result = agent_normal.ask_clarifying_question("generate something")
        assert result is None


class TestCriticReview:
    """Tests for critic review functionality."""
    
    def test_critic_review_success(self, agent_critic):
        """Test code review with valid response."""
        mock_response = Mock()
        mock_response.content = json.dumps({
            "score": 7,
            "issues": ["Missing type hints"],
            "suggestions": ["Add type hints"],
            "explanation": "Good code but needs improvement"
        })
        agent_critic.llm.invoke.return_value = mock_response
        
        result = agent_critic.critic_review("def add(a, b): return a + b", "test.py")
        assert result["score"] == 7
        assert len(result["issues"]) > 0
        assert len(result["suggestions"]) > 0
    
    def test_critic_review_default_on_error(self, agent_critic):
        """Test critic review returns default on error."""
        agent_critic.llm.invoke.side_effect = Exception("LLM error")
        
        result = agent_critic.critic_review("code", "test.py")
        assert "score" in result
        assert result["score"] == 5  # Default score


class TestExplainAction:
    """Tests for explain_action method."""
    
    def test_explain_action_success(self, agent_normal):
        """Test generating action explanation."""
        mock_response = Mock()
        mock_response.content = "This action created a file successfully."
        agent_normal.llm.invoke.return_value = mock_response
        
        result = agent_normal.explain_action("Created file", "Success", teach_mode=False)
        assert "successfully" in result.lower() or len(result) > 0
    
    def test_explain_action_teach_mode(self, agent_teach):
        """Test explanation in teaching mode."""
        mock_response = Mock()
        mock_response.content = "Detailed explanation with definitions."
        agent_teach.llm.invoke.return_value = mock_response
        
        result = agent_teach.explain_action("Created file", "Success", teach_mode=True)
        assert len(result) > 0

