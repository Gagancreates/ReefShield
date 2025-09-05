"use client"

import { Map } from "./map"

interface ReefSite {
  id: number
  name: string
  health: number
  status: "healthy" | "at-risk" | "critical"
  temperature: number
  alerts: number
  coordinates: [number, number]
}

interface GlobalMapProps {
  reefSites: ReefSite[]
  className?: string
}

export function GlobalMap({ reefSites, className = "" }: GlobalMapProps) {
  const markers = reefSites.map((site) => ({
    position: site.coordinates,
    popup: `
      <div class="p-2">
        <h3 class="font-semibold text-sm">${site.name}</h3>
        <p class="text-xs text-gray-600">Health: ${site.health}%</p>
        <p class="text-xs text-gray-600">Temperature: ${site.temperature}°C</p>
        <p class="text-xs text-gray-600">Alerts: ${site.alerts}</p>
      </div>
    `,
    status: site.status,
  }))

  return (
    <Map
      center={[12.5, 93]} // Centered on Andaman Islands
      zoom={8}
      markers={markers}
      className={className}
    />
  )
}