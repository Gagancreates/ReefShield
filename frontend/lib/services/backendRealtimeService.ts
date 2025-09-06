/**
 * Enhanced RealtimeService integrated with FastAPI Backend
 * Provides real-time data from the Python backend with fallback to simulated data
 */

import { 
  apiClient, 
  type ReefLocationData, 
  type CombinedTemperatureData, 
  type SystemStatus,
  type SchedulerStatus,
  type ReefShieldAPIClient 
} from './apiClient';

// Legacy interface compatibility for existing components
export interface TemperatureReading {
  date: string;
  temperature: number;
  anomaly: number;
  riskLevel: 'Safe' | 'Watch' | 'Warning' | 'Critical';
  source: 'Observed' | 'Forecast' | 'Historical' | 'Predicted';
}

export interface LocationData {
  id: string;
  name: string;
  coordinates: { lat: number; lng: number };
  currentTemperature: number;
  riskLevel: 'low' | 'moderate' | 'high';
  dhw: number;
  trend: 'stable' | 'increasing' | 'decreasing';
  temperatureHistory: TemperatureReading[];
  forecast: TemperatureReading[];
  chlorophyll?: {
    value: number;
    riskLevel: 'low' | 'moderate' | 'high';
    threshold: number;
  };
}

export interface SystemStatusData {
  satelliteDataFeed: string;
  aiProcessingEngine: string;
  alertSystem: string;
  dataSync: string;
  backendConnection: string;
  modelStatus: string;
  lastModelRun: string | null;
  nextScheduledRun: string | null;
}

export interface AlertData {
  id: string;
  title: string;
  location: string;
  severity: 'Critical' | 'Warning' | 'Medium';
  time: string;
  description: string;
}

export class BackendRealtimeService {
  private client: ReefShieldAPIClient;
  private intervalId: NodeJS.Timeout | null = null;
  private lastBackendData: ReefLocationData | null = null;
  private lastCombinedData: CombinedTemperatureData | null = null;
  private lastSystemStatus: SystemStatus | null = null;
  private connectionStatus: 'connected' | 'disconnected' | 'error' = 'disconnected';
  private errorCount = 0;
  private maxErrors = 3;

  constructor(client?: ReefShieldAPIClient) {
    this.client = client || apiClient;
  }

  // Convert backend data to frontend format
  private convertTemperatureReading(backendReading: any): TemperatureReading {
    const temp = backendReading.temperature;
    const baselineTemp = 29.0; // Bleaching threshold
    const anomaly = temp - baselineTemp;
    
    let riskLevel: 'Safe' | 'Watch' | 'Warning' | 'Critical' = 'Safe';
    if (anomaly >= 2.0) riskLevel = 'Critical';
    else if (anomaly >= 1.5) riskLevel = 'Warning';
    else if (anomaly >= 1.0) riskLevel = 'Watch';

    // Map backend source to frontend source
    let source: 'Observed' | 'Forecast' | 'Historical' | 'Predicted' = 'Observed';
    if (backendReading.source === 'Historical') source = 'Observed';
    else if (backendReading.source === 'Predicted') source = 'Forecast';
    else if (backendReading.source === 'Observed') source = 'Observed';
    else if (backendReading.source === 'Forecast') source = 'Forecast';

    return {
      date: backendReading.date,
      temperature: temp,
      anomaly: Number(anomaly.toFixed(2)),
      riskLevel,
      source
    };
  }

  private convertBackendDataToLocationData(backendData: ReefLocationData): LocationData {
    const historical = backendData.historical_data.map(reading => 
      this.convertTemperatureReading(reading)
    );
    const forecast = backendData.predictions.map(reading => 
      this.convertTemperatureReading(reading)
    );

    // Get current temperature from the most recent historical reading
    const currentReading = historical[historical.length - 1];
    const currentTemperature = currentReading ? currentReading.temperature : 28.0;

    // Generate location ID from name
    const locationId = backendData.location_name.toLowerCase().replace(/\s+/g, '-');

    return {
      id: locationId,
      name: backendData.location_name,
      coordinates: { 
        lat: backendData.coordinates.lat, 
        lng: backendData.coordinates.lon 
      },
      currentTemperature: Number(currentTemperature.toFixed(1)),
      riskLevel: backendData.risk_assessment.current_risk,
      dhw: backendData.risk_assessment.dhw || 0,
      trend: backendData.risk_assessment.trend,
      temperatureHistory: historical,
      forecast: forecast,
      // Simulate chlorophyll data for now (can be enhanced later)
      chlorophyll: {
        value: Number((0.5 + Math.random() * 0.4).toFixed(3)),
        riskLevel: backendData.risk_assessment.current_risk,
        threshold: 0.77
      }
    };
  }

