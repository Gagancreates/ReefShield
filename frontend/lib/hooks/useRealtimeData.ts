"use client"

import { useState, useEffect, useCallback } from 'react'
import { realtimeService, type LocationData } from '@/lib/data/realtimeService'

// Hook for real-time location data
export function useRealtimeLocations() {
  const [locations, setLocations] = useState<LocationData[]>([])
  const [loading, setLoading] = useState(false) // Changed to false since we show fallback immediately
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)
  const [isUsingFallback, setIsUsingFallback] = useState(true) // Track if using fallback data

  const updateData = useCallback((newData: LocationData[]) => {
    setLocations(newData)
    setLastUpdated(new Date())
    setIsUsingFallback(false) // Backend data received
    setLoading(false)
  }, [])

  useEffect(() => {
    // Subscribe to data updates (will immediately receive fallback data)
    const unsubscribe = realtimeService.onDataUpdate((data) => {
      setLocations(data)
      setLastUpdated(new Date())
      setLoading(false)
    })

    // Start real-time updates every 5 minutes
    const stopUpdates = realtimeService.startRealtimeUpdates(updateData, 300000)

    return () => {
      unsubscribe()
      stopUpdates()
    }
  }, [updateData])

  // Method to force refresh from backend
  const forceRefresh = useCallback(async () => {
    setLoading(true)
    try {
      await realtimeService.forceRefresh()
    } catch (error) {
      console.error('Failed to force refresh:', error)
      setLoading(false)
    }
  }, [])

  return { 
    locations, 
    loading, 
    lastUpdated, 
    isUsingFallback, 
    forceRefresh 
  }
}

// Hook for temperature analysis data
export function useTemperatureAnalysis() {
  const [data, setData] = useState<Array<{
    day: string
    temp: number
    threshold: number
    source: string
  }>>([])
  const [loading, setLoading] = useState(false) // Shows fallback immediately
  const [isUsingFallback, setIsUsingFallback] = useState(true)

  useEffect(() => {
    const loadAnalysisData = async () => {
      try {
        // This will return fallback data immediately if backend fails
        const analysisData = await realtimeService.getTemperatureAnalysis()
        setData(analysisData)
        setIsUsingFallback(false) // Assume backend data if no error
      } catch (error) {
        console.error('Failed to load temperature analysis:', error)
        // Generate fallback data directly
        const fallbackData = Array.from({ length: 14 }, (_, i) => ({
          day: `Day ${i + 1}`,
          temp: Number((28.5 + Math.random() * 2).toFixed(1)),
          threshold: 29.0,
          source: i < 7 ? 'Observed' : 'Forecast',
        }))
        setData(fallbackData)
        setIsUsingFallback(true)
      } finally {
        setLoading(false)
      }
    }

    // Load immediately (will show fallback if backend unavailable)
    loadAnalysisData()

    // Retry backend data every 5 minutes
    const interval = setInterval(loadAnalysisData, 5 * 60 * 1000)

    return () => clearInterval(interval)
  }, [])

  const forceRefresh = useCallback(async () => {
    setLoading(true)
    try {
      const analysisData = await realtimeService.getTemperatureAnalysis()
      setData(analysisData)
      setIsUsingFallback(false)
    } catch (error) {
      console.error('Failed to refresh temperature analysis:', error)
    } finally {
      setLoading(false)
    }
  }, [])

  return { data, loading, isUsingFallback, forceRefresh }
}

// Hook for real-time alerts
export function useRealtimeAlerts() {
  const [alerts, setAlerts] = useState<Array<{
    id: string
    title: string
    location: string
    severity: 'Critical' | 'Warning' | 'Medium'
    time: string
    description: string
  }>>([])
  const [loading, setLoading] = useState(false)
  const [isUsingFallback, setIsUsingFallback] = useState(true)

  // Generate fallback alerts
  const generateFallbackAlerts = useCallback(() => {
    const fallbackAlerts = [
      {
        id: 'fallback-alert-1',
        title: 'Temperature Monitoring Active',
        location: 'Jolly_Buoy',
        severity: 'Medium' as const,
        time: '2 minutes ago',
        description: 'System monitoring coral reef temperatures',
      },
      {
        id: 'fallback-alert-2',
        title: 'Coral Health Check',
        location: 'Havelock',
        severity: 'Medium' as const,
        time: '15 minutes ago',
        description: 'Regular health assessment in progress',
      }
    ]
    return fallbackAlerts
  }, [])

  useEffect(() => {
    const updateAlerts = async () => {
      try {
        const newAlerts = await realtimeService.generateAlerts()
        setAlerts(newAlerts)
        setIsUsingFallback(false)
      } catch (error) {
        console.error('Failed to update alerts, using fallback:', error)
        setAlerts(generateFallbackAlerts())
        setIsUsingFallback(true)
      } finally {
        setLoading(false)
      }
    }

    // Show fallback alerts immediately
    setAlerts(generateFallbackAlerts())

    // Try to load real alerts
    updateAlerts()

    // Update alerts every 2 minutes
    const interval = setInterval(updateAlerts, 2 * 60 * 1000)

    return () => clearInterval(interval)
  }, [generateFallbackAlerts])

  const forceRefresh = useCallback(async () => {
    setLoading(true)
    try {
      const newAlerts = await realtimeService.generateAlerts()
      setAlerts(newAlerts)
      setIsUsingFallback(false)
    } catch (error) {
      console.error('Failed to refresh alerts:', error)
      setAlerts(generateFallbackAlerts())
      setIsUsingFallback(true)
    } finally {
      setLoading(false)
    }
  }, [generateFallbackAlerts])

  return { alerts, loading, isUsingFallback, forceRefresh }
}

