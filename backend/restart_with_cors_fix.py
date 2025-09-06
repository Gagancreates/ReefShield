"""
Restart the backend with CORS fixes applied.
"""
import os
import sys
import subprocess
import time

def restart_backend():
    """Restart the backend server with CORS fixes."""
    print("🔧 Restarting backend with CORS fixes...")
    
    # Kill any existing backend processes
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(['taskkill', '/f', '/im', 'python.exe'], capture_output=True)
        else:  # Unix/Linux/Mac
            subprocess.run(['pkill', '-f', 'run.py'], capture_output=True)
        print("   🛑 Stopped existing backend processes")
        time.sleep(2)
    except Exception as e:
        print(f"   ⚠️ Could not stop existing processes: {e}")
    
    # Start the backend
    print("   🚀 Starting backend with updated CORS configuration...")
    try:
        # Set environment variables for CORS
        env = os.environ.copy()
        env['ALLOWED_ORIGINS'] = 'http://localhost:3000,http://127.0.0.1:3000'
        env['DEBUG'] = 'True'
        
        # Start the backend process
        process = subprocess.Popen(
            [sys.executable, 'run.py'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        print("   ✅ Backend started successfully!")
        print("   📋 Logs:")
        
        # Print logs for a few seconds
        start_time = time.time()
        while time.time() - start_time < 10:  # Show logs for 10 seconds
            line = process.stdout.readline()
            if line:
                print(f"      {line.strip()}")
            elif process.poll() is not None:
                break
        
        print("\n   🎯 Backend is running with CORS fixes!")
        print("   💡 Test CORS: python test_cors.py")
        print("   🌐 API Docs: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"   ❌ Failed to start backend: {e}")

if __name__ == "__main__":
    restart_backend()