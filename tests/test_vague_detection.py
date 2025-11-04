"""Tests for vague task detection."""

import pytest
from zeta import detect_vague_task


class TestVagueTaskDetection:
    """Tests for vague task detection function."""
    
    def test_very_short_task(self):
        """Test that very short tasks are detected as vague."""
        assert detect_vague_task("make") == True
        assert detect_vague_task("create") == True
        assert detect_vague_task("build app") == True
    
    def test_vague_keywords_without_details(self):
        """Test vague keywords without sufficient details."""
        assert detect_vague_task("make a chatbot") == True
        assert detect_vague_task("create something") == True
        assert detect_vague_task("build a") == True
    
    def test_specific_tasks_not_vague(self):
        """Test that specific tasks are not detected as vague."""
        assert detect_vague_task("create a Python script to calculate fibonacci numbers") == False
        assert detect_vague_task("make an HTML file with a button that changes color") == False
        assert detect_vague_task("build a REST API endpoint for user authentication") == False
    
    def test_task_with_many_words(self):
        """Test that tasks with many words are not vague."""
        assert detect_vague_task("create a comprehensive web application with database integration") == False
        assert detect_vague_task("build a machine learning model for image classification") == False
    
    def test_edge_cases(self):
        """Test edge cases."""
        assert detect_vague_task("") == True  # Empty string
        assert detect_vague_task("make a") == True  # Just keyword + article
        assert detect_vague_task("create a simple") == True  # Keyword + article + adjective
    
    def test_case_insensitive(self):
        """Test that detection is case insensitive."""
        assert detect_vague_task("MAKE A CHATBOT") == True
        assert detect_vague_task("Create Something") == True
        assert detect_vague_task("BUILD APP") == True

