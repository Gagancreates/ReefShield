"""
Test CORS configuration for the backend API.
"""
import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_cors():
    """Test CORS configuration."""
    print("🧪 Testing CORS Configuration...\n")
    
    # Test 1: Simple GET request
    print("1️⃣ Testing simple GET request...")
    try:
        response = requests.get(f"{API_BASE_URL}/test-cors")
        if response.status_code == 200:
            print("   ✅ GET request successful")
            print(f"   📄 Response: {response.json()}")
        else:
            print(f"   ❌ GET request failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ GET request error: {e}")
    
    # Test 2: OPTIONS request (CORS preflight)
    print("\n2️⃣ Testing OPTIONS request (CORS preflight)...")
    try:
        headers = {
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        response = requests.options(f"{API_BASE_URL}/api/temperature/analysis", headers=headers)
        print(f"   📊 OPTIONS response status: {response.status_code}")
        print(f"   📋 Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("   ✅ OPTIONS request successful")
        else:
            print(f"   ❌ OPTIONS request failed: {response.status_code}")
            print(f"   📄 Response text: {response.text}")
    except Exception as e:
        print(f"   ❌ OPTIONS request error: {e}")
    
    # Test 3: Actual API endpoint
    print("\n3️⃣ Testing actual API endpoint...")
    try:
        headers = {
            'Origin': 'http://localhost:3000',
            'Content-Type': 'application/json'
        }
        response = requests.get(f"{API_BASE_URL}/api/temperature/locations", headers=headers)
        print(f"   📊 API response status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ API request successful")
            data = response.json()
            print(f"   📍 Found {len(data.get('locations', []))} locations")
        else:
            print(f"   ❌ API request failed: {response.status_code}")
            print(f"   📄 Response text: {response.text}")
    except Exception as e:
        print(f"   ❌ API request error: {e}")

if __name__ == "__main__":
    test_cors()