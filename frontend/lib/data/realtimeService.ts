// Real-time data service using CSV data from models folder
export interface TemperatureReading {
    date: string;
    temperature: number;
    anomaly: number;
    riskLevel: 'Safe' | 'Watch' | 'Warning' | 'Critical';
    source: 'Observed' | 'Forecast';
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
}

// Simulated real-time data based on CSV patterns
const csvData: TemperatureReading[] = [
    { date: '2025-03-01', temperature: 28.09726, anomaly: 0.0, riskLevel: 'Safe', source: 'Observed' },
    { date: '2025-03-02', temperature: 28.29726, anomaly: 0.2, riskLevel: 'Safe', source: 'Observed' },
    { date: '2025-03-03', temperature: 27.99726, anomaly: -0.1, riskLevel: 'Safe', source: 'Observed' },
    { date: '2025-03-04', temperature: 28.897259, anomaly: 0.8, riskLevel: 'Watch', source: 'Observed' },
    { date: '2025-03-05', temperature: 29.29726, anomaly: 1.2, riskLevel: 'Watch', source: 'Observed' },
    { date: '2025-03-06', temperature: 29.59726, anomaly: 1.5, riskLevel: 'Warning', source: 'Observed' },
    { date: '2025-03-07', temperature: 29.897259, anomaly: 1.8, riskLevel: 'Warning', source: 'Observed' },
    { date: '2025-03-08', temperature: 30.59726, anomaly: 2.5, riskLevel: 'Critical', source: 'Observed' },
    { date: '2025-03-09', temperature: 30.897259, anomaly: 2.8, riskLevel: 'Critical', source: 'Observed' },
    { date: '2025-03-10', temperature: 31.09726, anomaly: 3.0, riskLevel: 'Critical', source: 'Observed' },
    { date: '2025-03-11', temperature: 30.79726, anomaly: 2.7, riskLevel: 'Critical', source: 'Observed' },
    { date: '2025-03-12', temperature: 30.69726, anomaly: 2.6, riskLevel: 'Critical', source: 'Observed' },
    { date: '2025-03-13', temperature: 29.897259, anomaly: 1.8, riskLevel: 'Warning', source: 'Observed' },
    { date: '2025-03-14', temperature: 29.29726, anomaly: 1.2, riskLevel: 'Watch', source: 'Observed' },
    { date: '2025-03-15', temperature: 31.05989697802198, anomaly: 2.9626369780219797, riskLevel: 'Critical', source: 'Forecast' },
    { date: '2025-03-16', temperature: 31.24539147032967, anomaly: 3.1481314703296697, riskLevel: 'Critical', source: 'Forecast' },
    { date: '2025-03-17', temperature: 31.430885962637362, anomaly: 3.333625962637363, riskLevel: 'Critical', source: 'Forecast' },
    { date: '2025-03-18', temperature: 31.616380454945055, anomaly: 3.5191204549450568, riskLevel: 'Critical', source: 'Forecast' },
    { date: '2025-03-19', temperature: 31.801874947252745, anomaly: 3.7046149472527468, riskLevel: 'Critical', source: 'Forecast' },
    { date: '2025-03-20', temperature: 31.98736943956044, anomaly: 3.8901094395604403, riskLevel: 'Critical', source: 'Forecast' },
    { date: '2025-03-21', temperature: 32.17286393186813, anomaly: 4.07560393186813, riskLevel: 'Critical', source: 'Forecast' },
];

// Generate variations for different locations
function generateLocationVariation(baseData: TemperatureReading[], locationOffset: number): TemperatureReading[] {
    return baseData.map(reading => ({
        ...reading,
        temperature: reading.temperature + locationOffset + (Math.random() - 0.5) * 0.5,
        anomaly: reading.anomaly + locationOffset * 0.3,
    }));
}

// Calculate DHW from temperature data
function calculateDHW(temperatureData: TemperatureReading[], mmm: number = 29.0): number {
    const hotspots = temperatureData
        .slice(-84) // Last 84 days (12 weeks)
        .map(reading => Math.max(0, reading.temperature - mmm))
        .filter(hs => hs >= 1.0); // Only count anomalies >= 1°C

    return hotspots.reduce((sum, hs) => sum + hs, 0) / 7.0;
}

