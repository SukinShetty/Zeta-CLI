"""Tests for benchmark suite."""

import pytest
from tests.benchmarks import BenchmarkSuite


class TestBenchmarks:
    """Test benchmark suite functionality."""
    
    def test_benchmark_vague_detection(self):
        """Test vague detection benchmark."""
        suite = BenchmarkSuite()
        result = suite.benchmark_vague_detection(iterations=10)
        
        assert 'total_time' in result
        assert 'avg_time_ms' in result
        assert 'iterations' in result
        assert result['iterations'] == 10
        assert result['total_time'] > 0
    
    def test_benchmark_tool_execution(self):
        """Test tool execution benchmark."""
        suite = BenchmarkSuite()
        result = suite.benchmark_tool_execution(iterations=10)
        
        assert 'total_time' in result
        assert 'avg_time_ms' in result
        assert 'iterations' in result
        assert result['iterations'] == 10
    
    def test_benchmark_file_operations(self):
        """Test file operations benchmark."""
        suite = BenchmarkSuite()
        result = suite.benchmark_file_operations(iterations=10)
        
        assert 'write_total' in result
        assert 'read_total' in result
        assert 'iterations' in result
        assert result['iterations'] == 10
    
    def test_benchmark_agent_initialization(self):
        """Test agent initialization benchmark."""
        suite = BenchmarkSuite()
        result = suite.benchmark_agent_initialization(iterations=5)
        
        assert 'total_time' in result
        assert 'avg_time_ms' in result
        assert 'iterations' in result
        assert result['iterations'] == 5
    
    def test_benchmark_tool_parsing(self):
        """Test tool parsing benchmark."""
        suite = BenchmarkSuite()
        result = suite.benchmark_tool_parsing(iterations=10)
        
        assert 'total_time' in result
        assert 'avg_time_ms' in result
        assert 'iterations' in result
        assert result['iterations'] == 10
    
    def test_run_all_benchmarks(self):
        """Test running all benchmarks."""
        suite = BenchmarkSuite()
        results = suite.run_all()
        
        assert len(results) == 5
        assert 'vague_detection' in results
        assert 'tool_execution' in results
        assert 'file_operations' in results
        assert 'agent_init' in results
        assert 'tool_parsing' in results

