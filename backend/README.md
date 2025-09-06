# Reef Temperature Monitoring API

A FastAPI-based backend service for coral reef temperature monitoring and bleaching prediction in the Andaman Islands.

## Features

- **Multi-location temperature prediction** for 4 reef sites in the Andaman Islands
- **14-day analysis window** (7 days past + 7 days future predictions)
- **Real-time DHW (Degree Heating Weeks) calculation** for bleaching risk assessment
- **Concurrent processing** for multiple locations
- **Caching system** to optimize performance
- **Background model retraining** capabilities

## Reef Locations

1. **Jolly Buoy** (11.495°N, 92.610°E) - Primary monitoring site
2. **Neel Islands** (11.833°N, 93.053°E) - Northern reef system  
3. **Mahatma Gandhi Marine National Park** (11.569°N, 92.654°E) - Protected marine area
4. **Havelock** (11.960°N, 93.000°E) - Tourist diving area

## Installation

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Usage

### Start the API server:
```bash
python run.py
```

The API will be available at `http://localhost:8000`

### API Documentation:
- Interactive docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Temperature Analysis
- `GET /api/temperature/analysis` - Get 14-day analysis for all locations
- `GET /api/temperature/analysis/{location_id}` - Get analysis for specific location

### Current Data
- `GET /api/temperature/current` - Get current temperature and DHW for all locations
- `GET /api/temperature/current/{location_id}` - Get current data for specific location

### Locations
- `GET /api/temperature/locations` - List all monitored reef locations

### Model Management
- `POST /api/temperature/retrain` - Retrain models for all locations
- `POST /api/temperature/retrain/{location_id}` - Retrain model for specific location

### Health Check
- `GET /api/temperature/health` - Service health status
- `GET /health` - General health check

## Response Format

### Temperature Analysis Response:
```json
{
  "locations": {
    "jolly-buoy": {
      "location_id": "jolly-buoy",
      "location_name": "Jolly_Buoy",
      "past_data": [
        {
          "date": "2025-01-01",
          "temperature": 28.5,
          "is_predicted": false
        }
      ],
      "future_data": [
        {
          "date": "2025-01-08",
          "temperature": 29.2,
          "is_predicted": true
        }
      ],
      "bleaching_threshold": 29.0,
      "current_dhw": 2.5,
      "risk_level": "low",
      "last_updated": "2025-01-07T10:30:00"
    }
  },
  "metadata": {
    "total_locations": 4,
    "prediction_window_days": 14,
    "past_days": 7,
    "future_days": 7
  },
  "generated_at": "2025-01-07T10:30:00"
}
```

## Configuration

### Environment Variables (.env):
```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# CORS Configuration  
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Cache Configuration
CACHE_TTL_SECONDS=300
MODEL_CACHE_TTL_HOURS=24

# External API Configuration
NOAA_API_TIMEOUT=30
MAX_CONCURRENT_REQUESTS=4
```

## Architecture

```
Frontend (Next.js)
    ↓ HTTP Requests
FastAPI Router (/api/temperature/*)
    ↓ Service Layer
PredictionService
    ↓ Concurrent Processing
MultiLocationTemperatureService
    ↓ Parallel Model Execution
LocationTemperatureModel (x4 locations)
    ↓ Data Fetching
NOAA OISST Satellite Data
```

## Model Details

- **Algorithm:** Random Forest Regressor (400 trees)
- **Features:** 14-day sliding window of historical SST data
- **Training:** Seasonal data from 1982 to present
- **Prediction:** Recursive forecasting for future days
- **DHW Calculation:** 12-week rolling window above bleaching threshold

## Performance Considerations

- **Caching:** 5-minute TTL for API responses, 24-hour TTL for trained models
- **Concurrency:** Parallel processing for all 4 locations
- **Background Tasks:** Model retraining runs asynchronously
- **Connection Pooling:** Optimized NOAA data fetching

## Error Handling

- Network failures when fetching satellite data
- Model training failures for individual locations
- Invalid coordinate inputs
- API rate limiting and timeouts
- Graceful degradation when some locations fail

## Development

### Run in development mode:
```bash
DEBUG=True python run.py
```

### Run tests:
```bash
pytest tests/
```

### Code formatting:
```bash
black app/
isort app/
```

## Deployment

### Docker (Optional):
```bash
docker build -t reef-temp-api .
docker run -p 8000:8000 reef-temp-api
```

### Production considerations:
- Use a production ASGI server (Gunicorn + Uvicorn)
- Set up proper logging and monitoring
- Configure Redis for distributed caching
- Set up health checks and auto-scaling
- Use environment-specific configuration

## Troubleshooting

### Common Issues:

1. **NOAA data fetch failures:**
   - Check internet connection
   - Verify NOAA OISST service availability
   - Check coordinate validity

2. **Model training errors:**
   - Ensure sufficient historical data
   - Check for data gaps in training period
   - Verify coordinate precision

3. **Performance issues:**
   - Monitor cache hit rates
   - Check concurrent request limits
   - Verify model cache effectiveness

### Logs:
Check application logs for detailed error information:
```bash
tail -f logs/app.log
```