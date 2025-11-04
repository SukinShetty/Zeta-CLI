"""Performance benchmarks for ZETA."""

import time
import statistics
from unittest.mock import Mock, patch
from zeta import ZetaAgent, ZetaTools, detect_vague_task


class BenchmarkSuite:
    """Performance benchmarking suite."""
    
    def __init__(self):
        self.results = {}
    
    def benchmark_vague_detection(self, iterations=1000):
        """Benchmark vague task detection performance."""
        tasks = [
            "make app",
            "create something",
            "build a web application with React and Node.js",
            "generate a Python script to parse CSV files",
            "make",
            "create a full-stack application",
        ] * (iterations // 6 + 1)
        
        start = time.perf_counter()
        for task in tasks[:iterations]:
            detect_vague_task(task)
        end = time.perf_counter()
        
        elapsed = end - start
        avg_time = elapsed / iterations
        self.results['vague_detection'] = {
            'total_time': elapsed,
            'avg_time_ms': avg_time * 1000,
            'iterations': iterations,
            'ops_per_sec': iterations / elapsed
        }
        return self.results['vague_detection']
    
    def benchmark_tool_execution(self, iterations=100):
        """Benchmark tool execution performance."""
        agent = ZetaAgent()
        
        # Mock LLM to avoid actual API calls
        agent.llm = Mock()
        agent.llm.invoke = Mock(return_value=Mock(content="Test response"))
        
        with patch('builtins.open', create=True):
            start = time.perf_counter()
            for _ in range(iterations):
                agent.execute_tool("read_file", {"file_path": "test.txt"})
            end = time.perf_counter()
        
        elapsed = end - start
        self.results['tool_execution'] = {
            'total_time': elapsed,
            'avg_time_ms': (elapsed / iterations) * 1000,
            'iterations': iterations,
            'ops_per_sec': iterations / elapsed
        }
        return self.results['tool_execution']
    
    def benchmark_file_operations(self, iterations=100):
        """Benchmark file operation performance."""
        import tempfile
        from pathlib import Path
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "benchmark.txt"
            
            # Write operations
            start = time.perf_counter()
            for i in range(iterations):
                test_file.write_text(f"Line {i}\n" * 10)
            write_time = time.perf_counter() - start
            
            # Read operations
            start = time.perf_counter()
            for _ in range(iterations):
                test_file.read_text()
            read_time = time.perf_counter() - start
            
            self.results['file_operations'] = {
                'write_total': write_time,
                'write_avg_ms': (write_time / iterations) * 1000,
                'read_total': read_time,
                'read_avg_ms': (read_time / iterations) * 1000,
                'iterations': iterations
            }
            return self.results['file_operations']
    
    def benchmark_agent_initialization(self, iterations=100):
        """Benchmark agent initialization time."""
        times = []
        
        for _ in range(iterations):
            start = time.perf_counter()
            agent = ZetaAgent()
            end = time.perf_counter()
            times.append(end - start)
        
        self.results['agent_init'] = {
            'total_time': sum(times),
            'avg_time_ms': statistics.mean(times) * 1000,
            'min_time_ms': min(times) * 1000,
            'max_time_ms': max(times) * 1000,
            'median_time_ms': statistics.median(times) * 1000,
            'iterations': iterations
        }
        return self.results['agent_init']
    
    def benchmark_tool_parsing(self, iterations=1000):
        """Benchmark tool call parsing performance."""
        agent = ZetaAgent()
        
        tool_calls = [
            'TOOL_CALL: read_file(file_path="test.txt")',
            'TOOL_CALL: write_file(file_path="app.py", content="print(\\"hello\\")")',
            'TOOL_CALL: run_command(command="ls -la")',
            'TOOL_CALL: list_files(directory=".")',
        ] * (iterations // 4 + 1)
        
        start = time.perf_counter()
        for call in tool_calls[:iterations]:
            agent.parse_tool_calls(call)
        end = time.perf_counter()
        
        elapsed = end - start
        self.results['tool_parsing'] = {
            'total_time': elapsed,
            'avg_time_ms': (elapsed / iterations) * 1000,
            'iterations': iterations,
            'ops_per_sec': iterations / elapsed
        }
        return self.results['tool_parsing']
    
    def run_all(self):
        """Run all benchmarks."""
        print("Running performance benchmarks...\n")
        
        print("1. Vague Detection Benchmark...")
        self.benchmark_vague_detection(1000)
        
        print("2. Tool Execution Benchmark...")
        self.benchmark_tool_execution(100)
        
        print("3. File Operations Benchmark...")
        self.benchmark_file_operations(100)
        
        print("4. Agent Initialization Benchmark...")
        self.benchmark_agent_initialization(100)
        
        print("5. Tool Parsing Benchmark...")
        self.benchmark_tool_parsing(1000)
        
        print("\n" + "="*60)
        print("BENCHMARK RESULTS")
        print("="*60)
        
        for name, result in self.results.items():
            print(f"\n{name.upper().replace('_', ' ')}:")
            for key, value in result.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.4f}")
                else:
                    print(f"  {key}: {value}")
        
        return self.results


if __name__ == "__main__":
    suite = BenchmarkSuite()
    suite.run_all()

