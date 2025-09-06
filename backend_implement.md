# Backend Implementation Plan

## Overview
Integrate the temperature prediction model (`models/finalig.py`) with the frontend dashboard to display 14-day temperature analysis (7 days past + 7 days future predictions) for multiple reef locations in the Andaman Islands.

## Step 1: Create FastAPI Backend Structure

### 1.1 Setup Backend Directory
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── models/
│   │   ├── __init__.py
│   │   ├── temperature.py   # Multi-location temperature prediction model wrapper
│   │   └── schemas.py       # Pydantic models for API responses
│   ├── services/
│   │   ├── __init__.py
│   │   └── prediction_service.py  # Service layer for model execution
│   ├── config/
│   │   ├── __init__.py
│   │   └── locations.py     # Reef location configurations
│   └── routers/
│       ├── __init__.py
│       └── temperature.py   # Temperature API endpoints
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container configuration (optional)
└── .env                    # Environment variables
```

### 1.2 Key Dependencies
- FastAPI
- Uvicorn (ASGI server)
- Pandas, NumPy, XArray
- Scikit-learn
- Python-multipart
- CORS middleware
- Asyncio (for concurrent processing)

### 1.3 Reef Locations Configuration
```python
# config/locations.py
REEF_LOCATIONS = [
    {
        "id": "jolly-buoy",
        "name": "Jolly_Buoy",
        "lat": 11.495,
        "lon": 92.610,
        "description": "Primary monitoring site"
    },
    {
        "id": "neel-islands", 
        "name": "Neel Islands",
        "lat": 11.832919,
        "lon": 93.052612,
        "description": "Northern reef system"
    },
    {
        "id": "mahatma-gandhi",
        "name": "Mahatma Gandhi Marine National Park", 
        "lat": 11.5690,
        "lon": 92.6542,
        "description": "Protected marine area"
    },
    {
        "id": "havelock",
        "name": "Havelock",
        "lat": 11.960000,
        "lon": 93.000000,
        "description": "Tourist diving area"
    }
]
```

## Step 2: Model Integration and API Development

### 2.1 Multi-Location Model Wrapper
- Modify `finalig.py` to accept location parameters (lat, lon)
- Create a service class that runs predictions for all 4 locations
- Implement parallel processing for multiple locations
- Add caching per location to avoid redundant model training
- Return structured data instead of CSV files

### 2.2 API Endpoints
```
GET /api/temperature/analysis
- Returns 14-day temperature data for all locations (7 past + 7 future( inlcuding today))
- Response format: { locations: { [location_id]: { past_data: [], future_data: [] } }, metadata: {} }

GET /api/temperature/analysis/{location_id}
- Returns 14-day temperature data for specific location
- Response format: { location_id: string, past_data: [], future_data: [], metadata: {} }

GET /api/temperature/current
- Returns current temperature and DHW analysis for all locations
- Response format: { locations: { [location_id]: { current_temp: float, dhw: float, risk_level: string } } }

GET /api/temperature/current/{location_id}
- Returns current temperature and DHW analysis for specific location
- Response format: { location_id: string, current_temp: float, dhw: float, risk_level: string }

GET /api/locations
- Returns list of all monitored reef locations
- Response format: { locations: [{ id: string, name: string, coordinates: {lat: float, lon: float} }] }

POST /api/temperature/retrain
- Triggers model retraining for all locations (admin endpoint)
- Response format: { status: string, message: string, locations_processed: number }

POST /api/temperature/retrain/{location_id}
- Triggers model retraining for specific location (admin endpoint)
- Response format: { status: string, message: string, location_id: string }
```

### 2.3 Data Models (Pydantic Schemas)
```python
class LocationCoordinates(BaseModel):
    lat: float
    lon: float

class ReefLocation(BaseModel):
    id: str
    name: str
    coordinates: LocationCoordinates
    description: str

class TemperatureReading(BaseModel):
    date: str
    temperature: float
    is_predicted: bool

class LocationTemperatureAnalysis(BaseModel):
    location_id: str
    location_name: str
    past_data: List[TemperatureReading]
    future_data: List[TemperatureReading]
    bleaching_threshold: float
    current_dhw: float
    risk_level: str
    last_updated: datetime

class MultiLocationTemperatureAnalysis(BaseModel):
    locations: Dict[str, LocationTemperatureAnalysis]
    metadata: Dict[str, Any]
    generated_at: datetime

