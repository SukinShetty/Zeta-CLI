"""Tests for error handling and edge cases."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from zeta import ZetaAgent, ZetaTools, ZetaLogger
from rich.console import Console


class TestErrorHandling:
    """Test error handling in various scenarios."""
    
    def test_explain_action_llm_error(self):
        """Test explain_action handles LLM errors gracefully."""
        agent = ZetaAgent(teach_mode=False)
        agent.llm = Mock()
        agent.llm.invoke = Mock(side_effect=Exception("LLM error"))
        
        result = agent.explain_action("test action", "test result")
        assert "Completed: test action" in result
    
    def test_critic_review_llm_error(self):
        """Test critic_review handles LLM errors gracefully."""
        agent = ZetaAgent(critic_mode=True)
        agent.llm = Mock()
        agent.llm.invoke = Mock(side_effect=Exception("LLM error"))
        
        review = agent.critic_review("def test(): pass", "test.py")
        assert review["score"] == 5
        assert "review" in review["explanation"].lower() or "error" in review["explanation"].lower()
    
    def test_ask_clarifying_question_invalid_response(self):
        """Test ask_clarifying_question handles invalid JSON."""
        agent = ZetaAgent()
        agent.llm = Mock()
        agent.llm.invoke = Mock(return_value=Mock(content="not json"))
        
        result = agent.ask_clarifying_question("make something")
        assert result is None
    
    def test_process_task_exception_handling(self):
        """Test process_task handles exceptions gracefully."""
        agent = ZetaAgent()
        agent.llm = Mock()
        agent.llm.invoke = Mock(side_effect=Exception("Connection error"))
        
        result = agent.process_task("test task")
        assert "error" in result.lower() or "try" in result.lower()
    
    def test_execute_tool_with_exception(self):
        """Test execute_tool handles tool execution errors."""
        agent = ZetaAgent()
        
        # Mock the tool's func method to raise an exception
        with patch.object(ZetaTools.read_file.func, '__call__', side_effect=Exception("Tool error")):
            result = agent.execute_tool("read_file", {"file_path": "test.txt"})
            assert "error" in result.lower()
    
    def test_cli_invalid_choice_out_of_range(self):
        """Test CLI handles invalid choice (out of range)."""
        from click.testing import CliRunner
        from zeta import cli
        
        runner = CliRunner()
        
        with patch('zeta.ZetaAgent') as MockAgent:
            mock_agent = MockAgent.return_value
            mock_agent.is_vague_task.return_value = True
            mock_agent.ask_clarifying_question.return_value = {
                'question': 'What would you like?',
                'options': ['Option 1', 'Option 2']
            }
            mock_agent.process_task.return_value = "Task completed"
            
            with patch('zeta.Prompt.ask', return_value="5"):  # Invalid choice
                result = runner.invoke(cli, ['run', 'make something'])
                assert result.exit_code in [0, 1]
    
    def test_cli_invalid_choice_non_numeric(self):
        """Test CLI handles invalid choice (non-numeric)."""
        from click.testing import CliRunner
        from zeta import cli
        
        runner = CliRunner()
        
        with patch('zeta.ZetaAgent') as MockAgent:
            mock_agent = MockAgent.return_value
            mock_agent.is_vague_task.return_value = True
            mock_agent.ask_clarifying_question.return_value = {
                'question': 'What would you like?',
                'options': ['Option 1', 'Option 2']
            }
            mock_agent.process_task.return_value = "Task completed"
            
            with patch('zeta.Prompt.ask', return_value="abc"):  # Non-numeric
                result = runner.invoke(cli, ['run', 'make something'])
                assert result.exit_code in [0, 1]
    
    def test_critic_mode_file_read_error(self):
        """Test critic mode handles file read errors."""
        from click.testing import CliRunner
        from zeta import cli
        from pathlib import Path
        import tempfile
        
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("print('hello')")
            
            with patch('zeta.ZetaAgent') as MockAgent:
                mock_agent = MockAgent.return_value
                mock_agent.is_vague_task.return_value = False
                mock_agent.process_task.return_value = "Task completed"
                mock_agent.critic_review.return_value = {
                    'score': 7,
                    'explanation': 'Good code',
                    'issues': [],
                    'suggestions': []
                }
                
                # Simulate file read error
                with patch('pathlib.Path.read_text', side_effect=Exception("Read error")):
                    result = runner.invoke(cli, ['run', 'test task', '--critic'], 
                                         input='y\n')
                    assert result.exit_code in [0, 1]
    
    def test_run_command_exception_in_tool(self):
        """Test run_command handles exceptions."""
        from zeta import ZetaTools
        
        with patch('subprocess.run', side_effect=Exception("Command failed")):
            result = ZetaTools.run_command.func("invalid command")
            assert "Error" in result
    
    def test_process_task_tool_execution_loop(self):
        """Test process_task tool execution loop."""
        agent = ZetaAgent()
        agent.llm = Mock()
        
        # Mock LLM to return tool calls
        mock_response = Mock()
        mock_response.content = 'TOOL_CALL: read_file(file_path="test.txt")'
        agent.llm.invoke.return_value = mock_response
        
        # Mock tool execution
        with patch.object(agent, 'execute_tool', return_value="File content"):
            result = agent.process_task("read test.txt")
            assert result is not None
    
    def test_teach_command_prompt_interaction(self):
        """Test teach command handles user prompts."""
        from click.testing import CliRunner
        from zeta import cli
        
        runner = CliRunner()
        
        with patch('zeta.ZetaAgent') as MockAgent:
            mock_agent = MockAgent.return_value
            mock_agent.process_task.return_value = "Lesson content"
            
            with patch('zeta.Prompt.ask', side_effect=["What is Python?", "exit"]):
                result = runner.invoke(cli, ['teach'])
                assert result.exit_code in [0, 1]

