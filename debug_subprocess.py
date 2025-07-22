#!/usr/bin/env python3
"""
Test script to debug the subprocess environment issue
"""

import subprocess
import json
import os

def test_subprocess_environment():
    """Test what environment the subprocess sees"""
    
    # Test 1: Check Python path in subprocess
    print("=== Testing subprocess Python environment ===")
    
    try:
        result = subprocess.run([
            'python3', '-c', 
            'import sys; print("Python executable:", sys.executable); print("Python path:"); [print(p) for p in sys.path]'
        ], capture_output=True, text=True, timeout=10)
        
        print("STDOUT:")
        print(result.stdout)
        print("STDERR:")
        print(result.stderr)
        print("Return code:", result.returncode)
        
    except Exception as e:
        print(f"Error testing subprocess: {e}")
    
    # Test 2: Check environment variables
    print("\n=== Testing environment variables ===")
    
    try:
        result = subprocess.run([
            'python3', '-c', 
            'import os; print("GEMINI_API_KEY:", "FOUND" if os.environ.get("GEMINI_API_KEY") else "NOT FOUND")'
        ], capture_output=True, text=True, timeout=10)
        
        print("STDOUT:")
        print(result.stdout)
        print("STDERR:")
        print(result.stderr)
        
    except Exception as e:
        print(f"Error testing environment: {e}")
    
    # Test 3: Try importing emergentintegrations
    print("\n=== Testing emergentintegrations import ===")
    
    try:
        result = subprocess.run([
            'python3', '-c', 
            'try:\n    from emergentintegrations.llm.chat import LlmChat\n    print("SUCCESS: emergentintegrations imported")\nexcept ImportError as e:\n    print(f"IMPORT ERROR: {e}")'
        ], capture_output=True, text=True, timeout=10)
        
        print("STDOUT:")
        print(result.stdout)
        print("STDERR:")
        print(result.stderr)
        
    except Exception as e:
        print(f"Error testing import: {e}")

if __name__ == "__main__":
    test_subprocess_environment()