class CurrentTemperatureData(BaseModel):
    location_id: str
    current_temp: float
    dhw: float
    risk_level: str
    coordinates: LocationCoordinates
    last_updated: datetime
```

## Step 3: Multi-Location Model Implementation

### 3.1 Enhanced finalig.py Integration
```python
# services/prediction_service.py
class MultiLocationPredictionService:
    def __init__(self):
        self.model_cache = {}  # Cache trained models per location
        self.data_cache = {}   # Cache recent data per location
        
    async def predict_all_locations(self) -> Dict[str, LocationTemperatureAnalysis]:
        """Run predictions for all reef locations concurrently"""
        tasks = []
        for location in REEF_LOCATIONS:
            task = self.predict_location(location['id'], location['lat'], location['lon'])
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return {loc['id']: result for loc, result in zip(REEF_LOCATIONS, results) 
                if not isinstance(result, Exception)}
    
    async def predict_location(self, location_id: str, lat: float, lon: float) -> LocationTemperatureAnalysis:
        """Run prediction for single location using modified finalig.py logic"""
        # Implementation details for single location prediction
        pass
        
    def get_aggregated_analysis(self) -> Dict[str, Any]:
        """Generate aggregated 14-day analysis across all locations for main dashboard chart"""
        # Average temperatures across locations for main chart
        # Include confidence intervals and location-specific variations
        pass
```

### 3.2 Concurrent Processing Strategy
- Use asyncio to run predictions for all 4 locations simultaneously
- Implement connection pooling for NOAA OISST data fetching
- Cache model training results per location (models trained once per day)
- Use Redis or in-memory cache for recent data to reduce API calls

## Step 4: Frontend Integration and Data Flow

### 4.1 Update Frontend Data Service
- Modify `frontend/lib/data/realtimeService.ts` to fetch from backend API
- Replace mock location data with real API calls to `/api/temperature/analysis`
- Add error handling and loading states for each location
- Implement data caching and refresh intervals (5-minute intervals)
- Add location-specific data fetching for detailed views

### 4.2 Update Dashboard Component
- Modify `frontend/app/dashboard/page.tsx` temperature chart to use aggregated data
- Integrate real prediction data into the 14-day analysis chart
- Add visual indicators for predicted vs observed data (solid vs dashed lines)
- Update chart styling to distinguish past/future data with different colors
- Show confidence intervals for predictions
- Add location selector for detailed analysis

### 4.3 Enhanced Data Flow Architecture
```
Frontend Dashboard
    ↓ (API Request: /api/temperature/analysis)
Backend FastAPI Router
    ↓ (Concurrent Processing)
Multi-Location Prediction Service
    ↓ (Parallel Execution)
[Location 1] ← finalig.py Model → [Location 2]
[Location 3] ← finalig.py Model → [Location 4]
    ↓ (Fetch OISST Data)
NOAA Satellite Data (4 concurrent connections)
    ↓ (Return Aggregated Predictions)
Backend API Response (All Locations)
    ↓ (Update UI)
Frontend Chart Update + Location Cards
```

### 4.4 Real-time Updates and Caching
- Implement WebSocket connections for live temperature updates
- Add refresh button and auto-refresh functionality (every 5 minutes)
- Cache model results per location to reduce API calls
- Add loading indicators during model execution for each location
- Implement progressive loading (show cached data first, then update with fresh predictions)

## Implementation Notes

### Performance Considerations
- Model training can take 30-60 seconds per location, implement async processing
- Cache trained models per location to avoid retraining on every request
- Use background tasks for data fetching and model updates
- Implement request queuing for concurrent requests
- Consider using Redis for distributed caching in production

### Multi-Location Specific Optimizations
- Batch NOAA data requests where possible (same time ranges)
- Implement smart caching based on location proximity
- Use connection pooling for external API calls
- Parallel model training during off-peak hours
- Location-specific error handling and fallback mechanisms

### Error Handling
- Network failures when fetching OISST data for specific locations
- Model training failures for individual locations (don't fail entire request)
- Invalid coordinate inputs validation
- API rate limiting and timeouts per location
- Graceful degradation when some locations fail

### Security & Configuration
- Environment variables for API keys and configuration
- CORS configuration for frontend access
- Input validation and sanitization for coordinates
- Rate limiting for API endpoints (per location and overall)
- Location-based access controls if needed

### Deployment Considerations
- Docker containerization for consistent deployment
- Environment-specific configuration for different reef monitoring regions
- Health check endpoints for each location's model status
- Logging and monitoring setup with location-specific metrics
- Database setup for storing historical predictions per location