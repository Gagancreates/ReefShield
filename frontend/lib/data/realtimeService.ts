// Real-time data service using backend API
import { loadChlorophyllData, getChlorophyllForLocation, getChlorophyllRiskLevel, type ChlorophyllData } from '@/lib/utils/chlorophyllData';

// Backend API configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
export interface TemperatureReading {
    date: string;
    temperature: number;
    is_predicted: boolean;
}

// Backend API response types
interface BackendTemperatureReading {
    date: string;
    temperature: number;
    is_predicted: boolean;
}

interface BackendLocationAnalysis {
    location_id: string;
    location_name: string;
    past_data: BackendTemperatureReading[];
    future_data: BackendTemperatureReading[];
    bleaching_threshold: number;
    current_dhw: number;
    risk_level: string;
    last_updated: string;
}

interface BackendCurrentData {
    location_id: string;
    current_temp: number;
    dhw: number;
    risk_level: string;
    coordinates: { lat: number; lon: number };
    last_updated: string;
}

interface BackendAnalysisResponse {
    locations: Record<string, BackendLocationAnalysis>;
    metadata: {
        total_locations: number;
        prediction_window_days: number;
        past_days: number;
        future_days: number;
        bleaching_threshold: number;
    };
    generated_at: string;
}

interface BackendCurrentResponse {
    locations: Record<string, BackendCurrentData>;
    generated_at: string;
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

export class RealtimeDataService {
    private locations: LocationData[] = [];
    private intervalId: NodeJS.Timeout | null = null;
    private chlorophyllData: ChlorophyllData[] = [];
    private cache: {
        analysis?: { data: BackendAnalysisResponse; timestamp: number };
        current?: { data: BackendCurrentResponse; timestamp: number };
    } = {};
    private readonly CACHE_TTL = 5 * 60 * 1000; // 5 minutes
    private isInitialized = false;
    private dataUpdateCallbacks: ((data: LocationData[]) => void)[] = [];

    constructor() {
        this.initializeService();
    }

    private async initializeService() {
        // Initialize with fallback data immediately
        await this.initializeChlorophyllData();
        this.locations = this.initializeWithFallbackData();
        this.isInitialized = true;
        
        // Notify any waiting callbacks with fallback data
        this.notifyDataCallbacks();
        
        // Then fetch real data in background
        this.updateLocationsFromAPI();
    }

    private async initializeChlorophyllData() {
        // Load chlorophyll data
        try {
            this.chlorophyllData = await loadChlorophyllData();
        } catch (error) {
            console.error('Failed to load chlorophyll data:', error);
            this.chlorophyllData = [];
        }
    }

    private initializeWithFallbackData(): LocationData[] {
        const fallbackAnalysis = this.getFallbackAnalysisData();
        const fallbackCurrent = this.getFallbackCurrentData();
        return this.convertBackendToLocationData(fallbackAnalysis, fallbackCurrent);
    }

    private notifyDataCallbacks() {
        this.dataUpdateCallbacks.forEach(callback => {
            try {
                callback([...this.locations]);
            } catch (error) {
                console.error('Error in data update callback:', error);
            }
        });
    }

    private isCacheValid(cacheEntry: { timestamp: number } | undefined): boolean {
        if (!cacheEntry) return false;
        return Date.now() - cacheEntry.timestamp < this.CACHE_TTL;
    }

    private async fetchWithRetry(url: string, retries = 3): Promise<Response> {
        for (let i = 0; i < retries; i++) {
            try {
                const response = await fetch(url, {
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                return response;
            } catch (error) {
                console.warn(`Fetch attempt ${i + 1} failed:`, error);
                if (i === retries - 1) throw error;
                await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1))); // Exponential backoff
            }
        }
        throw new Error('All fetch attempts failed');
    }