// Determine risk level from DHW and current temperature
function assessRisk(dhw: number, currentTemp: number, mmm: number = 29.0): 'low' | 'moderate' | 'high' {
    const anomaly = currentTemp - mmm;

    if (dhw >= 4 || anomaly >= 2.0) return 'high';
    if (dhw >= 2 || anomaly >= 1.0) return 'moderate';
    return 'low';
}

// Calculate trend from recent data
function calculateTrend(recentData: TemperatureReading[]): 'stable' | 'increasing' | 'decreasing' {
    if (recentData.length < 3) return 'stable';

    const recent = recentData.slice(-3);
    const firstTemp = recent[0].temperature;
    const lastTemp = recent[recent.length - 1].temperature;
    const diff = lastTemp - firstTemp;

    if (diff > 0.5) return 'increasing';
    if (diff < -0.5) return 'decreasing';
    return 'stable';
}

export class RealtimeDataService {
    private locations: LocationData[] = [];
    private currentDataIndex = 0;
    private intervalId: NodeJS.Timeout | null = null;

    constructor() {
        this.initializeLocations();
    }

    private initializeLocations() {
        const locationConfigs = [
            { id: 'north-andaman', name: 'North Andaman', lat: 13.2500, lon: 92.9167, offset: 0 },
            { id: 'neel-islands', name: 'Neel Islands', lat: 11.832919, lon: 93.052612, offset: -0.6 },
            { id: 'mahatma-gandhi', name: 'Mahatma Gandhi Marine National Park', lat: 11.5690, lon: 92.6542, offset: 0.3 },
            { id: 'havelock', name: 'Havelock', lat: 11.960000, lon: 93.000000, offset: -0.4 },
        ];

        this.locations = locationConfigs.map(config => {
            const locationData = generateLocationVariation(csvData, config.offset);
            const observedData = locationData.filter(d => d.source === 'Observed');
            const forecastData = locationData.filter(d => d.source === 'Forecast');
            const currentReading = observedData[observedData.length - 1];
            const dhw = calculateDHW(observedData);

            return {
                id: config.id,
                name: config.name,
                coordinates: { lat: config.lat, lng: config.lon },
                currentTemperature: Number(currentReading.temperature.toFixed(1)),
                riskLevel: assessRisk(dhw, currentReading.temperature),
                dhw: Number(dhw.toFixed(1)),
                trend: calculateTrend(observedData.slice(-7)),
                temperatureHistory: observedData,
                forecast: forecastData,
            };
        });
    }

    // Get current data for all locations
    getCurrentData(): LocationData[] {
        return this.locations.map(location => ({
            ...location,
            // Add small real-time variations
            currentTemperature: Number((location.currentTemperature + (Math.random() - 0.5) * 0.1).toFixed(1)),
        }));
    }

    // Get specific location data
    getLocationData(locationId: string): LocationData | null {
        return this.locations.find(loc => loc.id === locationId) || null;
    }

    // Get 14-day temperature data (observed + forecast)
    getTemperatureAnalysis(): { day: string; temp: number; threshold: number; source: string }[] {
        const observedData = csvData.filter(d => d.source === 'Observed').slice(-7);
        const forecastData = csvData.filter(d => d.source === 'Forecast').slice(0, 7);

        return [...observedData, ...forecastData].map((reading, index) => ({
            day: `Day ${index + 1}`,
            temp: Number(reading.temperature.toFixed(1)),
            threshold: 29.0,
            source: reading.source,
        }));
    }

    // Generate real-time alerts
    generateAlerts(): Array<{
        id: string;
        title: string;
        location: string;
        severity: 'Critical' | 'Warning' | 'Medium';
        time: string;
        description: string;
    }> {
        const alerts: Array<{
            id: string;
            title: string;
            location: string;
            severity: 'Critical' | 'Warning' | 'Medium';
            time: string;
            description: string;
        }> = [];
        const now = new Date();

        this.locations.forEach(location => {
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
    startRealtimeUpdates(callback: (data: LocationData[]) => void, intervalMs: number = 30000) {
        if (this.intervalId) {
            clearInterval(this.intervalId);
        }

        this.intervalId = setInterval(() => {
            // Simulate small real-time changes
            this.locations = this.locations.map(location => ({
                ...location,
                currentTemperature: Number((location.currentTemperature + (Math.random() - 0.5) * 0.2).toFixed(1)),
            }));

            callback(this.getCurrentData());
        }, intervalMs);
    }

    // Stop real-time updates
    stopRealtimeUpdates() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }
}

// Export singleton instance
export const realtimeService = new RealtimeDataService();