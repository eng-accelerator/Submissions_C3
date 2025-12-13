"""
Check if Python version is compatible with this project.
Python 3.14+ is NOT supported due to Pydantic V1 compatibility issues.
"""
import sys
import io

# Fix Windows console encoding issues
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def check_python_version():
    version = sys.version_info
    major = version.major
    minor = version.minor
    
    print(f"Python version: {major}.{minor}.{version.micro}")
    
    if major == 3 and 9 <= minor <= 13:
        print("[OK] Python version is compatible!")
        return True
    elif major == 3 and minor >= 14:
        print("[ERROR] Python 3.14+ is NOT compatible with this project.")
        print("   LangChain uses Pydantic V1 which doesn't support Python 3.14+")
        print("   Please use Python 3.9 - 3.13 (recommended: 3.11 or 3.12)")
        print("   Attempting to run anyway, but errors may occur...")
        return False  # Return False but allow continuation
    else:
        print("[WARNING] Python version may not be compatible.")
        print("   Recommended: Python 3.9 - 3.13")
        return False

if __name__ == "__main__":
    if not check_python_version():
        sys.exit(1)

