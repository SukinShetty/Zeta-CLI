"""Tests for ZetaLogger class."""

import pytest
from pathlib import Path
from zeta import ZetaLogger, LOG_FILE


class TestZetaLogger:
    """Tests for ZetaLogger class."""
    
    def test_init_log_creates_file(self, clean_log):
        """Test that init_log creates the log file."""
        ZetaLogger.init_log()
        assert Path(LOG_FILE).exists()
        
        content = Path(LOG_FILE).read_text()
        assert "ZETA Learning Log" in content
        assert "Welcome to ZETA" in content
    
    def test_init_log_with_existing_file(self, clean_log):
        """Test init_log doesn't overwrite existing file."""
        ZetaLogger.init_log()
        initial_content = Path(LOG_FILE).read_text()
        
        ZetaLogger.init_log()
        final_content = Path(LOG_FILE).read_text()
        
        assert initial_content == final_content
    
    def test_log_action(self, clean_log):
        """Test logging an action."""
        ZetaLogger.log("Test action", "Test explanation")
        
        assert Path(LOG_FILE).exists()
        content = Path(LOG_FILE).read_text()
        assert "Test action" in content
        assert "Test explanation" in content
    
    def test_log_with_lesson(self, clean_log):
        """Test logging with a lesson."""
        ZetaLogger.log("Test action", "Test explanation", lesson="Test lesson")
        
        content = Path(LOG_FILE).read_text()
        assert "Test action" in content
        assert "Test explanation" in content
        assert "Test lesson" in content
        assert "**Lesson:**" in content
    
    def test_log_timestamp_format(self, clean_log):
        """Test that timestamps are properly formatted."""
        ZetaLogger.log("Test action", "Test explanation")
        
        content = Path(LOG_FILE).read_text()
        assert "## " in content  # Timestamp header format
    
    def test_show_log_empty(self, clean_log):
        """Test showing log when file doesn't exist."""
        if Path(LOG_FILE).exists():
            Path(LOG_FILE).unlink()
        
        # Should not raise exception
        ZetaLogger.show_log()
    
    def test_show_log_with_content(self, clean_log):
        """Test showing log with content."""
        ZetaLogger.log("Test action", "Test explanation")
        
        # Should not raise exception
        ZetaLogger.show_log()
    
    def test_multiple_log_entries(self, clean_log):
        """Test logging multiple entries."""
        ZetaLogger.log("Action 1", "Explanation 1")
        ZetaLogger.log("Action 2", "Explanation 2")
        ZetaLogger.log("Action 3", "Explanation 3")
        
        content = Path(LOG_FILE).read_text()
        assert "Action 1" in content
        assert "Action 2" in content
        assert "Action 3" in content
        assert content.count("---") >= 2  # Should have separators

