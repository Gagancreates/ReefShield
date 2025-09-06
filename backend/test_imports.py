"""
Test script to check if all imports work correctly.
"""
import sys
import traceback

def test_imports():
    """Test all the imports used in the application."""
    print("🧪 Testing imports...")
    
    try:
        print("1. Testing basic imports...")
        import datetime
        import pandas as pd
        import numpy as np
        print("   ✅ Basic imports OK")
        
        print("2. Testing FastAPI imports...")
        from fastapi import FastAPI, HTTPException
        from fastapi.middleware.cors import CORSMiddleware
        print("   ✅ FastAPI imports OK")
        
        print("3. Testing Pydantic imports...")
        from pydantic import BaseModel, Field
        print("   ✅ Pydantic imports OK")
        
        print("4. Testing sklearn imports...")
        from sklearn.ensemble import RandomForestRegressor
        print("   ✅ Scikit-learn imports OK")
        
        print("5. Testing xarray imports...")
        import xarray as xr
        print("   ✅ XArray imports OK")
        
        print("6. Testing aiohttp imports...")
        import aiohttp
        print("   ✅ Aiohttp imports OK")
        
        print("7. Testing app imports...")
        sys.path.insert(0, 'app')
        from app.config.locations import REEF_LOCATIONS
        print(f"   ✅ App config imports OK - {len(REEF_LOCATIONS)} locations loaded")
        
        print("\n🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\n✅ Ready to start the API server!")
        print("Run: python run.py")
    else:
        print("\n❌ Please fix the import issues first.")
        print("Try: pip install -r requirements.txt")