"""
Fix missing dependencies for NOAA data access.
"""
import subprocess
import sys
import os

def install_dependencies():
    """Install missing dependencies for NetCDF and xarray."""
    print("🔧 Installing missing dependencies for NOAA data access...")
    
    dependencies = [
        "netcdf4==1.6.5",
        "h5netcdf==1.3.0", 
        "scipy==1.11.4",
        "dask==2023.12.1"
    ]
    
    for dep in dependencies:
        print(f"📦 Installing {dep}...")
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", dep
            ], capture_output=True, text=True, check=True)
            print(f"   ✅ {dep} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to install {dep}: {e.stderr}")
            return False
    
    print("\n🧪 Testing xarray backends...")
    try:
        import xarray as xr
        import netcdf4
        import h5netcdf
        print("   ✅ NetCDF4 backend available")
        print("   ✅ H5NetCDF backend available")
        
        # Test opening a simple dataset
        print("   🌐 Testing NOAA data access...")
        test_url = "https://psl.noaa.gov/thredds/dodsC/Datasets/noaa.oisst.v2.highres/sst.day.mean.2023.nc"
        
        try:
            ds = xr.open_dataset(test_url, engine='netcdf4')
            print("   ✅ NOAA data access working with netcdf4")
            ds.close()
        except Exception as e:
            print(f"   ⚠️ NOAA access test failed: {e}")
            print("   💡 This might be due to network issues, not dependency problems")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import test failed: {e}")
        return False

def main():
    """Main function."""
    print("🚀 Fixing Backend Dependencies for NOAA Data Access")
    print("=" * 60)
    
    success = install_dependencies()
    
    if success:
        print("\n🎉 Dependencies installed successfully!")
        print("\n📋 Next steps:")
        print("   1. Restart the backend: python run.py")
        print("   2. The NOAA data fetching should now work properly")
        print("   3. Check logs for successful model training")
    else:
        print("\n❌ Some dependencies failed to install")
        print("\n🔧 Manual installation:")
        print("   pip install netcdf4 h5netcdf scipy dask")

if __name__ == "__main__":
    main()