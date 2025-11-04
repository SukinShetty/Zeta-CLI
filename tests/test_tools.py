"""Tests for ZetaTools class."""

import pytest
import subprocess
from pathlib import Path
from unittest.mock import patch, Mock
from zeta import ZetaTools


class TestReadFile:
    """Tests for read_file tool."""
    
    def test_read_existing_file(self, temp_dir, sample_file):
        """Test reading an existing file."""
        # read_file is decorated with @tool, access the underlying function
        result = ZetaTools.read_file.func(str(sample_file))
        assert "Hello, ZETA!" in result
    
    def test_read_nonexistent_file(self, temp_dir):
        """Test reading a non-existent file."""
        result = ZetaTools.read_file.func(str(temp_dir / "nonexistent.txt"))
        assert "Error" in result
        assert "does not exist" in result
    
    def test_read_file_with_error(self, temp_dir):
        """Test reading file with permission error."""
        # Create file first, then mock open to fail
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            result = ZetaTools.read_file.func(str(test_file))
            assert "Error reading file" in result or "Error" in result


class TestWriteFile:
    """Tests for write_file tool."""
    
    @patch('zeta.Confirm')
    def test_write_file_with_confirmation_accepted(self, mock_confirm, temp_dir):
        """Test writing file when confirmation is accepted."""
        mock_confirm.ask.return_value = True
        file_path = temp_dir / "new_file.txt"
        content = "Test content"
        
        result = ZetaTools.write_file(str(file_path), content, confirm=True)
        
        assert "Successfully wrote" in result
        assert file_path.exists()
        assert file_path.read_text() == content
    
    @patch('zeta.Confirm')
    def test_write_file_with_confirmation_declined(self, mock_confirm, temp_dir):
        """Test writing file when confirmation is declined."""
        mock_confirm.ask.return_value = False
        file_path = temp_dir / "new_file.txt"
        content = "Test content"
        
        result = ZetaTools.write_file(str(file_path), content, confirm=True)
        
        assert "declined" in result.lower()
        assert not file_path.exists()
    
    @patch('zeta.Confirm')
    def test_write_file_without_confirmation(self, mock_confirm, temp_dir):
        """Test writing file without confirmation prompt."""
        file_path = temp_dir / "new_file.txt"
        content = "Test content"
        
        result = ZetaTools.write_file(str(file_path), content, confirm=False)
        
        assert "Successfully wrote" in result
        assert file_path.exists()
        assert file_path.read_text() == content
    
    @patch('zeta.Confirm')
    def test_write_file_creates_parent_dirs(self, mock_confirm, temp_dir):
        """Test that write_file creates parent directories."""
        file_path = temp_dir / "subdir" / "nested" / "file.txt"
        content = "Nested content"
        
        result = ZetaTools.write_file(str(file_path), content, confirm=False)
        
        assert "Successfully wrote" in result
        assert file_path.exists()
        assert file_path.read_text() == content
    
    @patch('zeta.Confirm')
    def test_write_file_overwrites_existing(self, mock_confirm, temp_dir, sample_file):
        """Test writing to an existing file."""
        new_content = "Updated content"
        result = ZetaTools.write_file(str(sample_file), new_content, confirm=False)
        
        assert "Successfully wrote" in result
        assert sample_file.read_text() == new_content
    
    @patch('zeta.Confirm')
    def test_write_file_error_handling(self, mock_confirm, temp_dir):
        """Test error handling when writing file."""
        with patch('builtins.open', side_effect=IOError("Disk full")):
            result = ZetaTools.write_file(str(temp_dir / "test.txt"), "content", confirm=False)
            assert "Error writing file" in result


class TestRunCommand:
    """Tests for run_command tool."""
    
    def test_run_valid_command(self):
        """Test running a valid command."""
        result = ZetaTools.run_command.func("echo test")
        assert "test" in result or "Command executed successfully" in result
    
    def test_run_invalid_command(self):
        """Test running an invalid command."""
        result = ZetaTools.run_command.func("nonexistent_command_xyz123")
        assert "Error" in result
    
    def test_run_command_timeout(self):
        """Test command timeout handling."""
        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired("sleep", 30)):
            result = ZetaTools.run_command.func("sleep 60")
            assert "timed out" in result.lower()
    
    def test_run_command_with_error(self):
        """Test command that returns error code."""
        result = ZetaTools.run_command.func("python -c 'import sys; sys.exit(1)'")
        assert "Error" in result or "failed" in result.lower()


class TestListFiles:
    """Tests for list_files tool."""
    
    def test_list_files_existing_directory(self, temp_dir):
        """Test listing files in existing directory."""
        # Create some test files
        (temp_dir / "file1.txt").touch()
        (temp_dir / "file2.txt").touch()
        (temp_dir / "subdir").mkdir()
        
        result = ZetaTools.list_files.func(str(temp_dir))
        
        assert "[FILE]" in result or "[DIR]" in result
        assert "file1.txt" in result or "file2.txt" in result
    
    def test_list_files_nonexistent_directory(self):
        """Test listing files in non-existent directory."""
        result = ZetaTools.list_files.func("/nonexistent/directory/xyz")
        assert "Error" in result
        assert "does not exist" in result
    
    def test_list_files_empty_directory(self, temp_dir):
        """Test listing files in empty directory."""
        result = ZetaTools.list_files.func(str(temp_dir))
        assert "empty" in result.lower() or len(result) == 0
    
    def test_list_files_error_handling(self):
        """Test error handling when listing files."""
        with patch('pathlib.Path.iterdir', side_effect=PermissionError("Access denied")):
            result = ZetaTools.list_files.func(".")
            assert "Error listing directory" in result

