# Backend Integration Guide

## Overview
The frontend has been successfully integrated with the FastAPI backend to display real-time temperature predictions for 4 reef locations in the Andaman Islands.

## Integration Changes

### 1. Updated Data Service (`lib/data/realtimeService.ts`)
- **Replaced CSV-based mock data** with real API calls to the backend
- **Added API client** with retry logic and caching (5-minute TTL)
- **Implemented fallback data** for when the backend is unavailable
- **Added proper error handling** and graceful degradation

### 2. Updated Hooks (`lib/hooks/useRealtimeData.ts`)
- **Made all data fetching async** to handle API calls
- **Added proper error handling** in all hooks
- **Maintained existing interface** for seamless component integration

### 3. Environment Configuration
- **Added `.env.local`** with backend API URL configuration
- **Configurable API endpoint** via `NEXT_PUBLIC_API_URL`

## API Integration Details

### Backend Endpoints Used:
- `GET /api/temperature/analysis` - 14-day temperature analysis for all locations
- `GET /api/temperature/current` - Current temperature and DHW data

### Data Flow:
```
Frontend Components
    ↓ (useRealtimeLocations hook)
RealtimeDataService
    ↓ (HTTP requests with caching)
Backend FastAPI
    ↓ (Multi-location predictions)
NOAA Satellite Data + ML Models
```

### Caching Strategy:
- **API Response Cache**: 5 minutes TTL
- **Automatic Refresh**: Every 5 minutes
- **Fallback Data**: When backend is unavailable
- **Retry Logic**: 3 attempts with exponential backoff

## Configuration

### Environment Variables (`.env.local`):
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_ENV=development
```

### Backend Requirements:
- Backend API server running on `http://localhost:8000`
- All 4 reef locations configured and operational
- NOAA data access for real predictions

## Features Maintained

### ✅ All existing features work with real data:
- **Real-time location monitoring** (4 Andaman reef sites)
- **14-day temperature analysis** (7 past + 7 future predictions)
- **DHW calculation and risk assessment**
- **Interactive location details** with maps and charts
- **Real-time alerts** based on actual temperature thresholds
- **Chlorophyll data integration** (still uses CSV data)

### 🔄 Enhanced with real predictions:
- **Actual NOAA satellite data** instead of mock data
- **Machine learning predictions** for future temperatures
- **Real DHW calculations** based on historical data
- **Accurate risk assessments** using actual thresholds

## Usage

### 1. Start the Backend:
```bash
cd backend
python run.py
```

### 2. Start the Frontend:
```bash
cd frontend
npm run dev
```

### 3. Access the Dashboard:
- Visit: `http://localhost:3000/dashboard`
- The dashboard will automatically fetch real data from the backend
- If backend is unavailable, fallback data will be displayed

## Error Handling

### Backend Unavailable:
- Frontend displays fallback data
- User sees a subtle indicator that data may not be current
- Automatic retry when backend comes back online

### Network Issues:
- Retry logic with exponential backoff
- Cached data served while retrying
- Graceful degradation to fallback data

### API Errors:
- Detailed error logging in browser console
- User-friendly error states in UI
- Automatic recovery when issues resolve

## Performance Optimizations

### Caching:
- **5-minute cache** for API responses
- **Background refresh** to keep data current
- **Efficient data structures** for fast lookups

### Network:
- **Concurrent API calls** for analysis and current data
- **Request deduplication** to avoid redundant calls
- **Optimized payload sizes** with only necessary data

### UI:
- **Progressive loading** - show cached data first
- **Smooth transitions** between data updates
- **Responsive design** maintained across all screen sizes

## Monitoring & Debugging

### Browser Console Logs:
- API request/response details
- Cache hit/miss information
- Error details with stack traces
- Performance timing information

### Network Tab:
- Monitor API call frequency
- Check response times and payload sizes
- Verify caching behavior

### Backend Logs:
- Model training progress
- Data fetching status from NOAA
- Performance metrics per location

## Troubleshooting

### Common Issues:

1. **"Failed to fetch" errors:**
   - Ensure backend is running on `http://localhost:8000`
   - Check CORS configuration in backend
   - Verify network connectivity

2. **Stale data displayed:**
   - Check cache TTL settings
   - Verify automatic refresh intervals
   - Clear browser cache if needed

3. **Slow initial load:**
   - First API call may take 30-60 seconds (model training)
   - Subsequent calls are much faster (cached models)
   - Consider pre-warming models in production

4. **Missing location data:**
   - Check backend logs for NOAA data fetch issues
   - Verify all 4 locations are configured correctly
   - Ensure coordinates are accurate

### Development Tips:

1. **Test with backend offline:**
   - Stop backend server
   - Verify fallback data displays correctly
   - Check error handling in console

2. **Monitor API performance:**
   - Use browser Network tab
   - Check response times for each endpoint
   - Verify caching reduces redundant requests

3. **Debug data flow:**
   - Add console.log in hooks to trace data updates
   - Check component re-render frequency
   - Verify state management efficiency

## Future Enhancements

### Potential Improvements:
- **WebSocket integration** for real-time updates
- **Service worker caching** for offline support
- **Progressive Web App** features
- **Push notifications** for critical alerts
- **Data export functionality** for research use
- **Historical data visualization** with longer time ranges

### Scalability Considerations:
- **Redis caching** for production deployment
- **CDN integration** for global access
- **Load balancing** for high availability
- **Database integration** for historical data storage