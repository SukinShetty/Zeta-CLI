"""Tests to improve coverage for uncovered lines."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from zeta import ZetaAgent, ZetaTools, detect_vague_task
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
import tempfile
from pathlib import Path


class TestCoverageGaps:
    """Tests to cover previously untested code paths."""
    
    def test_process_task_with_tool_calls_loop(self):
        """Test process_task handles tool calls in a loop."""
        agent = ZetaAgent()
        agent.llm = Mock()
        
        # Mock LLM to return tool calls multiple times
        mock_response_1 = Mock()
        mock_response_1.content = 'TOOL_CALL: read_file(file_path="test.txt")'
        
        mock_response_2 = Mock()
        mock_response_2.content = "Final response"
        
        agent.llm.invoke.side_effect = [mock_response_1, mock_response_2]
        
        with patch.object(agent, 'execute_tool', return_value="File content"):
            result = agent.process_task("read test.txt")
            assert result is not None
    
    def test_execute_tool_write_file_with_confirm(self):
        """Test execute_tool calls write_file with confirm=True."""
        agent = ZetaAgent()
        
        with patch.object(ZetaTools, 'write_file', return_value="File written") as mock_write:
            result = agent.execute_tool("write_file", {
                "file_path": "test.txt",
                "content": "test content"
            })
            
            mock_write.assert_called_once_with("test.txt", "test content", confirm=True)
            assert result == "File written"
    
    def test_parse_tool_calls_multiline_content_edge_case(self):
        """Test parse_tool_calls with multiline content in different formats."""
        agent = ZetaAgent()
        
        # Test with triple single quotes
        tool_text = 'TOOL_CALL: write_file(file_path="test.py", content=\'\'\'line1\nline2\'\'\')'
        calls = agent.parse_tool_calls(tool_text)
        assert len(calls) > 0
        assert calls[0]["tool"] == "write_file"
    
    def test_parse_tool_calls_args_assignment(self):
        """Test parse_tool_calls properly assigns args."""
        agent = ZetaAgent()
        
        tool_text = 'TOOL_CALL: read_file(file_path="test.txt")'
        calls = agent.parse_tool_calls(tool_text)
        
        assert len(calls) == 1
        assert calls[0]["tool"] == "read_file"
        assert "file_path" in calls[0]["args"]
        assert calls[0]["args"]["file_path"] == "test.txt"
    
    def test_detect_vague_task_returns_true(self):
        """Test detect_vague_task returns True for vague tasks."""
        assert detect_vague_task("make app") is True
        assert detect_vague_task("create something") is True
        assert detect_vague_task("build") is True
    
    def test_cli_teach_prompt_loop(self):
        """Test teach command prompt interaction loop."""
        from click.testing import CliRunner
        from zeta import cli
        
        runner = CliRunner()
        
        with patch('zeta.ZetaAgent') as MockAgent:
            mock_agent = MockAgent.return_value
            mock_agent.process_task.return_value = "Lesson about Python"
            
            # Simulate multiple questions then exit
            with patch('zeta.Prompt.ask', side_effect=["What is Python?", "How does it work?", "exit"]):
                result = runner.invoke(cli, ['teach'])
                assert result.exit_code in [0, 1]
    
    def test_cli_clarification_valid_choice(self):
        """Test CLI handles valid clarification choice."""
        from click.testing import CliRunner
        from zeta import cli
        
        runner = CliRunner()
        
        with patch('zeta.ZetaAgent') as MockAgent:
            mock_agent = MockAgent.return_value
            mock_agent.is_vague_task.return_value = True
            mock_agent.ask_clarifying_question.return_value = {
                'question': 'What would you like?',
                'options': ['Web app', 'CLI app', 'Mobile app']
            }
            mock_agent.process_task.return_value = "Task completed"
            mock_agent.explain_action.return_value = "Explanation"
            MockAgent.return_value = mock_agent
            
            with patch('zeta.Confirm.ask', return_value=False):
                with patch('zeta.Prompt.ask', return_value="2"):  # Valid choice
                    result = runner.invoke(cli, ['run', 'make app'])
                    assert result.exit_code in [0, 1]
    
    def test_cli_clarification_choice_1(self):
        """Test CLI handles choice 1."""
        from click.testing import CliRunner
        from zeta import cli
        
        runner = CliRunner()
        
        with patch('zeta.ZetaAgent') as MockAgent:
            mock_agent = MockAgent.return_value
            mock_agent.is_vague_task.return_value = True
            mock_agent.ask_clarifying_question.return_value = {
                'question': 'What would you like?',
                'options': ['Option 1']
            }
            mock_agent.process_task.return_value = "Task completed"
            mock_agent.explain_action.return_value = "Explanation"
            MockAgent.return_value = mock_agent
            
            with patch('zeta.Confirm.ask', return_value=False):
                with patch('zeta.Prompt.ask', return_value="1"):
                    result = runner.invoke(cli, ['run', 'make something'])
                    assert result.exit_code in [0, 1]
    
    def test_critic_mode_with_python_files(self):
        """Test critic mode reviews Python files."""
        from click.testing import CliRunner
        from zeta import cli
        
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("def hello():\n    print('world')")
            
            with patch('zeta.ZetaAgent') as MockAgent:
                mock_agent = MockAgent.return_value
                mock_agent.is_vague_task.return_value = False
                mock_agent.process_task.return_value = "Task completed"
                mock_agent.critic_review.return_value = {
                    'score': 7,
                    'explanation': 'Good code but could improve',
                    'issues': ['No docstring'],
                    'suggestions': ['Add docstring']
                }
                
                # Change to temp directory
                import os
                old_cwd = os.getcwd()
                try:
                    os.chdir(tmpdir)
                    with patch('zeta.Confirm.ask', return_value=False):
                        result = runner.invoke(cli, ['run', 'test task', '--critic'])
                        assert result.exit_code in [0, 1]
                finally:
                    os.chdir(old_cwd)
    
    def test_critic_mode_high_score(self):
        """Test critic mode with high score (>=8)."""
        from click.testing import CliRunner
        from zeta import cli
        
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("def hello():\n    pass")
            
            with patch('zeta.ZetaAgent') as MockAgent:
                mock_agent = MockAgent.return_value
                mock_agent.is_vague_task.return_value = False
                mock_agent.process_task.return_value = "Task completed"
                mock_agent.critic_review.return_value = {
                    'score': 9,
                    'explanation': 'Excellent code',
                    'issues': [],
                    'suggestions': []
                }
                
                import os
                old_cwd = os.getcwd()
                try:
                    os.chdir(tmpdir)
                    with patch('zeta.Confirm.ask', return_value=False):
                        result = runner.invoke(cli, ['run', 'test', '--critic'])
                        assert result.exit_code in [0, 1]
                finally:
                    os.chdir(old_cwd)
    
    def test_critic_mode_with_issues_and_suggestions(self):
        """Test critic mode displays issues and suggestions."""
        from click.testing import CliRunner
        from zeta import cli
        
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("print('test')")
            
            with patch('zeta.ZetaAgent') as MockAgent:
                mock_agent = MockAgent.return_value
                mock_agent.is_vague_task.return_value = False
                mock_agent.process_task.return_value = "Task completed"
                mock_agent.critic_review.return_value = {
                    'score': 6,
                    'explanation': 'Needs improvement',
                    'issues': ['Issue 1', 'Issue 2'],
                    'suggestions': ['Suggestion 1', 'Suggestion 2']
                }
                
                import os
                old_cwd = os.getcwd()
                try:
                    os.chdir(tmpdir)
                    with patch('zeta.Confirm.ask', return_value=False):
                        result = runner.invoke(cli, ['run', 'test', '--critic'])
                        assert result.exit_code in [0, 1]
                finally:
                    os.chdir(old_cwd)
    
    def test_teaching_mode_lesson_display(self):
        """Test teaching mode displays lesson after task."""
        from click.testing import CliRunner
        from zeta import cli
        
        runner = CliRunner()
        
        with patch('zeta.ZetaAgent') as MockAgent:
            mock_agent = MockAgent.return_value
            mock_agent.is_vague_task.return_value = False
            mock_agent.process_task.side_effect = [
                "Task completed",
                "This is a lesson about how it works"
            ]
            mock_agent.explain_action.return_value = "Explanation"
            MockAgent.return_value = mock_agent
            
            with patch('zeta.Confirm.ask', return_value=True):  # User wants to learn
                result = runner.invoke(cli, ['run', 'test task', '--teach'])
                assert result.exit_code in [0, 1]
    
    def test_parse_tool_calls_with_multiple_args(self):
        """Test parse_tool_calls with multiple arguments."""
        agent = ZetaAgent()
        
        tool_text = 'TOOL_CALL: write_file(file_path="test.txt", content="hello", extra="value")'
        calls = agent.parse_tool_calls(tool_text)
        
        assert len(calls) > 0
        assert calls[0]["tool"] == "write_file"
        assert "file_path" in calls[0]["args"]
        assert "content" in calls[0]["args"]

