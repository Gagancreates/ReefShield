# Quick Start Guide

## 🚀 Get the API Running in 3 Steps

### 1. Install Dependencies

**Option A - Complete Fix (Recommended):**
```bash
cd backend
python complete_fix.py
```

**Option B - Fix xarray dependencies:**
```bash
cd backend
python fix_xarray_dependencies.py
```

**Option C - Manual Installation:**
```bash
cd backend
pip install -r requirements.txt
```

**Option D - If you have xarray/NOAA issues:**
```bash
cd backend
python test_noaa_access.py  # Test NOAA connectivity
python complete_fix.py      # Fix all issues
```

**Option D - Individual Package Installation:**
```bash
cd backend
pip install fastapi uvicorn[standard] pydantic numpy pandas scikit-learn xarray aiohttp python-multipart python-dotenv aiofiles httpx
```

### 2. Start the API Server
```bash
python run.py
```

### 3. Test the API
Open your browser and go to:
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **Root Info:** http://localhost:8000/

## 🧪 Test Individual Components

### Test the prediction service:
```bash
python test_api.py
```
*Note: This will fetch real satellite data and may take 30-60 seconds*

## 📡 API Endpoints to Try

### Get all reef locations:
```bash
curl http://localhost:8000/api/temperature/locations
```

### Get temperature analysis for all locations:
```bash
curl http://localhost:8000/api/temperature/analysis
```

### Get current temperature data:
```bash
curl http://localhost:8000/api/temperature/current
```

### Get data for specific location (Jolly Buoy):
```bash
curl http://localhost:8000/api/temperature/analysis/jolly-buoy
```

## ⚡ Performance Notes

- **First request** may take 30-60 seconds as models need to train
- **Subsequent requests** are cached and return in ~1-2 seconds
- **All 4 locations** are processed concurrently for efficiency
- **Models retrain** automatically every 24 hours

## 🔧 Configuration

Edit `.env` file to customize:
- API port and host
- Cache settings
- CORS origins
- Debug mode

## 🐛 Troubleshooting

### Common issues:

1. **Pydantic/FastAPI version conflicts:**
   ```bash
   python test_imports.py  # Check what's failing
   python install.py       # Auto-install compatible versions
   ```

2. **"Module not found" errors:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **"ForwardRef._evaluate() missing argument" error:**
   ```bash
   pip uninstall pydantic fastapi
   pip install pydantic==2.4.2 fastapi==0.104.1
   ```

4. **NOAA data fetch failures:**
   - Check internet connection
   - Try again (NOAA servers sometimes timeout)

5. **Port already in use:**
   - Change `API_PORT` in `.env` file
   - Or kill existing process: `lsof -ti:8000 | xargs kill` (Linux/Mac)
   - Or use Task Manager (Windows)

### Check logs:
The API prints detailed logs to console showing:
- Model training progress
- Data fetching status
- Error details
- Performance metrics

## 🌐 Frontend Integration

Once the backend is running, update your frontend to use:
```typescript
const API_BASE_URL = 'http://localhost:8000/api';
```

The API is CORS-enabled for `http://localhost:3000` by default.