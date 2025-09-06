"""
Test script for Phase 3 API endpoints
"""

import asyncio
import json
import requests
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
    """Test a single API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        return {
            "status_code": response.status_code,
            "success": response.status_code < 400,
            "data": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
            "response_time": response.elapsed.total_seconds()
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

def test_server_connectivity():
    """Test if server is running and accessible"""
    print("🔌 Testing server connectivity...")
    
    for attempt in range(5):
        try:
            response = requests.get(f"{BASE_URL}/", timeout=5)
            if response.status_code == 200:
                print(f"  ✅ Server is running and accessible")
                return True
        except Exception as e:
            print(f"  ⏳ Attempt {attempt + 1}/5 failed: {e}")
            time.sleep(2)
    
    print(f"  ❌ Server is not accessible at {BASE_URL}")
    return False

def analyze_response_data(endpoint: str, data: Dict[str, Any]):
    """Analyze and display key information from response data"""
    if not isinstance(data, dict):
        return
    
    if endpoint == "/api/v1/reef-data":
        print(f"    📍 Location: {data.get('location_name', 'Unknown')}")
        if 'coordinates' in data:
            coords = data['coordinates']
            print(f"    🗺️ Coordinates: {coords.get('lat', 'N/A')}, {coords.get('lon', 'N/A')}")
        
        historical = data.get('historical_data', [])
        predictions = data.get('predictions', [])
        print(f"    📊 Historical readings: {len(historical)}")
        print(f"    🔮 Predictions: {len(predictions)}")
        
        if 'risk_assessment' in data:
            risk = data['risk_assessment']
            print(f"    ⚠️ Risk level: {risk.get('current_risk', 'Unknown')}")
            print(f"    📈 Trend: {risk.get('trend', 'Unknown')}")
            print(f"    🌡️ DHW: {risk.get('dhw', 'N/A')}")
    
    elif endpoint == "/api/v1/combined-data":
        print(f"    📍 Location: {data.get('location_name', 'Unknown')}")
        readings = data.get('data', [])
        print(f"    📈 Combined readings: {len(readings)}")
        
        if readings:
            historical_count = sum(1 for r in readings if r.get('source') == 'Historical')
            predicted_count = sum(1 for r in readings if r.get('source') == 'Predicted')
            print(f"    📊 Historical: {historical_count}, Predicted: {predicted_count}")
    
    elif endpoint == "/api/v1/status":
        print(f"    🔧 API Status: {data.get('api_status', 'Unknown')}")
        
        model_status = data.get('model_status', {})
        print(f"    🤖 Model running: {model_status.get('is_running', 'Unknown')}")
        print(f"    ⏰ Last run: {model_status.get('last_run', 'Never')}")
        
        file_status = data.get('data_files_status', {})
        files_ok = sum(1 for f in file_status.values() if f.get('exists', False))
        print(f"    📁 Data files: {files_ok}/{len(file_status)} exist")

def main():
    """Test all API endpoints"""
    print("🧪 ReefShield Backend - Phase 3 API Testing")
    print("=" * 50)
    
    # Check server connectivity first
    if not test_server_connectivity():
        print("\n❌ Cannot proceed with testing - server is not accessible")
        print("💡 Make sure to start the FastAPI server first:")
        print("   cd backend && python main.py")
        return False
    
    print(f"\n🚀 Starting API endpoint tests...")
    
    endpoints = [
        ("/", "GET", "Root endpoint"),
        ("/health", "GET", "Basic health check"),
        ("/api/v1/health", "GET", "Enhanced health check"),
        ("/api/v1/reef-data", "GET", "Complete reef data"),
        ("/api/v1/combined-data", "GET", "14-day combined data"),
        ("/api/v1/status", "GET", "System status"),
        ("/api/v1/cache-info", "GET", "Cache information"),
        ("/api/v1/run-model", "POST", "Trigger model run", {"force": False, "notify": True}),
    ]
    
    results = {}
    
    for endpoint_info in endpoints:
        endpoint = endpoint_info[0]
        method = endpoint_info[1]
        description = endpoint_info[2]
        data = endpoint_info[3] if len(endpoint_info) > 3 else None
        
        print(f"\n🔍 Testing {method} {endpoint}")
        print(f"    📝 {description}")
        
        result = test_endpoint(endpoint, method, data)
        results[endpoint] = result
        
        if result.get('success'):
            print(f"    ✅ SUCCESS ({result.get('status_code', 'N/A')})")
            print(f"    ⏱️ Response time: {result.get('response_time', 0):.3f}s")
            
            # Analyze response data
            response_data = result.get('data', {})
            analyze_response_data(endpoint, response_data)
            
        else:
            print(f"    ❌ FAILED: {result.get('error', 'Unknown error')}")
            if 'status_code' in result:
                print(f"    📊 Status code: {result['status_code']}")
    
    # Summary
    print(f"\n📋 Test Summary:")
    print("=" * 30)
    
    passed = sum(1 for r in results.values() if r.get('success'))
    total = len(results)
    
    for endpoint, result in results.items():
        status_icon = "✅" if result.get('success') else "❌"
        status_text = "PASSED" if result.get('success') else "FAILED"
        print(f"  {status_icon} {endpoint}: {status_text}")
    
    print(f"\n📊 Overall: {passed}/{total} endpoints working ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All API endpoints are working! Phase 3 is complete.")
        print("📚 API Documentation available at: http://localhost:8000/docs")
        return True
    elif passed >= total * 0.8:  # 80% or more working
        print("✅ Most endpoints working! Phase 3 is mostly complete.")
        print("⚠️ Check the failed endpoints and server logs for issues.")
        return True
    else:
        print("⚠️ Many endpoints failed. Check the server logs and configuration.")
        return False

if __name__ == "__main__":
    success = main()
    print(f"\n{'='*50}")
    if success:
        print("🚀 Phase 3 testing completed successfully!")
        print("💡 Next: Test frontend integration with these endpoints")
    else:
        print("🔧 Phase 3 needs fixes before proceeding")
    print(f"{'='*50}")