  // Fetch data from backend with error handling
  private async fetchBackendData(): Promise<boolean> {
    try {
      console.log('🔄 Fetching data from FastAPI backend...');
      
      // Test connection first
      const isConnected = await this.client.checkConnection();
      if (!isConnected) {
        throw new Error('Backend connection failed');
      }

      // Fetch reef data
      const reefData = await this.client.getReefData();
      this.lastBackendData = reefData;

      // Fetch system status
      const systemStatus = await this.client.getSystemStatus();
      this.lastSystemStatus = systemStatus;

      // Fetch combined data for temperature analysis
      const combinedData = await this.client.getCombinedData();
      this.lastCombinedData = combinedData;

      this.connectionStatus = 'connected';
      this.errorCount = 0;
      
      console.log('✅ Successfully fetched data from backend');
      return true;

    } catch (error) {
      this.errorCount++;
      console.error(`❌ Backend fetch error (${this.errorCount}/${this.maxErrors}):`, error);
      
      if (this.errorCount >= this.maxErrors) {
        this.connectionStatus = 'error';
        console.warn('🚨 Too many backend errors, switching to fallback mode');
      } else {
        this.connectionStatus = 'disconnected';
      }
      
      return false;
    }
  }

  // Get current data (from backend or fallback)
  getCurrentData(): LocationData[] {
    if (this.connectionStatus === 'connected' && this.lastBackendData) {
      // Return real backend data
      const locationData = this.convertBackendDataToLocationData(this.lastBackendData);
      return [locationData];
    } else {
      // Fallback to simulated data
      return this.getFallbackLocationData();
    }
  }

  // Get temperature analysis data for charts
  getTemperatureAnalysis(): Array<{
    day: string;
    temp: number;
    threshold: number;
    source: string;
  }> {
    if (this.connectionStatus === 'connected' && this.lastCombinedData) {
      // Use real backend data
      return this.lastCombinedData.data.map((reading, index) => ({
        day: `Day ${index + 1}`,
        temp: Number(reading.temperature.toFixed(1)),
        threshold: 29.0,
        source: reading.source === 'Historical' ? 'Observed' : 'Forecast'
      }));
    } else {
      // Fallback to simulated data
      return this.getFallbackTemperatureAnalysis();
    }
  }

  // Get system status (enhanced with backend data)
  getSystemStatus(): SystemStatusData {
    const baseStatus: SystemStatusData = {
      satelliteDataFeed: 'Online',
      aiProcessingEngine: 'Active',
      alertSystem: 'Operational',
      dataSync: 'Syncing',
      backendConnection: this.connectionStatus,
      modelStatus: 'Unknown',
      lastModelRun: null,
      nextScheduledRun: null
    };

    if (this.connectionStatus === 'connected' && this.lastSystemStatus) {
      const modelStatus = this.lastSystemStatus.model_status;
      
      return {
        ...baseStatus,
        backendConnection: 'connected',
        modelStatus: modelStatus.is_running ? 'Running' : 'Idle',
        lastModelRun: modelStatus.last_run,
        nextScheduledRun: modelStatus.next_scheduled_run,
        dataSync: this.lastSystemStatus.api_status === 'healthy' ? 'Synced' : 'Error'
      };
    }

    return baseStatus;
  }

