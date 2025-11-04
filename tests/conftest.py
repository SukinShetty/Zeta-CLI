"""Pytest configuration and fixtures."""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock
from zeta import ZetaTools, ZetaLogger, ZetaAgent


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_file(temp_dir):
    """Create a sample file for testing."""
    file_path = temp_dir / "test.txt"
    file_path.write_text("Hello, ZETA!")
    return file_path


@pytest.fixture
def mock_llm():
    """Mock Ollama LLM."""
    mock = Mock()
    mock.invoke.return_value = Mock(content="Mocked LLM response")
    return mock


@pytest.fixture
def agent_normal(mock_llm):
    """Create ZetaAgent instance in normal mode."""
    agent = ZetaAgent(teach_mode=False, critic_mode=False)
    agent.llm = mock_llm
    return agent


@pytest.fixture
def agent_teach(mock_llm):
    """Create ZetaAgent instance in teaching mode."""
    agent = ZetaAgent(teach_mode=True, critic_mode=False)
    agent.llm = mock_llm
    return agent


@pytest.fixture
def agent_critic(mock_llm):
    """Create ZetaAgent instance in critic mode."""
    agent = ZetaAgent(teach_mode=False, critic_mode=True)
    agent.llm = mock_llm
    return agent


@pytest.fixture
def clean_log():
    """Ensure clean log file for tests."""
    log_path = Path("zeta_log.md")
    if log_path.exists():
        log_path.unlink()
    yield
    if log_path.exists():
        log_path.unlink()