    private async fetchAnalysisData(): Promise<BackendAnalysisResponse> {
        // Check cache first
        if (this.isCacheValid(this.cache.analysis)) {
            return this.cache.analysis!.data;
        }

        try {
            const response = await this.fetchWithRetry(`${API_BASE_URL}/temperature/analysis`);
            const data: BackendAnalysisResponse = await response.json();
            
            // Cache the response
            this.cache.analysis = { data, timestamp: Date.now() };
            return data;
        } catch (error) {
            console.error('Failed to fetch analysis data:', error);
            throw error; // Don't use fallback here, let caller handle
        }
    }

    private async fetchCurrentData(): Promise<BackendCurrentResponse> {
        // Check cache first
        if (this.isCacheValid(this.cache.current)) {
            return this.cache.current!.data;
        }

        try {
            const response = await this.fetchWithRetry(`${API_BASE_URL}/temperature/current`);
            const data: BackendCurrentResponse = await response.json();
            
            // Cache the response
            this.cache.current = { data, timestamp: Date.now() };
            return data;
        } catch (error) {
            console.error('Failed to fetch current data:', error);
            throw error; // Don't use fallback here, let caller handle
        }
    }

    private getFallbackAnalysisData(): BackendAnalysisResponse {
        // Fallback data when API is unavailable
        const fallbackLocations: Record<string, BackendLocationAnalysis> = {};
        const locationConfigs = [
            { id: 'jolly-buoy', name: 'Jolly_Buoy' },
            { id: 'neel-islands', name: 'Neel Islands' },
            { id: 'mahatma-gandhi', name: 'Mahatma Gandhi Marine National Park' },
            { id: 'havelock', name: 'Havelock' },
        ];

        locationConfigs.forEach(config => {
            fallbackLocations[config.id] = {
                location_id: config.id,
                location_name: config.name,
                past_data: Array.from({ length: 8 }, (_, i) => ({
                    date: new Date(Date.now() - (7 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
                    temperature: 28.5 + Math.random() * 2,
                    is_predicted: false
                })),
                future_data: Array.from({ length: 7 }, (_, i) => ({
                    date: new Date(Date.now() + (i + 1) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
                    temperature: 29.0 + Math.random() * 2,
                    is_predicted: true
                })),
                bleaching_threshold: 29.0,
                current_dhw: 2.5,
                risk_level: 'moderate',
                last_updated: new Date().toISOString()
            };
        });

        return {
            locations: fallbackLocations,
            metadata: {
                total_locations: 4,
                prediction_window_days: 14,
                past_days: 7,
                future_days: 7,
                bleaching_threshold: 29.0
            },
            generated_at: new Date().toISOString()
        };
    }

    private getFallbackCurrentData(): BackendCurrentResponse {
        const fallbackLocations: Record<string, BackendCurrentData> = {};
        const locationConfigs = [
            { id: 'jolly-buoy', lat: 11.495, lon: 92.610 },
            { id: 'neel-islands', lat: 11.832919, lon: 93.052612 },
            { id: 'mahatma-gandhi', lat: 11.5690, lon: 92.6542 },
            { id: 'havelock', lat: 11.960000, lon: 93.000000 },
        ];

        locationConfigs.forEach(config => {
            fallbackLocations[config.id] = {
                location_id: config.id,
                current_temp: 28.5 + Math.random() * 2,
                dhw: 2.5,
                risk_level: 'moderate',
                coordinates: { lat: config.lat, lon: config.lon },
                last_updated: new Date().toISOString()
            };
        });

        return {
            locations: fallbackLocations,
            generated_at: new Date().toISOString()
        };
    }

    private convertBackendToLocationData(analysisData: BackendAnalysisResponse, currentData: BackendCurrentResponse): LocationData[] {
        const locations: LocationData[] = [];

        Object.values(analysisData.locations).forEach(analysis => {
            const current = currentData.locations[analysis.location_id];
            if (!current) return;

            // Get chlorophyll data for this location
            const chlorData = getChlorophyllForLocation(analysis.location_name, this.chlorophyllData);
            const chlorophyll = chlorData ? {
                value: Number(chlorData.chlor_a.toFixed(3)),
                riskLevel: getChlorophyllRiskLevel(chlorData.chlor_a, 0.77) as 'low' | 'moderate' | 'high',
                threshold: 0.77
            } : undefined;

            // Convert temperature readings
            const temperatureHistory: TemperatureReading[] = analysis.past_data.map(reading => ({
                date: reading.date,
                temperature: reading.temperature,
                is_predicted: reading.is_predicted
            }));

            const forecast: TemperatureReading[] = analysis.future_data.map(reading => ({
                date: reading.date,
                temperature: reading.temperature,
                is_predicted: reading.is_predicted
            }));

            // Determine trend from recent temperature data
            const recentTemps = analysis.past_data.slice(-3).map(r => r.temperature);
            let trend: 'stable' | 'increasing' | 'decreasing' = 'stable';
            if (recentTemps.length >= 2) {
                const diff = recentTemps[recentTemps.length - 1] - recentTemps[0];
                if (diff > 0.5) trend = 'increasing';
                else if (diff < -0.5) trend = 'decreasing';
            }

            locations.push({
                id: analysis.location_id,
                name: analysis.location_name,
                coordinates: { lat: current.coordinates.lat, lng: current.coordinates.lon },
                currentTemperature: Number(current.current_temp.toFixed(1)),
                riskLevel: current.risk_level as 'low' | 'moderate' | 'high',
                dhw: Number(current.dhw.toFixed(1)),
                trend,
                temperatureHistory,
                forecast,
                chlorophyll,
            });
        });

        return locations;
    }

    private async updateLocationsFromAPI() {
        try {
            const [analysisData, currentData] = await Promise.all([
                this.fetchAnalysisData(),
                this.fetchCurrentData()
            ]);

            this.locations = this.convertBackendToLocationData(analysisData, currentData);
            console.log('Successfully updated data from backend API');
            
            // Notify callbacks with new data
            this.notifyDataCallbacks();
        } catch (error) {
            console.error('Failed to update locations from API, keeping existing data:', error);
            // Keep existing data (fallback or previous API data) if update fails
        }
    }

    // Register callback for data updates
    onDataUpdate(callback: (data: LocationData[]) => void) {
        this.dataUpdateCallbacks.push(callback);
        
        // If already initialized, immediately call with current data
        if (this.isInitialized) {
            callback([...this.locations]);
        }
        
        // Return unsubscribe function
        return () => {
            const index = this.dataUpdateCallbacks.indexOf(callback);
            if (index > -1) {
                this.dataUpdateCallbacks.splice(index, 1);
            }
        };
    }

    // Get current data for all locations
    async getCurrentData(): Promise<LocationData[]> {
        // Wait for initialization if not ready
        if (!this.isInitialized) {
            await new Promise(resolve => {
                const checkInit = () => {
                    if (this.isInitialized) {
                        resolve(void 0);
                    } else {
                        setTimeout(checkInit, 10);
                    }
                };
                checkInit();
            });
        }
        
        return [...this.locations];
    }

    // Get specific location data
    async getLocationData(locationId: string): Promise<LocationData | null> {
        const locations = await this.getCurrentData();
        return locations.find(loc => loc.id === locationId) || null;
    }

    // Get 14-day temperature data (observed + forecast) - aggregated across all locations
    async getTemperatureAnalysis(): Promise<{ day: string; temp: number; threshold: number; source: string }[]> {
        try {
            const analysisData = await this.fetchAnalysisData();
            
            // Aggregate temperature data across all locations
            const allDays = new Map<string, { temps: number[]; isPredicted: boolean }>();
            
            Object.values(analysisData.locations).forEach(location => {
                // Add past data
                location.past_data.forEach(reading => {
                    const day = reading.date;
                    if (!allDays.has(day)) {
                        allDays.set(day, { temps: [], isPredicted: reading.is_predicted });
                    }
                    allDays.get(day)!.temps.push(reading.temperature);
                });
                
                // Add future data
                location.future_data.forEach(reading => {
                    const day = reading.date;
                    if (!allDays.has(day)) {
                        allDays.set(day, { temps: [], isPredicted: reading.is_predicted });
                    }
                    allDays.get(day)!.temps.push(reading.temperature);
                });
            });
            
            // Convert to chart format with averaged temperatures
            const sortedDays = Array.from(allDays.entries()).sort(([a], [b]) => a.localeCompare(b));
            
            return sortedDays.map(([date, data], index) => {
                const avgTemp = data.temps.reduce((sum, temp) => sum + temp, 0) / data.temps.length;
                return {
                    day: `Day ${index + 1}`,
                    temp: Number(avgTemp.toFixed(1)),
                    threshold: analysisData.metadata.bleaching_threshold,
                    source: data.isPredicted ? 'Forecast' : 'Observed',
                };
            });
        } catch (error) {
            console.error('Failed to get temperature analysis, using fallback:', error);
            // Return fallback data
            return Array.from({ length: 14 }, (_, i) => ({
                day: `Day ${i + 1}`,
                temp: 28.5 + Math.random() * 2,
                threshold: 29.0,
                source: i < 7 ? 'Observed' : 'Forecast',
            }));
        }
    }

    // Generate real-time alerts based on current data
    async generateAlerts(): Promise<Array<{
        id: string;
        title: string;
        location: string;
        severity: 'Critical' | 'Warning' | 'Medium';
        time: string;
        description: string;
    }>> {
        const alerts: Array<{
            id: string;
            title: string;
            location: string;
            severity: 'Critical' | 'Warning' | 'Medium';
            time: string;
            description: string;
        }> = [];

        const locations = await this.getCurrentData();

        locations.forEach(location => {
            if (location.riskLevel === 'high') {
                alerts.push({
                    id: `alert-${location.id}-temp`,
                    title: 'High Temperature Alert',
                    location: location.name,
                    severity: 'Critical' as const,
                    time: `${Math.floor(Math.random() * 30)} minutes ago`,
                    description: `Water temperature ${location.currentTemperature}°C exceeds safe threshold`,
                });
            }

            if (location.dhw >= 4) {
                alerts.push({
                    id: `alert-${location.id}-dhw`,
                    title: 'Coral Bleaching Risk',
                    location: location.name,
                    severity: location.dhw >= 8 ? 'Critical' : 'Warning',
                    time: `${Math.floor(Math.random() * 60)} minutes ago`,
                    description: `DHW ${location.dhw} °C-weeks indicates bleaching stress`,
                });
            }

            if (location.trend === 'increasing' && location.riskLevel !== 'low') {
                alerts.push({
                    id: `alert-${location.id}-trend`,
                    title: 'Temperature Rising',
                    location: location.name,
                    severity: 'Medium' as const,
                    time: `${Math.floor(Math.random() * 120)} minutes ago`,
                    description: 'Upward temperature trend detected',
                });
            }
        });

        return alerts.slice(0, 3); // Return top 3 alerts
    }

    // Start real-time updates
    startRealtimeUpdates(callback: (data: LocationData[]) => void, intervalMs: number = 300000) { // 5 minutes
        // Register the callback for immediate updates
        const unsubscribe = this.onDataUpdate(callback);
        
        if (this.intervalId) {
            clearInterval(this.intervalId);
        }

        this.intervalId = setInterval(async () => {
            // Refresh data from API
            await this.updateLocationsFromAPI();
        }, intervalMs);
        
        // Return cleanup function
        return () => {
            unsubscribe();
            this.stopRealtimeUpdates();
        };
    }

    // Stop real-time updates
    stopRealtimeUpdates() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }

    // Force refresh from backend
    async forceRefresh(): Promise<void> {
        await this.updateLocationsFromAPI();
    }
}

// Export singleton instance
export const realtimeService = new RealtimeDataService();