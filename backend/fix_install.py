"""
Fix installation issues for Python 3.12+ environments.
"""
import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"   ✅ {description} completed")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ {description} failed:")
        if e.stderr:
            print(f"   Error: {e.stderr.strip()}")
        return False

def main():
    """Fix common installation issues."""
    print("🛠️ Fixing installation issues...")
    print("=" * 50)
    
    # Check Python version
    python_version = sys.version_info
    print(f"🐍 Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # For Python 3.12+, we need to handle the distutils issue
    if python_version >= (3, 12):
        print("⚠️ Python 3.12+ detected - applying fixes for distutils removal")
        
        # Install setuptools first (provides distutils replacement)
        if not run_command("pip install --upgrade setuptools", "Upgrading setuptools"):
            return False
    
    # Upgrade pip first
    if not run_command("pip install --upgrade pip", "Upgrading pip"):
        print("   ⚠️ Pip upgrade failed, continuing anyway...")
    
    # Install packages that commonly have pre-built wheels first
    core_packages = [
        "numpy==1.26.4",
        "pandas==2.1.4", 
        "pydantic==2.5.0",
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0"
    ]
    
    print("\n📦 Installing core packages with pre-built wheels...")
    for package in core_packages:
        if not run_command(f"pip install {package}", f"Installing {package.split('==')[0]}"):
            print(f"   ⚠️ Failed to install {package}, trying without version pin...")
            base_name = package.split('==')[0]
            run_command(f"pip install {base_name}", f"Installing {base_name} (latest)")
    
    # Install remaining packages
    remaining_packages = [
        "scikit-learn==1.3.2",
        "xarray==2023.12.0",
        "aiohttp==3.9.1",
        "python-multipart==0.0.6",
        "python-dotenv==1.0.0",
        "aiofiles==23.2.1",
        "httpx==0.25.2"
    ]
    
    print("\n📦 Installing remaining packages...")
    for package in remaining_packages:
        if not run_command(f"pip install {package}", f"Installing {package.split('==')[0]}"):
            print(f"   ⚠️ Failed to install {package}")
    
    # Test imports
    print("\n🧪 Testing imports...")
    if run_command(f"{sys.executable} test_imports.py", "Testing imports"):
        print("\n🎉 Installation fixed successfully!")
        print("\n🚀 Next steps:")
        print("   python run.py")
        return True
    else:
        print("\n❌ Some imports still failing. Check the test output above.")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n💡 If issues persist:")
        print("   1. Try creating a fresh virtual environment")
        print("   2. Use Python 3.11 instead of 3.12+")
        print("   3. Install packages individually: pip install fastapi uvicorn pydantic")
        sys.exit(1)