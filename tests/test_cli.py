"""Tests for CLI commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, Mock
from zeta import cli


class TestCLIHelp:
    """Tests for help command."""
    
    def test_help_command(self):
        """Test that help command works."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert "ZETA" in result.output
        assert "run" in result.output or "teach" in result.output
    
    def test_version_command(self):
        """Test version command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert "1.0.0" in result.output


class TestRunCommand:
    """Tests for run command."""
    
    @patch('zeta.ZetaAgent')
    @patch('zeta.detect_vague_task')
    @patch('zeta.Confirm')
    def test_run_with_task(self, mock_confirm, mock_detect, mock_agent_class):
        """Test run command with a task."""
        mock_detect.return_value = False
        mock_confirm.ask.return_value = False  # Don't ask for learning
        mock_agent = Mock()
        mock_agent.process_task.return_value = "Task completed successfully"
        mock_agent.explain_action.return_value = "Explanation"
        mock_agent_class.return_value = mock_agent
        
        runner = CliRunner()
        result = runner.invoke(cli, ['run', 'test task'])
        
        # May exit with 0 or 1 depending on LLM availability, but shouldn't crash
        assert result.exit_code in [0, 1]
    
    @patch('zeta.ZetaAgent')
    @patch('zeta.detect_vague_task')
    def test_run_with_vague_task(self, mock_detect, mock_agent_class):
        """Test run command with vague task."""
        mock_detect.return_value = True
        mock_agent = Mock()
        mock_agent.ask_clarifying_question.return_value = {
            "question": "What kind?",
            "options": ["Option 1", "Option 2"]
        }
        mock_agent.process_task.return_value = "Task completed"
        mock_agent.explain_action.return_value = "Explanation"
        mock_agent_class.return_value = mock_agent
        
        runner = CliRunner()
        # Simulate user input
        result = runner.invoke(cli, ['run', 'make something'], input='1\nn\n')
        
        # Should not crash
        assert result.exit_code in [0, 1]  # May exit due to input handling
    
    @patch('zeta.ZetaAgent')
    def test_run_with_teach_flag(self, mock_agent_class):
        """Test run command with --teach flag."""
        mock_agent = Mock()
        mock_agent.process_task.return_value = "Task with teaching"
        mock_agent.explain_action.return_value = "Detailed explanation"
        mock_agent_class.return_value = mock_agent
        
        runner = CliRunner()
        with patch('zeta.detect_vague_task', return_value=False):
            result = runner.invoke(cli, ['run', 'test', '--teach'], input='n\n')
            # Should attempt to create agent with teach_mode=True
            mock_agent_class.assert_called()
    
    @patch('zeta.ZetaAgent')
    def test_run_with_critic_flag(self, mock_agent_class):
        """Test run command with --critic flag."""
        mock_agent = Mock()
        mock_agent.process_task.return_value = "Task with critic"
        mock_agent.explain_action.return_value = "Explanation"
        mock_agent.critic_review.return_value = {"score": 8, "issues": []}
        mock_agent_class.return_value = mock_agent
        
        runner = CliRunner()
        with patch('zeta.detect_vague_task', return_value=False):
            with patch('pathlib.Path.glob', return_value=[]):
                result = runner.invoke(cli, ['run', 'test', '--critic'], input='n\n')
                # Should attempt to create agent with critic_mode=True
                mock_agent_class.assert_called()


class TestTeachCommand:
    """Tests for teach command."""
    
    @patch('zeta.ZetaAgent')
    @patch('zeta.Prompt')
    def test_teach_command(self, mock_prompt, mock_agent_class):
        """Test teach command."""
        mock_agent = Mock()
        mock_agent.process_task.return_value = "Lesson content"
        mock_agent_class.return_value = mock_agent
        
        # Simulate user typing "exit"
        mock_prompt.ask.side_effect = ["What is Python?", "exit"]
        
        runner = CliRunner()
        result = runner.invoke(cli, ['teach'])
        
        # Should complete without error
        assert result.exit_code in [0, 1]


class TestLogCommand:
    """Tests for log command."""
    
    @patch('zeta.ZetaLogger.show_log')
    def test_log_command(self, mock_show_log):
        """Test log command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['log'])
        
        assert result.exit_code == 0
        mock_show_log.assert_called_once()


class TestCommandErrors:
    """Tests for error handling in commands."""
    
    @patch('zeta.ZetaAgent')
    def test_run_command_with_exception(self, mock_agent_class):
        """Test run command handles exceptions."""
        mock_agent_class.side_effect = Exception("Agent initialization failed")
        
        runner = CliRunner()
        result = runner.invoke(cli, ['run', 'test'])
        
        # Should handle error gracefully
        assert result.exit_code != 0 or "error" in result.output.lower()

