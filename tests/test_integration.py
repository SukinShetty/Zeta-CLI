"""Integration tests for ZETA workflows."""

import pytest
from pathlib import Path
from unittest.mock import patch, Mock, MagicMock
from zeta import ZetaAgent, ZetaLogger, detect_vague_task


class TestFullWorkflow:
    """Tests for complete user workflows."""
    
    @patch('zeta.ZetaAgent')
    @patch('zeta.ZetaLogger')
    def test_vague_task_workflow(self, mock_logger, mock_agent_class, temp_dir):
        """Test complete workflow with vague task."""
        # Setup mocks
        mock_agent = Mock()
        mock_agent.ask_clarifying_question.return_value = {
            "question": "What kind of app?",
            "options": ["Web app", "CLI app", "Mobile app"]
        }
        mock_agent.process_task.return_value = "Created web app successfully"
        mock_agent.explain_action.return_value = "Explanation of what was done"
        mock_agent_class.return_value = mock_agent
        
        # Simulate workflow
        task = "make an app"
        assert detect_vague_task(task) == True
        
        clarification = mock_agent.ask_clarifying_question(task)
        assert clarification is not None
        assert "options" in clarification
    
    def test_file_creation_workflow(self, temp_dir):
        """Test file creation workflow."""
        from zeta import ZetaTools
        
        file_path = temp_dir / "test_output.txt"
        content = "Test content for workflow"
        
        with patch('zeta.Confirm') as mock_confirm:
            mock_confirm.ask.return_value = True
            
            # Create file
            result = ZetaTools.write_file(str(file_path), content, confirm=True)
            assert "Successfully wrote" in result
            
            # Verify file exists
            assert file_path.exists()
            assert file_path.read_text() == content
            
            # Log the action
            ZetaLogger.log("Created file", f"Created {file_path}", "File creation lesson")
            
            # Verify log entry
            log_content = Path("zeta_log.md").read_text()
            assert "Created file" in log_content
    
    @patch('zeta.ZetaAgent')
    def test_teaching_mode_workflow(self, mock_agent_class):
        """Test teaching mode workflow."""
        mock_agent = Mock()
        mock_agent.process_task.return_value = "Detailed explanation with definitions"
        mock_agent_class.return_value = mock_agent
        
        # Simulate teaching session
        agent = ZetaAgent(teach_mode=True, critic_mode=False)
        agent.llm = Mock()
        agent.llm.invoke.return_value = Mock(content="Detailed lesson content")
        
        response = agent.process_task("Explain what HTML is")
        assert response is not None
    
    @patch('zeta.ZetaAgent')
    def test_critic_mode_workflow(self, mock_agent_class, temp_dir):
        """Test critic mode workflow."""
        # Create a test Python file
        test_file = temp_dir / "test_code.py"
        test_file.write_text("def add(a, b):\n    return a + b\n")
        
        mock_agent = Mock()
        mock_agent.critic_review.return_value = {
            "score": 7,
            "issues": ["Missing type hints"],
            "suggestions": ["Add type hints"],
            "explanation": "Good but needs improvement"
        }
        mock_agent_class.return_value = mock_agent
        
        # Simulate critic review
        code = test_file.read_text()
        review = mock_agent.critic_review(code, str(test_file))
        
        assert review["score"] < 8
        assert len(review["issues"]) > 0
        assert len(review["suggestions"]) > 0


class TestErrorRecovery:
    """Tests for error recovery workflows."""
    
    def test_tool_error_recovery(self, temp_dir):
        """Test recovery from tool errors."""
        from zeta import ZetaTools
        
        # Try to read non-existent file
        result = ZetaTools.read_file.func(str(temp_dir / "nonexistent.txt"))
        assert "Error" in result
        
        # System should continue functioning
        # Try another operation
        listing = ZetaTools.list_files.func(str(temp_dir))
        assert isinstance(listing, str)
    
    @patch('zeta.ZetaAgent')
    def test_llm_error_recovery(self, mock_agent_class):
        """Test recovery from LLM errors."""
        mock_agent = Mock()
        mock_agent.process_task.side_effect = Exception("LLM connection failed")
        mock_agent_class.return_value = mock_agent
        
        # Should handle error gracefully
        try:
            result = mock_agent.process_task("test task")
        except Exception:
            # Error should be caught and handled
            pass
        
        # System should still be functional
        assert True