  // Generate alerts based on current data
  generateAlerts(): AlertData[] {
    const locations = this.getCurrentData();
    const alerts: AlertData[] = [];
    
    locations.forEach(location => {
      if (location.riskLevel === 'high') {
        alerts.push({
          id: `alert-${location.id}-temp`,
          title: 'High Temperature Alert',
          location: location.name,
          severity: 'Critical',
          time: `${Math.floor(Math.random() * 30)} minutes ago`,
          description: `Water temperature ${location.currentTemperature}°C exceeds safe threshold`
        });
      }

      if (location.dhw >= 4) {
        alerts.push({
          id: `alert-${location.id}-dhw`,
          title: 'Coral Bleaching Risk',
          location: location.name,
          severity: location.dhw >= 8 ? 'Critical' : 'Warning',
          time: `${Math.floor(Math.random() * 60)} minutes ago`,
          description: `DHW ${location.dhw} °C-weeks indicates bleaching stress`
        });
      }

      if (location.trend === 'increasing' && location.riskLevel !== 'low') {
        alerts.push({
          id: `alert-${location.id}-trend`,
          title: 'Temperature Rising',
          location: location.name,
          severity: 'Medium',
          time: `${Math.floor(Math.random() * 120)} minutes ago`,
          description: 'Upward temperature trend detected'
        });
      }
    });

    // Add backend connection alert if disconnected
    if (this.connectionStatus === 'error') {
      alerts.push({
        id: 'alert-backend-connection',
        title: 'Backend Connection Lost',
        location: 'System',
        severity: 'Warning',
        time: '5 minutes ago',
        description: 'Using cached data. Attempting to reconnect...'
      });
    }

    return alerts.slice(0, 5); // Return top 5 alerts
  }

  // Get specific location data
  getLocationData(locationId: string): LocationData | null {
    const locations = this.getCurrentData();
    return locations.find(loc => loc.id === locationId) || null;
  }

  // Start real-time updates
  startRealtimeUpdates(callback: (data: LocationData[]) => void, intervalMs: number = 30000): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }

    // Initial fetch
    this.fetchBackendData().then(() => {
      callback(this.getCurrentData());
    });

    // Set up periodic updates
    this.intervalId = setInterval(async () => {
      await this.fetchBackendData();
      callback(this.getCurrentData());
    }, intervalMs);

    console.log(`🔄 Started real-time updates (${intervalMs}ms interval)`);
  }

  // Stop real-time updates
  stopRealtimeUpdates(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
      console.log('⏹️ Stopped real-time updates');
    }
  }

  // Backend-specific methods
  async triggerModelRun(): Promise<boolean> {
    try {
      await this.client.triggerImmediateRun('frontend-user');
      console.log('✅ Model run triggered successfully');
      return true;
    } catch (error) {
      console.error('❌ Failed to trigger model run:', error);
      return false;
    }
  }

  async getSchedulerInfo(): Promise<SchedulerStatus | null> {
    try {
      return await this.client.getSchedulerStatus();
    } catch (error) {
      console.error('❌ Failed to get scheduler info:', error);
      return null;
    }
  }

  getConnectionStatus(): 'connected' | 'disconnected' | 'error' {
    return this.connectionStatus;
  }

  // Fallback methods for when backend is unavailable
  private getFallbackLocationData(): LocationData[] {
    // Simplified fallback data
    return [{
      id: 'andaman-reef',
      name: 'Andaman Reef',
      coordinates: { lat: 11.67, lng: 92.75 },
      currentTemperature: 28.5,
      riskLevel: 'low',
      dhw: 0.5,
      trend: 'stable',
      temperatureHistory: [],
      forecast: [],
      chlorophyll: {
        value: 0.65,
        riskLevel: 'low',
        threshold: 0.77
      }
    }];
  }

  private getFallbackTemperatureAnalysis(): Array<{
    day: string;
    temp: number;
    threshold: number;
    source: string;
  }> {
    // Generate simple 14-day pattern
    const data = [];
    for (let i = 0; i < 14; i++) {
      data.push({
        day: `Day ${i + 1}`,
        temp: 28.0 + Math.sin(i * 0.5) * 0.8 + Math.random() * 0.3,
        threshold: 29.0,
        source: i < 7 ? 'Observed' : 'Forecast'
      });
    }
    return data;
  }
}

// Export singleton instance
export const backendRealtimeService = new BackendRealtimeService();

// Export for backward compatibility
export { backendRealtimeService as realtimeService };