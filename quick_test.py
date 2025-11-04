#!/usr/bin/env python3
"""
Quick test script for ZETA
Run this to verify your ZETA installation is working correctly.
"""

import sys
import subprocess
from pathlib import Path

def run_command(cmd):
    """Run a command and return success status."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def print_status(test_name, passed):
    """Print test status."""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {test_name}")

def main():
    print("=" * 60)
    print("ZETA Quick Test Script")
    print("=" * 60)
    print()
    
    all_passed = True
    
    # Test 1: Python version
    print("Test 1: Checking Python version...")
    success, output, _ = run_command("python --version")
    if success:
        version = output.strip()
        print(f"  Found: {version}")
        # Check if version is 3.8+
        version_num = version.split()[1]
        major, minor = map(int, version_num.split('.')[:2])
        if major >= 3 and minor >= 8:
            print_status("Python version check", True)
        else:
            print_status("Python version check (need 3.8+)", False)
            all_passed = False
    else:
        print_status("Python version check", False)
        all_passed = False
    
    print()
    
    # Test 2: Ollama installation
    print("Test 2: Checking Ollama installation...")
    success, output, _ = run_command("ollama --version")
    if success:
        print(f"  Found: {output.strip()}")
        print_status("Ollama installation", True)
    else:
        print_status("Ollama installation", False)
        print("  ⚠️  Please install Ollama from https://ollama.ai/")
        all_passed = False
    
    print()
    
    # Test 3: Ollama service running
    print("Test 3: Checking if Ollama service is running...")
    success, output, _ = run_command("ollama list")
    if success:
        print("  Ollama service is running")
        print_status("Ollama service", True)
    else:
        print_status("Ollama service", False)
        print("  ⚠️  Please start Ollama: ollama serve")
        all_passed = False
    
    print()
    
    # Test 4: Check for MiniMax M2 model
    print("Test 4: Checking for MiniMax M2 model...")
    success, output, _ = run_command("ollama list")
    if success and "minimax-m2" in output.lower():
        print("  MiniMax M2 model found")
        print_status("Model availability", True)
    else:
        print_status("Model availability", False)
        print("  ⚠️  Please pull the model: ollama pull minimax-m2:cloud")
        all_passed = False
    
    print()
    
    # Test 5: Check Python dependencies
    print("Test 5: Checking Python dependencies...")
    required_packages = ['click', 'langchain_ollama', 'langchain', 'langgraph', 'rich']
    missing_packages = []
    
    for package in required_packages:
        # Handle package name differences
        import_name = package.replace('-', '_')
        try:
            __import__(import_name)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} (missing)")
            missing_packages.append(package)
    
    if missing_packages:
        print_status("Python dependencies", False)
        print(f"  ⚠️  Install missing packages: pip install {' '.join(missing_packages)}")
        all_passed = False
    else:
        print_status("Python dependencies", True)
    
    print()
    
    # Test 6: Check if ZETA module exists
    print("Test 6: Checking ZETA module...")
    zeta_file = Path("zeta.py")
    if zeta_file.exists():
        print("  ✅ zeta.py found")
        print_status("ZETA module", True)
    else:
        print("  ❌ zeta.py not found")
        print_status("ZETA module", False)
        all_passed = False
    
    print()
    
    # Test 7: Check if setup.py exists
    print("Test 7: Checking setup.py...")
    setup_file = Path("setup.py")
    if setup_file.exists():
        print("  ✅ setup.py found")
        print_status("Setup file", True)
    else:
        print("  ❌ setup.py not found")
        print_status("Setup file", False)
        all_passed = False
    
    print()
    
    # Test 8: Try importing ZETA (if installed)
    print("Test 8: Checking ZETA installation...")
    try:
        import zeta
        print("  ✅ ZETA module can be imported")
        print_status("ZETA installation", True)
    except ImportError:
        print("  ⚠️  ZETA not installed yet")
        print("  💡 Run: pip install -e .")
        print_status("ZETA installation", False)
        # Don't fail the test, just warn
    
    print()
    print("=" * 60)
    
    if all_passed:
        print("✅ All critical tests passed!")
        print()
        print("Next steps:")
        print("  1. Install ZETA: pip install -e .")
        print("  2. Test basic command: zeta --help")
        print("  3. Run a simple task: zeta run 'list files'")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print()
        print("Common fixes:")
        print("  - Install Ollama: https://ollama.ai/")
        print("  - Pull model: ollama pull minimax-m2:cloud")
        print("  - Install dependencies: pip install click langchain-ollama langchain langgraph rich")
        print("  - Install ZETA: pip install -e .")
    
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

