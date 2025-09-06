"use client"

import { useState, useEffect, useCallback } from 'react'
import { backendRealtimeService, type LocationData } from '@/lib/services/backendRealtimeService'
import type { SystemStatusData, AlertData } from '@/lib/services/backendRealtimeService'

// Hook for real-time location data
export function useRealtimeLocations() {
  const [locations, setLocations] = useState<LocationData[]>([])
  const [loading, setLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  const updateData = useCallback((newData: LocationData[]) => {
    setLocations(newData)
    setLastUpdated(new Date())
  }, [])

  useEffect(() => {
    // Initial load
    const initialData = backendRealtimeService.getCurrentData()
    setLocations(initialData)
    setLoading(false)
    setLastUpdated(new Date())

    // Start real-time updates every 30 seconds
    backendRealtimeService.startRealtimeUpdates(updateData, 30000)

    return () => {
      backendRealtimeService.stopRealtimeUpdates()
    }
  }, [updateData])

  return { locations, loading, lastUpdated }
}

// Hook for temperature analysis data
export function useTemperatureAnalysis() {
  const [data, setData] = useState<Array<{
    day: string
    temp: number
    threshold: number
    source: string
  }>>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Function to update temperature data
    const updateTemperatureData = () => {
      const connectionStatus = backendRealtimeService.getConnectionStatus()
      const analysisData = backendRealtimeService.getTemperatureAnalysis()
      
      setData(analysisData)
      
      // Only set loading to false when we have a successful connection and data
      if (connectionStatus === 'connected' && analysisData.length > 0) {
        setLoading(false)
      } else if (connectionStatus === 'error') {
        setLoading(false) // Stop loading on error too
      }
    }

    // Initial fetch
    updateTemperatureData()
    
    // Set up rapid polling for initial connection
    const fastInterval = setInterval(updateTemperatureData, 3000) // Check every 3 seconds

    // After 30 seconds, switch to normal polling aligned with backend updates
    const transitionTimeout = setTimeout(() => {
      clearInterval(fastInterval)
      
      // Now sync with backend update cycle (every 30 seconds)
      const normalInterval = setInterval(updateTemperatureData, 30000)
      
      return () => clearInterval(normalInterval)
    }, 30000)

    return () => {
      clearInterval(fastInterval)
      clearTimeout(transitionTimeout)
    }
  }, [])

  return { data, loading }
}

// Hook for temperature page specific data format
export function useTemperaturePageData() {
  const [data, setData] = useState<Array<{
    date: string;
    temp: number;
    threshold: number;
    site: string;
  }>>([])

  useEffect(() => {
    const analysisData = backendRealtimeService.getTemperatureAnalysis()
    if (analysisData.length > 0) {
      const formattedData = analysisData.map((item, index) => ({
        date: `2025-03-${String(index + 1).padStart(2, '0')}`,
        temp: item.temp,
        threshold: item.threshold,
        site: "Andaman Islands"
      }))
      setData(formattedData)
    } else {
      setData([])
    }
    
    // Update temperature analysis every minute
    const interval = setInterval(() => {
      const newAnalysisData = backendRealtimeService.getTemperatureAnalysis()
      if (newAnalysisData.length > 0) {
        const newFormattedData = newAnalysisData.map((item, index) => ({
          date: `2025-03-${String(index + 1).padStart(2, '0')}`,
          temp: item.temp,
          threshold: item.threshold,
          site: "Andaman Islands"
        }))
        setData(newFormattedData)
      } else {
        setData([])
      }
    }, 60000)

    return () => clearInterval(interval)
  }, [])

  return { data }
}

// Hook for real-time alerts
export function useRealtimeAlerts() {
  const [alerts, setAlerts] = useState<AlertData[]>([])

  useEffect(() => {
    const updateAlerts = () => {
      const newAlerts = backendRealtimeService.generateAlerts()
      setAlerts(newAlerts)
    }

    // Initial load
    updateAlerts()

    // Update alerts every 2 minutes
    const interval = setInterval(updateAlerts, 2 * 60 * 1000)

    return () => clearInterval(interval)
  }, [])

  return { alerts }
}

// Hook for specific location data
export function useLocationData(locationId: string) {
  const [locationData, setLocationData] = useState<LocationData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const data = backendRealtimeService.getLocationData(locationId)
    setLocationData(data)
    setLoading(false)
  }, [locationId])

  return { locationData, loading }
}

// Hook for enhanced system status with backend integration
export function useSystemStatus() {
  const [status, setStatus] = useState<SystemStatusData>({
    satelliteDataFeed: 'Online',
    aiProcessingEngine: 'Active',
    alertSystem: 'Operational',
    dataSync: 'Connecting...',
    backendConnection: 'disconnected',
    modelStatus: 'Unknown',
    lastModelRun: null,
    nextScheduledRun: null
  })

  useEffect(() => {
    const updateStatus = () => {
      const newStatus = backendRealtimeService.getSystemStatus()
      setStatus(newStatus)
    }

    // Initial load
    updateStatus()

    // Update status every 30 seconds
    const interval = setInterval(updateStatus, 30 * 1000)

    return () => clearInterval(interval)
  }, [])

  return { status }
}

// Hook for backend connection status
export function useBackendConnection() {
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'error'>('disconnected')
  const [lastChecked, setLastChecked] = useState<Date | null>(null)

  useEffect(() => {
    const checkConnection = () => {
      const status = backendRealtimeService.getConnectionStatus()
      setConnectionStatus(status)
      setLastChecked(new Date())
    }

    // Initial check
    checkConnection()

    // Check every 10 seconds initially, then every 30 seconds
    const initialInterval = setInterval(checkConnection, 10 * 1000)
    
    // After 1 minute, switch to 30-second intervals
    setTimeout(() => {
      clearInterval(initialInterval)
      const regularInterval = setInterval(checkConnection, 30 * 1000)
      
      return () => clearInterval(regularInterval)
    }, 60 * 1000)

    return () => {
      clearInterval(initialInterval)
    }
  }, [])

  return { connectionStatus, lastChecked }
}

// Hook for triggering manual model runs
export function useModelExecution() {
  const [isRunning, setIsRunning] = useState(false)
  const [lastResult, setLastResult] = useState<string | null>(null)

  const triggerRun = useCallback(async () => {
    setIsRunning(true)
    try {
      const success = await backendRealtimeService.triggerModelRun()
      setLastResult(success ? 'Model run triggered successfully' : 'Failed to trigger model run')
    } catch (error) {
      setLastResult(`Error: ${error}`)
    } finally {
      setIsRunning(false)
    }
  }, [])

  return { triggerRun, isRunning, lastResult }
}

// Hook for scheduler information
export function useSchedulerStatus() {
  const [schedulerInfo, setSchedulerInfo] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchSchedulerInfo = async () => {
      setLoading(true)
      try {
        const info = await backendRealtimeService.getSchedulerInfo()
        setSchedulerInfo(info)
      } catch (error) {
        console.error('Failed to fetch scheduler info:', error)
      } finally {
        setLoading(false)
      }
    }

    // Initial fetch
    fetchSchedulerInfo()

    // Update every 2 minutes
    const interval = setInterval(fetchSchedulerInfo, 2 * 60 * 1000)

    return () => clearInterval(interval)
  }, [])

  return { schedulerInfo, loading }
}