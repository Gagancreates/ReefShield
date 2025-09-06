"""
Fix xarray dependencies for NOAA data access.
"""
import subprocess
import sys
import importlib

def check_package(package_name):
    """Check if a package is installed."""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

def install_package(package):
    """Install a package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    """Install missing xarray dependencies."""
    print("🔧 Fixing xarray dependencies for NOAA data access...\n")
    
    # Critical packages for xarray NetCDF support
    critical_packages = [
        ("netcdf4", "netcdf4==1.6.5"),
        ("h5netcdf", "h5netcdf==1.3.0"), 
        ("scipy", "scipy==1.11.4"),
        ("cftime", "cftime==1.6.2"),
        ("bottleneck", "bottleneck==1.3.7"),
        ("dask", "dask==2023.12.1"),
    ]
    
    # Optional packages for better performance
    optional_packages = [
        ("pydap", "pydap==3.4.0"),
    ]
    
    missing_critical = []
    missing_optional = []
    
    # Check critical packages
    print("📋 Checking critical packages...")
    for import_name, pip_name in critical_packages:
        if check_package(import_name):
            print(f"   ✅ {import_name} - installed")
        else:
            print(f"   ❌ {import_name} - missing")
            missing_critical.append(pip_name)
    
    # Check optional packages
    print("\n📋 Checking optional packages...")
    for import_name, pip_name in optional_packages:
        if check_package(import_name):
            print(f"   ✅ {import_name} - installed")
        else:
            print(f"   ⚠️ {import_name} - missing (optional)")
            missing_optional.append(pip_name)
    
    # Install missing packages
    if missing_critical:
        print(f"\n🔧 Installing {len(missing_critical)} critical packages...")
        for package in missing_critical:
            print(f"   📦 Installing {package}...")
            if install_package(package):
                print(f"   ✅ {package} installed successfully")
            else:
                print(f"   ❌ Failed to install {package}")
    
    if missing_optional:
        print(f"\n🔧 Installing {len(missing_optional)} optional packages...")
        for package in missing_optional:
            print(f"   📦 Installing {package}...")
            if install_package(package):
                print(f"   ✅ {package} installed successfully")
            else:
                print(f"   ⚠️ Failed to install {package} (optional)")
    
    if not missing_critical and not missing_optional:
        print("\n🎉 All xarray dependencies are already installed!")
    
    # Test xarray functionality
    print("\n🧪 Testing xarray functionality...")
    try:
        import xarray as xr
        import netcdf4
        import numpy as np
        
        print("   ✅ xarray imported successfully")
        print("   ✅ netcdf4 imported successfully")
        
        # Test creating a simple dataset
        data = xr.Dataset({
            'temperature': (['x', 'y'], np.random.rand(2, 3))
        })
        print("   ✅ xarray dataset creation works")
        
        print("\n🎯 xarray is ready for NOAA data access!")
        print("\n💡 Next steps:")
        print("   1. Restart the backend: python run.py")
        print("   2. Check logs for successful NOAA data fetching")
        print("   3. Verify real temperature predictions in frontend")
        
    except Exception as e:
        print(f"   ❌ xarray test failed: {e}")
        print("\n🔧 Try manually installing:")
        print("   pip install netcdf4 h5netcdf scipy cftime bottleneck dask")

if __name__ == "__main__":
    main()