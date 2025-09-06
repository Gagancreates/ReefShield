#!/usr/bin/env python3
"""
Phase 5 Integration Test: Frontend-Backend Integration
Tests the connection between React frontend and FastAPI backend
"""

import requests
import json
import time
import subprocess
import threading
from datetime import datetime
from pathlib import Path
import webbrowser

BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def test_backend_readiness():
    """Test if backend is ready for frontend integration"""
    print("🔧 Testing Backend Readiness for Frontend Integration")
    print("=" * 60)
    
    required_endpoints = [
        ("/health", "Basic health check"),
        ("/api/v1/health", "Enhanced health check"),
        ("/api/v1/reef-data", "Reef data endpoint"),
        ("/api/v1/combined-data", "Combined temperature data"),
        ("/api/v1/status", "System status"),
        ("/api/v1/scheduler/status", "Scheduler status"),
    ]
    
    success_count = 0
    for endpoint, description in required_endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"  ✅ {description}")
                success_count += 1
            else:
                print(f"  ❌ {description} - Status: {response.status_code}")
        except Exception as e:
            print(f"  ❌ {description} - Error: {e}")
    
    print(f"\n📊 Backend readiness: {success_count}/{len(required_endpoints)} endpoints working")
    return success_count == len(required_endpoints)

def test_cors_configuration():
    """Test CORS configuration for frontend requests"""
    print("\n🌐 Testing CORS Configuration")
    print("-" * 30)
    
    # Test preflight request
    try:
        response = requests.options(
            f"{BASE_URL}/api/v1/reef-data",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        if response.status_code in [200, 204]:
            cors_headers = {
                "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
            }
            
            print("  ✅ CORS preflight successful")
            print(f"  🔓 Allowed Origins: {cors_headers['Access-Control-Allow-Origin']}")
            print(f"  📝 Allowed Methods: {cors_headers['Access-Control-Allow-Methods']}")
            
            # Check if localhost:3000 is allowed
            if "localhost:3000" in str(cors_headers['Access-Control-Allow-Origin']) or cors_headers['Access-Control-Allow-Origin'] == "*":
                print("  ✅ Frontend origin is allowed")
                return True
            else:
                print("  ❌ Frontend origin not in allowed origins")
                return False
        else:
            print(f"  ❌ CORS preflight failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ CORS test error: {e}")
        return False

def test_api_data_format():
    """Test API data format compatibility with frontend"""
    print("\n📋 Testing API Data Format Compatibility")
    print("-" * 45)
    
    # Test reef data format
    try:
        response = requests.get(f"{BASE_URL}/api/v1/reef-data")
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields
            required_fields = [
                "location_name", "coordinates", "last_updated",
                "historical_data", "predictions", "risk_assessment"
            ]
            
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                print("  ✅ Reef data format is compatible")
                print(f"  📍 Location: {data['location_name']}")
                print(f"  📊 Historical readings: {len(data['historical_data'])}")
                print(f"  🔮 Predictions: {len(data['predictions'])}")
                print(f"  ⚠️ Risk level: {data['risk_assessment']['current_risk']}")
            else:
                print(f"  ❌ Missing required fields: {missing_fields}")
                return False
        else:
            print(f"  ❌ Failed to fetch reef data: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Reef data test error: {e}")
        return False
    
    # Test combined data format
    try:
        response = requests.get(f"{BASE_URL}/api/v1/combined-data")
        if response.status_code == 200:
            data = response.json()
            
            if "data" in data and len(data["data"]) > 0:
                print("  ✅ Combined data format is compatible")
                print(f"  📈 Data points: {len(data['data'])}")
                
                # Check temperature reading format
                sample_reading = data["data"][0]
                required_reading_fields = ["date", "temperature", "source"]
                missing_reading_fields = [field for field in required_reading_fields if field not in sample_reading]
                
                if not missing_reading_fields:
                    print("  ✅ Temperature reading format is compatible")
                else:
                    print(f"  ❌ Missing reading fields: {missing_reading_fields}")
                    return False
            else:
                print("  ❌ No data in combined data response")
                return False
        else:
            print(f"  ❌ Failed to fetch combined data: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Combined data test error: {e}")
        return False
    
    return True

def test_real_time_capabilities():
    """Test real-time data update capabilities"""
    print("\n⏱️ Testing Real-time Data Capabilities")
    print("-" * 40)
    
    # Test multiple requests to check for data freshness
    timestamps = []
    
    for i in range(3):
        try:
            response = requests.get(f"{BASE_URL}/api/v1/reef-data")
            if response.status_code == 200:
                data = response.json()
                timestamps.append(data.get("last_updated"))
                print(f"  📊 Request {i+1}: {data.get('last_updated', 'No timestamp')}")
            time.sleep(1)
        except Exception as e:
            print(f"  ❌ Request {i+1} failed: {e}")
            return False
    
    # Check if timestamps are present and reasonable
    valid_timestamps = [ts for ts in timestamps if ts]
    if len(valid_timestamps) == len(timestamps):
        print("  ✅ All responses include timestamps")
        print("  ✅ Real-time data capability confirmed")
        return True
    else:
        print(f"  ⚠️ Some responses missing timestamps ({len(valid_timestamps)}/{len(timestamps)})")
        return False

def check_frontend_files():
    """Check if frontend integration files exist"""
    print("\n📁 Checking Frontend Integration Files")
    print("-" * 40)
    
    frontend_root = Path("c:/Users/workspace/ReefShield/frontend")
    required_files = [
        "lib/services/apiClient.ts",
        "lib/services/backendRealtimeService.ts",
        "lib/hooks/useRealtimeData.ts",
        "components/backend-status.tsx",
        ".env.local"
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = frontend_root / file_path
        if full_path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - Missing")
            all_exist = False
    
    return all_exist

def run_integration_tests():
    """Run comprehensive integration tests"""
    print("🧪 ReefShield Frontend-Backend Integration Tests")
    print("=" * 60)
    print(f"🕐 Starting tests at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend not responding correctly")
            return False
        print("✅ Backend is running")
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        print("💡 Make sure the FastAPI backend is running on localhost:8000")
        return False
    
    # Run individual tests
    tests = [
        ("Backend Readiness", test_backend_readiness),
        ("CORS Configuration", test_cors_configuration),
        ("API Data Format", test_api_data_format),
        ("Real-time Capabilities", test_real_time_capabilities),
        ("Frontend Files", check_frontend_files),
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test failed with error: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Integration Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    print(f"\n📊 Overall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 All integration tests passed!")
        print("✨ Frontend is ready to connect to the backend")
        print("\n💡 Next steps:")
        print("  1. Start the Next.js frontend: cd frontend && npm run dev")
        print("  2. Open http://localhost:3000 in your browser")
        print("  3. Check the Backend Status component on the dashboard")
        return True
    else:
        print("⚠️ Some tests failed. Please fix the issues before proceeding.")
        return False

if __name__ == "__main__":
    success = run_integration_tests()
    
    if success:
        print("\n🚀 Integration testing complete!")
        print("Ready to start the frontend for live testing.")
    else:
        print("\n❌ Integration tests failed.")
        print("Please resolve the issues and try again.")