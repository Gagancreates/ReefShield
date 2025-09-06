"""
Test script for data processing functionality
"""

import sys
import logging
from pathlib import Path

# Add the backend app to the path
sys.path.append(str(Path(__file__).parent))

from app.services.data_service import DataService
from app.services.model_service import ModelService
from app.utils.csv_reader import CSVProcessor
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_csv_processor():
    """Test CSV processor functionality"""
    print("\n🔍 Testing CSV Processor...")
    
    processor = CSVProcessor(settings.MODELS_DIR)
    
    # Test file info
    for csv_name, csv_path in [
        ("Historical CSV", settings.historical_csv_path),
        ("Predictions CSV", settings.predictions_csv_path),
        ("Combined 14-day CSV", settings.combined_14day_csv_path),
    ]:
        info = processor.get_file_info(csv_path)
        print(f"  {csv_name}: {'✅' if info['exists'] else '❌'} "
              f"({info['row_count']} rows, {info['size_bytes']} bytes)")
    
    # Test reading combined CSV
    if settings.combined_14day_csv_path.exists():
        readings = processor.get_combined_14day_data(settings.combined_14day_csv_path)
        print(f"  Combined readings extracted: {len(readings)}")
        if readings:
            print(f"    First reading: {readings[0].date} - {readings[0].temperature}°C ({readings[0].source})")
            print(f"    Last reading: {readings[-1].date} - {readings[-1].temperature}°C ({readings[-1].source})")


def test_data_service():
    """Test DataService functionality"""
    print("\n📊 Testing Data Service...")
    
    data_service = DataService()
    
    try:
        # Test getting historical data
        historical = data_service.get_last_8_historical()
        print(f"  Historical data: {len(historical)} readings")
        
        # Test getting predictions
        predictions = data_service.get_all_predictions()
        print(f"  Prediction data: {len(predictions)} readings")
        
        # Test combined data
        combined_data = data_service.get_combined_temperature_data()
        print(f"  Combined 14-day data: {len(combined_data.data)} readings")
        print(f"    Location: {combined_data.location_name}")
        print(f"    Coordinates: {combined_data.coordinates.lat}, {combined_data.coordinates.lon}")
        
        # Test full reef data
        reef_data = data_service.combine_data()
        print(f"  Full reef data:")
        print(f"    Historical: {len(reef_data.historical_data)} readings")
        print(f"    Predictions: {len(reef_data.predictions)} readings")
        print(f"    Risk level: {reef_data.risk_assessment.current_risk}")
        print(f"    Trend: {reef_data.risk_assessment.trend}")
        print(f"    DHW: {reef_data.risk_assessment.dhw}")
        
        # Test file status
        file_status = data_service.get_data_file_status()
        print(f"  File status check: {len(file_status)} files checked")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error in DataService: {e}")
        return False


def test_model_service():
    """Test ModelService functionality"""
    print("\n🤖 Testing Model Service...")
    
    model_service = ModelService()
    
    try:
        # Test model script check
        script_exists = model_service.check_model_script_exists()
        print(f"  Model script exists: {'✅' if script_exists else '❌'}")
        
        # Test CSV files check
        csv_status = model_service.check_csv_files_exist()
        print(f"  CSV files status:")
        for file_type, exists in csv_status.items():
            print(f"    {file_type}: {'✅' if exists else '❌'}")
        
        # Test execution status
        status = model_service.get_execution_status()
        print(f"  Execution status:")
        print(f"    Running: {status.is_running}")
        print(f"    Last run: {status.last_run or 'Never'}")
        print(f"    Next run: {status.next_scheduled_run or 'Not scheduled'}")
        
        # Test model info
        info = model_service.get_model_info()
        print(f"  Model info:")
        print(f"    Script path: {info.get('script_path', 'Unknown')}")
        print(f"    Python executable: {info.get('python_executable', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error in ModelService: {e}")
        return False


def test_configuration():
    """Test configuration settings"""
    print("\n⚙️ Testing Configuration...")
    
    try:
        # Test settings access
        print(f"  Models directory: {settings.MODELS_DIR}")
        print(f"  API title: {settings.API_TITLE}")
        print(f"  Reef location: {settings.REEF_LOCATION['name']}")
        
        # Test path validation
        validation = settings.validate_paths()
        print(f"  Path validation:")
        for path_type, exists in validation.items():
            print(f"    {path_type}: {'✅' if exists else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error in Configuration: {e}")
        return False


def main():
    """Run all tests"""
    print("🧪 ReefShield Backend - Phase 2 Testing")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_configuration),
        ("CSV Processor", test_csv_processor),
        ("Data Service", test_data_service),
        ("Model Service", test_model_service),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"  ❌ {test_name} test failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n📋 Test Summary:")
    print("=" * 30)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Phase 2 is complete.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)