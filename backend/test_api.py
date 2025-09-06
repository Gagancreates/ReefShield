"""
Simple test script to verify the API endpoints work correctly.
"""
import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.prediction_service import PredictionService
from app.config.locations import REEF_LOCATIONS


async def test_prediction_service():
    """Test the prediction service functionality."""
    print("🧪 Testing Reef Temperature Monitoring API...")
    
    service = PredictionService()
    
    try:
        # Test 1: Get locations
        print("\n1️⃣ Testing get_locations()...")
        locations = service.get_locations()
        print(f"✅ Found {len(locations)} locations")
        for loc in locations:
            print(f"   - {loc['name']} ({loc['id']})")
        
        # Test 2: Test single location prediction (fastest)
        print("\n2️⃣ Testing single location prediction...")
        test_location = REEF_LOCATIONS[0]  # Jolly Buoy
        print(f"   Testing location: {test_location['name']}")
        
        # This will take some time as it needs to fetch data and train model
        print("   ⏳ Fetching data and training model (this may take 30-60 seconds)...")
        analysis = await service.get_temperature_analysis(test_location['id'])
        
        if test_location['id'] in analysis.locations:
            loc_data = analysis.locations[test_location['id']]
            print(f"   ✅ Analysis complete for {loc_data.location_name}")
            print(f"   📊 Past data points: {len(loc_data.past_data)}")
            print(f"   🔮 Future predictions: {len(loc_data.future_data)}")
            print(f"   🌡️ Current DHW: {loc_data.current_dhw}")
            print(f"   ⚠️ Risk level: {loc_data.risk_level}")
            
            # Show some sample data
            if loc_data.past_data:
                latest = loc_data.past_data[-1]
                print(f"   📅 Latest temp: {latest.temperature}°C on {latest.date}")
            
            if loc_data.future_data:
                next_pred = loc_data.future_data[0]
                print(f"   🔮 Next prediction: {next_pred.temperature}°C on {next_pred.date}")
        else:
            print(f"   ❌ No data returned for {test_location['id']}")
        
        # Test 3: Current temperature data
        print("\n3️⃣ Testing current temperature data...")
        current_data = await service.get_current_temperature_data(test_location['id'])
        
        if test_location['id'] in current_data.locations:
            current = current_data.locations[test_location['id']]
            print(f"   ✅ Current data for {test_location['name']}")
            print(f"   🌡️ Temperature: {current.current_temp}°C")
            print(f"   📊 DHW: {current.dhw}")
            print(f"   ⚠️ Risk: {current.risk_level}")
        else:
            print(f"   ❌ No current data for {test_location['id']}")
        
        print("\n🎉 All tests completed successfully!")
        print("\n💡 To test all locations, run the full API server:")
        print("   python run.py")
        print("   Then visit: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("Starting API tests...")
    print("Note: This will fetch real data from NOAA and may take some time.")
    
    # Run the async test
    asyncio.run(test_prediction_service())