#!/usr/bin/env python3
"""
Test script for Phase 4: Background Scheduler endpoints
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_scheduler_endpoints():
    """Test all scheduler-related endpoints"""
    print("🧪 ReefShield Backend - Phase 4 Scheduler Testing")
    print("=" * 60)
    
    # Test scheduler status
    print("\n🔍 Testing scheduler status...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/scheduler/status")
        if response.status_code == 200:
            data = response.json()
            print("  ✅ Scheduler status retrieved successfully")
            print(f"  📊 Scheduler running: {data['scheduler']['is_running']}")
            print(f"  📅 Jobs count: {len(data['scheduler']['jobs'])}")
            if data['scheduler']['jobs']:
                job = data['scheduler']['jobs'][0]
                print(f"  ⏰ Next run: {job.get('next_run_time', 'Not scheduled')}")
        else:
            print(f"  ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test job history
    print("\n🔍 Testing job history...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/scheduler/history?limit=5")
        if response.status_code == 200:
            data = response.json()
            print("  ✅ Job history retrieved successfully")
            print(f"  📈 History entries: {data['count']}")
        else:
            print(f"  ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test manual trigger
    print("\n🔍 Testing manual model trigger...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/scheduler/trigger", 
            params={"user_id": "test_user"}
        )
        if response.status_code == 200:
            data = response.json()
            print("  ✅ Manual trigger executed successfully")
            job_result = data.get('job_result', {})
            print(f"  🚀 Job success: {job_result.get('success', 'Unknown')}")
            print(f"  📝 Message: {job_result.get('message', 'No message')}")
        else:
            print(f"  ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test reschedule (change to a different time temporarily)
    print("\n🔍 Testing reschedule...")
    try:
        # Reschedule to 7:30 AM
        response = requests.post(
            f"{BASE_URL}/api/v1/scheduler/reschedule?hour=7&minute=30"
        )
        if response.status_code == 200:
            data = response.json()
            print("  ✅ Rescheduled successfully")
            print(f"  🕐 New schedule: {data.get('new_schedule', 'Unknown')}")
        else:
            print(f"  ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Wait a moment for scheduler to update
    time.sleep(1)
    
    # Check updated status
    print("\n🔍 Verifying schedule update...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/scheduler/status")
        if response.status_code == 200:
            data = response.json()
            if data['scheduler']['jobs']:
                job = data['scheduler']['jobs'][0]
                next_run = job.get('next_run_time', 'Not scheduled')
                print(f"  ✅ Updated next run: {next_run}")
        else:
            print(f"  ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test pause scheduler
    print("\n🔍 Testing pause scheduler...")
    try:
        response = requests.post(f"{BASE_URL}/api/v1/scheduler/pause")
        if response.status_code == 200:
            print("  ✅ Scheduler paused successfully")
        else:
            print(f"  ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test resume scheduler
    print("\n🔍 Testing resume scheduler...")
    try:
        response = requests.post(f"{BASE_URL}/api/v1/scheduler/resume")
        if response.status_code == 200:
            print("  ✅ Scheduler resumed successfully")
        else:
            print(f"  ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Restore original schedule (6:00 AM)
    print("\n🔍 Restoring original schedule...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/scheduler/reschedule?hour=6&minute=0"
        )
        if response.status_code == 200:
            print("  ✅ Original schedule restored (6:00 AM)")
        else:
            print(f"  ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

def test_integration_with_existing_endpoints():
    """Test that existing endpoints still work with scheduler integration"""
    print("\n🔗 Testing integration with existing endpoints...")
    
    endpoints_to_test = [
        "/health",
        "/api/v1/health", 
        "/api/v1/status",
        "/api/v1/reef-data",
        "/api/v1/combined-data"
    ]
    
    success_count = 0
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"  ✅ {endpoint}")
                success_count += 1
            else:
                print(f"  ❌ {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"  ❌ {endpoint} - Error: {e}")
    
    print(f"\n📊 Integration test: {success_count}/{len(endpoints_to_test)} endpoints working")

def main():
    """Main test execution"""
    print(f"🕐 Starting tests at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test server connectivity first
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding correctly")
            return
        print("✅ Server connectivity confirmed")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return
    
    # Run scheduler tests
    test_scheduler_endpoints()
    
    # Test integration
    test_integration_with_existing_endpoints()
    
    print("\n" + "=" * 60)
    print("🎉 Phase 4 Scheduler Testing Complete!")
    print("💡 Scheduler is now managing daily model execution")
    print("📅 Default schedule: 6:00 AM UTC daily")
    print("🔧 Use scheduler endpoints to manage execution timing")
    print("=" * 60)

if __name__ == "__main__":
    main()