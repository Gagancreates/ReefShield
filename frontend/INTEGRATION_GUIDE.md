# Phase 5 Frontend-Backend Integration Guide

## ✅ Integration Complete!

The ReefShield React frontend is now fully integrated with the FastAPI backend. Here's how to test the integration:

### Prerequisites
1. **Backend Running**: FastAPI server on `http://localhost:8000`
2. **Environment**: `.env.local` file created in frontend directory
3. **Dependencies**: All frontend packages installed

### Testing the Integration

#### 1. Start the Frontend
```bash
cd frontend
npm run dev
```
The frontend will start on `http://localhost:3000`

#### 2. Check Integration Status
- Look for the **Backend Status** component on the dashboard
- Status should show **"Connected"** if integration is working
- Green WiFi icon indicates successful connection

#### 3. Verify Real-time Data
- Dashboard should display real data from the backend
- Temperature charts should show actual model predictions
- Location data should come from the FastAPI endpoints

#### 4. Test Backend Controls
- Use the **"Trigger Run"** button to manually execute the model
- Check scheduler status and next run times
- Monitor connection status in real-time

### New Frontend Features

#### 🔧 Backend Integration
- **API Client**: [`lib/services/apiClient.ts`](lib/services/apiClient.ts)
- **Enhanced Service**: [`lib/services/backendRealtimeService.ts`](lib/services/backendRealtimeService.ts)
- **Updated Hooks**: [`lib/hooks/useRealtimeData.ts`](lib/hooks/useRealtimeData.ts)

#### 📊 New Components
- **Backend Status**: [`components/backend-status.tsx`](components/backend-status.tsx)
- Shows connection status, scheduler info, and manual controls

#### 🔄 Enhanced Hooks
- `useBackendConnection()` - Monitor backend connectivity
- `useModelExecution()` - Trigger manual model runs
- `useSchedulerStatus()` - Get scheduler information
- `useSystemStatus()` - Enhanced system status with backend data

### API Endpoints Integrated

#### Core Data
- `GET /api/v1/reef-data` - Complete reef location data
- `GET /api/v1/combined-data` - 14-day temperature analysis
- `GET /api/v1/status` - System status

#### Management
- `GET /api/v1/scheduler/status` - Scheduler status
- `POST /api/v1/scheduler/trigger` - Manual model execution
- `GET /api/v1/errors/stats` - Error monitoring
- `GET /api/v1/logs/stats` - Logging statistics

### Environment Configuration

The frontend uses these environment variables:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_ENVIRONMENT=development
NEXT_PUBLIC_ENABLE_BACKEND_INTEGRATION=true
NEXT_PUBLIC_SHOW_CONNECTION_STATUS=true
```

### Error Handling & Fallbacks

#### Graceful Degradation
- If backend is unavailable, frontend falls back to simulated data
- Connection status is clearly displayed to users
- Retry mechanisms attempt to reconnect automatically

#### Debug Features
- Set `NEXT_PUBLIC_DEBUG_API_CALLS=true` for API call debugging
- Connection status component shows detailed information
- Error messages are user-friendly

### Troubleshooting

#### Backend Not Connected
1. Verify FastAPI server is running on port 8000
2. Check CORS configuration in backend
3. Ensure `.env.local` has correct API URL

#### Data Not Updating
1. Check browser console for API errors
2. Verify backend endpoints return data
3. Test individual API calls manually

#### Real-time Updates Not Working
1. Check WebSocket connections (if implemented)
2. Verify polling intervals in environment
3. Monitor browser network tab for failed requests

### Next Steps

The frontend-backend integration is complete! You can now:

1. **Customize UI**: Modify components to show additional backend data
2. **Add Features**: Implement new backend endpoints and frontend hooks
3. **Deploy**: Move to Phase 6 for production deployment
4. **Monitor**: Use the backend status component for system monitoring

### Performance Notes

- **Data Caching**: Backend responses are cached for 5 minutes
- **Update Intervals**: Frontend polls every 30 seconds
- **Error Recovery**: Automatic retry with exponential backoff
- **Fallback Mode**: Seamless transition to cached/simulated data

The integration provides a robust, production-ready connection between your React frontend and FastAPI backend with comprehensive error handling and monitoring capabilities!