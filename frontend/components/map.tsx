"use client"

import { useEffect, useRef } from "react"
import L from "leaflet"
import "leaflet/dist/leaflet.css"

// Fix for default markers in Leaflet with Next.js
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
  iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
})

interface MapProps {
  center: [number, number]
  zoom?: number
  markers?: Array<{
    position: [number, number]
    popup?: string
    status?: "healthy" | "at-risk" | "critical"
  }>
  className?: string
}

export function Map({ center, zoom = 10, markers = [], className = "" }: MapProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<L.Map | null>(null)

  useEffect(() => {
    if (!mapRef.current || mapInstanceRef.current) return

    // Initialize map
    const map = L.map(mapRef.current).setView(center, zoom)

    // Add tile layer
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map)

    mapInstanceRef.current = map

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove()
        mapInstanceRef.current = null
      }
    }
  }, [center, zoom])

  useEffect(() => {
    if (!mapInstanceRef.current) return

    // Clear existing markers
    mapInstanceRef.current.eachLayer((layer) => {
      if (layer instanceof L.Marker) {
        mapInstanceRef.current?.removeLayer(layer)
      }
    })

    // Add new markers
    markers.forEach((marker) => {
      if (!mapInstanceRef.current) return

      const getMarkerColor = (status?: string) => {
        switch (status) {
          case "healthy":
            return "#10b981" // emerald-500
          case "at-risk":
            return "#f59e0b" // amber-500
          case "critical":
            return "#ef4444" // red-500
          default:
            return "#6b7280" // gray-500
        }
      }

      const customIcon = L.divIcon({
        className: "custom-marker",
        html: `<div style="
          width: 20px;
          height: 20px;
          border-radius: 50%;
          background-color: ${getMarkerColor(marker.status)};
          border: 3px solid white;
          box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        "></div>`,
        iconSize: [20, 20],
        iconAnchor: [10, 10],
      })

      const leafletMarker = L.marker(marker.position, { icon: customIcon }).addTo(mapInstanceRef.current)

      if (marker.popup) {
        leafletMarker.bindPopup(marker.popup)
      }
    })
  }, [markers])

  return <div ref={mapRef} className={`w-full h-full ${className}`} />
}