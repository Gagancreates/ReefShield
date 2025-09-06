"""
Test NOAA data access with xarray.
"""
import xarray as xr
import datetime as dt
import sys
import os

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_noaa_access():
    """Test accessing NOAA OISST data."""
    print("🌊 Testing NOAA OISST data access...\n")
    
    # Test coordinates (Jolly Buoy)
    lat, lon = 11.495, 92.610
    test_year = 2023
    
    print(f"📍 Testing location: {lat}°N, {lon}°E")
    print(f"📅 Testing year: {test_year}")
    
    # Test URL
    url = f"https://psl.noaa.gov/thredds/dodsC/Datasets/noaa.oisst.v2.highres/sst.day.mean.{test_year}.nc"
    print(f"🔗 URL: {url}")
    
    try:
        print("\n1️⃣ Opening NOAA dataset...")
        ds = xr.open_dataset(url)
        print("   ✅ Dataset opened successfully")
        
        print("\n2️⃣ Checking dataset structure...")
        print(f"   📊 Variables: {list(ds.data_vars.keys())}")
        print(f"   📏 Dimensions: {dict(ds.dims)}")
        
        if 'sst' in ds.data_vars:
            print("   ✅ SST variable found")
            
            print("\n3️⃣ Testing data selection...")
            # Select a small time range
            start_date = f"{test_year}-01-01"
            end_date = f"{test_year}-01-07"
            
            sst_subset = ds["sst"].sel(
                time=slice(start_date, end_date),
                lat=lat,
                lon=lon,
                method="nearest"
            )
            
            print(f"   📅 Selected time range: {start_date} to {end_date}")
            print(f"   📍 Selected coordinates: {sst_subset.lat.values}°N, {sst_subset.lon.values}°E")
            
            print("\n4️⃣ Loading data...")
            data = sst_subset.load()
            print(f"   📊 Data shape: {data.shape}")
            print(f"   🌡️ Sample temperatures: {data.values[:3]} K")
            
            # Convert to Celsius
            temps_celsius = data.values - 273.15
            print(f"   🌡️ Sample temperatures (°C): {temps_celsius[:3]}")
            
            print("\n✅ NOAA data access test PASSED!")
            print("🎯 xarray can successfully fetch NOAA OISST data")
            
        else:
            print("   ❌ SST variable not found in dataset")
            return False
            
        ds.close()
        return True
        
    except Exception as e:
        print(f"\n❌ NOAA data access test FAILED: {e}")
        print("\n🔧 Possible solutions:")
        print("   1. Check internet connection")
        print("   2. Install missing dependencies: python fix_xarray_dependencies.py")
        print("   3. Verify NOAA server availability")
        print("   4. Check firewall/proxy settings")
        return False

def test_model_integration():
    """Test the temperature model with real data."""
    print("\n🤖 Testing temperature model integration...\n")
    
    try:
        from app.models.temperature import LocationTemperatureModel
        
        print("1️⃣ Creating temperature model...")
        model = LocationTemperatureModel(11.495, 92.610, "test-location")
        print("   ✅ Model created successfully")
        
        print("\n2️⃣ Testing recent data fetch...")
        import asyncio
        
        async def test_fetch():
            recent_data = await model.get_recent_data(days_back=7)
            return recent_data
        
        recent_data = asyncio.run(test_fetch())
        
        if not recent_data.empty:
            print(f"   ✅ Fetched {len(recent_data)} days of data")
            print(f"   📅 Date range: {recent_data['Date'].min()} to {recent_data['Date'].max()}")
            print(f"   🌡️ Temperature range: {recent_data['SST'].min():.1f}°C to {recent_data['SST'].max():.1f}°C")
            print("\n✅ Model integration test PASSED!")
            return True
        else:
            print("   ❌ No data fetched")
            return False
            
    except Exception as e:
        print(f"   ❌ Model integration test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 NOAA Data Access Test Suite")
    print("=" * 40)
    
    # Test 1: Basic NOAA access
    noaa_success = test_noaa_access()
    
    # Test 2: Model integration (only if NOAA access works)
    if noaa_success:
        model_success = test_model_integration()
        
        if model_success:
            print("\n🎉 All tests PASSED!")
            print("🚀 Ready to run the backend with real NOAA data")
        else:
            print("\n⚠️ NOAA access works but model integration failed")
    else:
        print("\n❌ NOAA access failed - fix dependencies first")
        print("🔧 Run: python fix_xarray_dependencies.py")