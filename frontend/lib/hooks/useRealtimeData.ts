"use client"

import { useState, useEffect, useCallback } from 'react'
import { realtimeService, type LocationData } from '@/lib/data/realtimeService'

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
    const initialData = realtimeService.getCurrentData()
    setLocations(initialData)
    setLoading(false)
    setLastUpdated(new Date())

    // Start real-time updates every 30 seconds
    realtimeService.startRealtimeUpdates(updateData, 30000)

    return () => {
      realtimeService.stopRealtimeUpdates()
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

  useEffect(() => {
    const analysisData = realtimeService.getTemperatureAnalysis()
    setData(analysisData)
  }, [])

  return { data }
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

  useEffect(() => {
    const updateAlerts = () => {
      const newAlerts = realtimeService.generateAlerts()
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
    const data = realtimeService.getLocationData(locationId)
    setLocationData(data)
    setLoading(false)
  }, [locationId])

  return { locationData, loading }
}

// Hook for system status simulation
export function useSystemStatus() {
  const [status, setStatus] = useState({
    satelliteDataFeed: 'Online',
    aiProcessingEngine: 'Active', 
    alertSystem: 'Operational',
    dataSync: 'Syncing'
  })

  useEffect(() => {
    const updateStatus = () => {
      // Simulate occasional status changes
      const statuses = ['Online', 'Active', 'Operational', 'Syncing', 'Updating']
      const randomStatus = statuses[Math.floor(Math.random() * statuses.length)]
      
      setStatus(prev => ({
        ...prev,
        dataSync: Math.random() > 0.8 ? randomStatus : 'Syncing'
      }))
    }

    // Update status every 5 minutes
    const interval = setInterval(updateStatus, 5 * 60 * 1000)

    return () => clearInterval(interval)
  }, [])

  return { status }
}