"""
Installation script for the reef temperature monitoring API.
"""
import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"   ✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False

def main():
    """Main installation process."""
    print("🚀 Installing Reef Temperature Monitoring API...")
    print("=" * 50)
    
    # Check Python version
    python_version = sys.version_info
    print(f"🐍 Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        return False
    
    # Install packages one by one to identify issues
    packages = [
        "fastapi>=0.100.0,<0.105.0",
        "uvicorn[standard]>=0.23.0,<0.25.0", 
        "pydantic>=2.4.0,<2.6.0",
        "pandas>=2.0.0,<2.2.0",
        "numpy>=1.24.0,<1.26.0",
        "scikit-learn>=1.3.0,<1.4.0",
        "xarray>=2023.1.0",
        "aiohttp>=3.8.0",
        "python-multipart>=0.0.6",
        "python-dotenv>=1.0.0",
        "aiofiles>=23.0.0",
        "httpx>=0.24.0"
    ]
    
    failed_packages = []
    
    for package in packages:
        if not run_command(f"pip install {package}", f"Installing {package.split('>=')[0]}"):
            failed_packages.append(package)
    
    if failed_packages:
        print(f"\n❌ Failed to install: {', '.join(failed_packages)}")
        print("\n🔧 Try installing manually:")
        for pkg in failed_packages:
            print(f"   pip install {pkg}")
        return False
    
    # Test imports
    print("\n🧪 Testing imports...")
    if run_command(f"{sys.executable} test_imports.py", "Testing imports"):
        print("\n🎉 Installation completed successfully!")
        print("\n🚀 Next steps:")
        print("   1. python run.py")
        print("   2. Visit http://localhost:8000/docs")
        return True
    else:
        print("\n❌ Import test failed. Please check the error messages above.")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n💡 If you continue to have issues, try:")
        print("   1. Create a fresh virtual environment")
        print("   2. pip install --upgrade pip")
        print("   3. Run this script again")
        sys.exit(1)