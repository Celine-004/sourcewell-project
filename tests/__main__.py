"""
SourceWell Test Suite - Module Execution Entry Point
"""

from . import run_full_suite
import sys

def main():
    """Execute SourceWell test suite from command line."""
    try:
        result = run_full_suite(verbose=True)
        success = result.get('overall_success', False)
        
        if success:
            print(f"\n SourceWell v{result.get('version', 'Unknown')}: ALL TESTS PASSED")
            sys.exit(0)
        else:
            print(f"\n SourceWell v{result.get('version', 'Unknown')}: SOME TESTS FAILED")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n SourceWell Test Execution Error: {e}")
        sys.exit(2)

if __name__ == "__main__":
    main()
