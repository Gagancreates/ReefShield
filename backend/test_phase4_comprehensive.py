#!/usr/bin/env python3
"""
Comprehensive test script for Phase 4: Enhanced Backend Features
- Background Scheduler
- Error Handling & Retry Mechanisms  
- Structured Logging with File Rotation
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_phase4_features():
    """Test all Phase 4 enhanced features"""
    print("🧪 ReefShield Backend - Phase 4 Enhanced Features Testing")
    print("=" * 70)
    
    # Test 1: Background Scheduler Features
    print("\n📅 TESTING BACKGROUND SCHEDULER")
    print("-" * 40)
    
    # Scheduler status
    print("🔍 Testing scheduler status...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/scheduler/status")
        if response.status_code == 200:
            data = response.json()
            scheduler = data['scheduler']
            print(f"  ✅ Scheduler running: {scheduler['is_running']}")
            print(f"  📊 Active jobs: {len(scheduler['jobs'])}")
            if scheduler['jobs']:
                job = scheduler['jobs'][0]
                print(f"  ⏰ Next run: {job.get('next_run_time', 'Not scheduled')}")
                print(f"  🔧 Job ID: {job.get('id', 'Unknown')}")
        else:
            print(f"  ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Job history
    print("\\n🔍 Testing job history...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/scheduler/history?limit=5")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ History entries: {data['count']}")
            if data['history']:
                latest = data['history'][-1]
                print(f"  📈 Latest job: {latest.get('trigger', 'Unknown')} - {latest.get('success', 'Unknown')}")
        else:
            print(f"  ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test 2: Error Handling & Retry Mechanisms
    print("\\n🚨 TESTING ERROR HANDLING & RETRY MECHANISMS")
    print("-" * 50)
    
    # Error statistics
    print("🔍 Testing error statistics...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/errors/stats")
        if response.status_code == 200:
            data = response.json()
            stats = data['error_statistics']
            print(f"  ✅ Total errors tracked: {stats.get('total_errors', 0)}")
            print(f"  📊 Error types: {len(stats.get('error_counts', {}))}")
            if stats.get('error_counts'):
                for error_type, count in stats['error_counts'].items():
                    print(f"    - {error_type}: {count}")
        else:
            print(f"  ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Trigger a manual model run to test error handling
    print("\\n🔍 Testing manual model trigger with error handling...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/scheduler/trigger", 
            params={"user_id": "test_phase4"}
        )
        if response.status_code == 200:
            data = response.json()
            job_result = data.get('job_result', {})
            print(f"  ✅ Manual trigger completed")
            print(f"  🚀 Success: {job_result.get('success', 'Unknown')}")
            print(f"  📝 Message: {job_result.get('message', 'No message')[:100]}...")
            print(f"  ⚡ Job ID: {job_result.get('job_id', 'Unknown')}")
        else:
            print(f"  ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test 3: Structured Logging
    print("\\n📋 TESTING STRUCTURED LOGGING")
    print("-" * 35)
    
    # Logging statistics
    print("🔍 Testing logging statistics...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/logs/stats")
        if response.status_code == 200:
            data = response.json()
            stats = data['logging_statistics']
            print(f"  ✅ Logging system initialized: {stats.get('initialized', False)}")
            print(f"  📁 Logs directory: {stats.get('logs_directory', 'Unknown')}")
            print(f"  🔧 Active loggers: {stats.get('loggers_count', 0)}")
            
            log_files = stats.get('log_files', [])
            print(f"  📄 Log files: {len(log_files)}")
            for log_file in log_files[:5]:  # Show first 5 files
                if 'error' not in log_file:
                    name = log_file.get('name', 'Unknown')
                    size_mb = log_file.get('size_mb', 0)
                    print(f"    - {name}: {size_mb} MB")
        else:
            print(f"  ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test 4: Integration with Existing Features
    print("\\n🔗 TESTING INTEGRATION WITH EXISTING FEATURES")
    print("-" * 45)
    
    # Test key endpoints still work with enhanced features
    endpoints_to_test = [
        ("/health", "Basic health check"),
        ("/api/v1/health", "Enhanced health check"),
        ("/api/v1/status", "System status"),
        ("/api/v1/reef-data", "Reef data"),
        ("/api/v1/combined-data", "Combined data")
    ]
    
    success_count = 0
    for endpoint, description in endpoints_to_test:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"  ✅ {description}")
                success_count += 1
            else:
                print(f"  ❌ {description} - Status: {response.status_code}")
        except Exception as e:
            print(f"  ❌ {description} - Error: {e}")
    
    print(f"\\n📊 Integration test: {success_count}/{len(endpoints_to_test)} endpoints working")
    
    # Test 5: Scheduler Management
    print("\\n⚙️ TESTING SCHEDULER MANAGEMENT")
    print("-" * 35)
    
    # Test reschedule (temporarily change schedule)
    print("🔍 Testing schedule management...")
    try:
        # Reschedule to 8:30 AM
        response = requests.post(
            f"{BASE_URL}/api/v1/scheduler/reschedule?hour=8&minute=30"
        )
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Rescheduled to: {data.get('new_schedule', 'Unknown')}")
        else:
            print(f"  ❌ Reschedule failed: {response.status_code}")
        
        # Wait a moment and restore original schedule
        time.sleep(1)
        
        response = requests.post(
            f"{BASE_URL}/api/v1/scheduler/reschedule?hour=6&minute=0"
        )
        if response.status_code == 200:
            print("  ✅ Original schedule restored (6:00 AM)")
        else:
            print(f"  ❌ Restore failed: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Schedule management error: {e}")

def test_performance_and_reliability():
    """Test system performance and reliability"""
    print("\\n⚡ TESTING PERFORMANCE & RELIABILITY")
    print("-" * 40)
    
    # Rapid API calls to test error handling
    print("🔍 Testing rapid API calls...")
    start_time = time.time()
    success_count = 0
    total_calls = 10
    
    for i in range(total_calls):
        try:
            response = requests.get(f"{BASE_URL}/api/v1/health", timeout=5)
            if response.status_code == 200:
                success_count += 1
        except Exception:
            pass
    
    end_time = time.time()
    duration = end_time - start_time
    avg_response_time = duration / total_calls
    
    print(f"  ✅ Completed {success_count}/{total_calls} calls")
    print(f"  ⏱️ Average response time: {avg_response_time:.3f}s")
    print(f"  📊 Success rate: {(success_count/total_calls)*100:.1f}%")

def main():
    """Main test execution"""
    print(f"🕐 Starting Phase 4 comprehensive tests at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
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
    
    # Run comprehensive tests
    test_phase4_features()
    test_performance_and_reliability()
    
    print("\\n" + "=" * 70)
    print("🎉 Phase 4 Comprehensive Testing Complete!")
    print("✨ Enhanced Features Summary:")
    print("  📅 Background Scheduler - Daily automated model execution")
    print("  🚨 Error Handling - Retry mechanisms & circuit breakers")
    print("  📋 Structured Logging - JSON logs with file rotation")
    print("  🔧 Management APIs - Scheduler & error monitoring")
    print("  🔗 Full Integration - All existing features enhanced")
    print("=" * 70)

if __name__ == "__main__":
    main()