// Hook for specific location data
export function useLocationData(locationId: string) {
  const [locationData, setLocationData] = useState<LocationData | null>(null)
  const [loading, setLoading] = useState(false) // Show fallback immediately
  const [isUsingFallback, setIsUsingFallback] = useState(true)

  useEffect(() => {
    const loadLocationData = async () => {
      try {
        // This will return fallback data immediately via the service
        const data = await realtimeService.getLocationData(locationId)
        setLocationData(data)
        setIsUsingFallback(false) // Assume backend data if found
      } catch (error) {
        console.error('Failed to load location data:', error)
      } finally {
        setLoading(false)
      }
    }

    // Load immediately (will show fallback if available)
    loadLocationData()

    // Subscribe to updates for this specific location
    const unsubscribe = realtimeService.onDataUpdate((allLocations) => {
      const location = allLocations.find(loc => loc.id === locationId)
      if (location) {
        setLocationData(location)
        setIsUsingFallback(false)
        setLoading(false)
      }
    })

    return () => {
      unsubscribe()
    }
  }, [locationId])

  const forceRefresh = useCallback(async () => {
    setLoading(true)
    try {
      await realtimeService.forceRefresh()
      const data = await realtimeService.getLocationData(locationId)
      setLocationData(data)
      setIsUsingFallback(false)
    } catch (error) {
      console.error('Failed to refresh location data:', error)
    } finally {
      setLoading(false)
    }
  }, [locationId])

  return { locationData, loading, isUsingFallback, forceRefresh }
}

// Hook for system status simulation
export function useSystemStatus() {
  const [status, setStatus] = useState({
    satelliteDataFeed: 'Online',
    aiProcessingEngine: 'Active', 
    alertSystem: 'Operational',
    dataSync: 'Using Fallback Data' // Start with fallback indication
  })
  const [isUsingFallback, setIsUsingFallback] = useState(true)

  useEffect(() => {
    // Subscribe to data updates to know when backend is available
    const unsubscribe = realtimeService.onDataUpdate(() => {
      setStatus(prev => ({
        ...prev,
        dataSync: 'Synced with Backend'
      }))
      setIsUsingFallback(false)
    })

    const updateStatus = () => {
      // Simulate occasional status changes
      const statuses = ['Online', 'Active', 'Operational']
      const syncStatuses = isUsingFallback 
        ? ['Using Fallback Data', 'Waiting for Backend', 'Retrying Connection']
        : ['Synced with Backend', 'Updating', 'Live Data']
      
      const randomSyncStatus = syncStatuses[Math.floor(Math.random() * syncStatuses.length)]
      
      setStatus(prev => ({
        satelliteDataFeed: statuses[Math.floor(Math.random() * statuses.length)],
        aiProcessingEngine: statuses[Math.floor(Math.random() * statuses.length)],
        alertSystem: statuses[Math.floor(Math.random() * statuses.length)],
        dataSync: Math.random() > 0.8 ? randomSyncStatus : prev.dataSync
      }))
    }

    // Update status every 5 minutes
    const interval = setInterval(updateStatus, 5 * 60 * 1000)

    return () => {
      clearInterval(interval)
      unsubscribe()
    }
  }, [isUsingFallback])

  return { status, isUsingFallback }
}

// New utility hook to check overall system connectivity
export function useConnectivityStatus() {
  const [isConnected, setIsConnected] = useState(false)
  const [connectionType, setConnectionType] = useState<'backend' | 'fallback'>('fallback')
  const [lastBackendSync, setLastBackendSync] = useState<Date | null>(null)

  useEffect(() => {
    // Subscribe to data updates to track connectivity
    const unsubscribe = realtimeService.onDataUpdate((data) => {
      if (data && data.length > 0) {
        setIsConnected(true)
        // Check if this looks like real backend data (has recent timestamps, etc.)
        const hasRecentData = data.some(location => 
          location.temperatureHistory.some(reading => 
            new Date(reading.date).getTime() > Date.now() - 24 * 60 * 60 * 1000
          )
        )
        
        if (hasRecentData) {
          setConnectionType('backend')
          setLastBackendSync(new Date())
        } else {
          setConnectionType('fallback')
        }
      } else {
        setIsConnected(false)
        setConnectionType('fallback')
      }
    })

    return unsubscribe
  }, [])

  const testConnection = useCallback(async () => {
    try {
      await realtimeService.forceRefresh()
      return true
    } catch {
      return false
    }
  }, [])

  return {
    isConnected,
    connectionType,
    lastBackendSync,
    testConnection
  }
}

// --- New hook for 14-day combined temperature data ---
export function useCombinedTemperatureData() {
  const [data, setData] = useState<Array<{ day: string, temp: number, threshold: number, source: string }>>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchCombinedData() {
      setLoading(true)
      setError(null)
      try {
        const res = await fetch(
          process.env.NEXT_PUBLIC_API_URL
            ? process.env.NEXT_PUBLIC_API_URL + '/v1/combined-data'
            : 'http://localhost:8000/api/v1/combined-data'
        )
        if (!res.ok) throw new Error('Failed to fetch combined temperature data')
        const json = await res.json()
        // json.data is an array of { date, temperature, source }
        const chartData = json.data.map((item: any, idx: number) => ({
          day: `Day ${idx + 1}`,
          temp: Number(item.temperature),
          threshold: 29.0, // hardcoded bleaching threshold
          source: item.source,
        }))
        setData(chartData)
      } catch (e: any) {
        setError(e.message || 'Unknown error')
        setData([])
      } finally {
        setLoading(false)
      }
    }
    fetchCombinedData()
  }, [])

  return { data, loading, error }
}