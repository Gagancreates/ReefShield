"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { MapPin, Search, Filter, Layers, ZoomIn, ZoomOut, RotateCcw, RefreshCw } from "lucide-react"
import { GlobalMap } from "@/components/global-map"
import { useRealtimeLocations } from "@/lib/hooks/useRealtimeData"

export default function MapPage() {
  // Real-time data hooks
  const { locations: realtimeLocations, loading, lastUpdated } = useRealtimeLocations()

  // Convert real-time data to reef sites format
  const reefSites = realtimeLocations.map((loc, index) => ({
    id: index + 1,
    name: loc.name,
    lat: loc.coordinates.lat,
    lng: loc.coordinates.lng,
    health: loc.riskLevel === 'low' ? 90 : loc.riskLevel === 'moderate' ? 75 : 60,
    status: loc.riskLevel === 'low' ? 'healthy' as const : loc.riskLevel === 'moderate' ? 'at-risk' as const : 'critical' as const,
    temperature: loc.currentTemperature,
    alerts: loc.riskLevel === 'high' ? 3 : loc.riskLevel === 'moderate' ? 1 : 0,
    lastUpdate: lastUpdated ? `${Math.floor((Date.now() - lastUpdated.getTime()) / 60000)} minutes ago` : 'Just now',
    coordinates: [loc.coordinates.lat, loc.coordinates.lng] as [number, number],
    dhw: loc.dhw,
    trend: loc.trend,
    riskLevel: loc.riskLevel
  }))

  const [selectedSite, setSelectedSite] = useState<(typeof reefSites)[0] | null>(null)
  const [filterStatus, setFilterStatus] = useState("all")
  const [searchTerm, setSearchTerm] = useState("")

  const filteredSites = reefSites.filter((site) => {
    const matchesSearch = site.name.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesFilter = filterStatus === "all" || site.status === filterStatus
    return matchesSearch && matchesFilter
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case "healthy":
        return "bg-emerald-500"
      case "at-risk":
        return "bg-amber-500"
      case "critical":
        return "bg-red-500"
      default:
        return "bg-gray-500"
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "healthy":
        return "default"
      case "at-risk":
        return "secondary"
      case "critical":
        return "destructive"
      default:
        return "secondary"
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-serif text-4xl font-bold text-gray-900">Reef Map</h1>
          <p className="text-muted-foreground">
            Interactive monitoring of Andaman Islands coral reef sites
            {lastUpdated && (
              <span className="ml-2 text-xs text-green-600">
                • Live (Updated {lastUpdated.toLocaleTimeString()})
              </span>
            )}
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Layers className="h-4 w-4 mr-2" />
            Layers
          </Button>
          <Button variant="outline" size="sm">
            <Filter className="h-4 w-4 mr-2" />
            Filters
          </Button>
        </div>
      </div>

      {/* Search and Filter Controls */}
      <div className="flex gap-4 items-center">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-600" />
          <Input
            placeholder="Search reef sites..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 text-gray-900 placeholder:text-gray-500 border-2 border-gray-300 focus:border-blue-500"
          />
        </div>
        <Select value={filterStatus} onValueChange={setFilterStatus}>
          <SelectTrigger className="w-40 text-gray-900 border-2 border-gray-300 focus:border-blue-500">
            <SelectValue />
          </SelectTrigger>
          <SelectContent className="bg-white border-2 border-gray-300">
            <SelectItem value="all" className="text-gray-900 hover:bg-gray-100">
              All Sites
            </SelectItem>
            <SelectItem value="healthy" className="text-gray-900 hover:bg-gray-100">
              Healthy
            </SelectItem>
            <SelectItem value="at-risk" className="text-gray-900 hover:bg-gray-100">
              At Risk
            </SelectItem>
            <SelectItem value="critical" className="text-gray-900 hover:bg-gray-100">
              Critical
            </SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Map Container */}
        <div className="lg:col-span-2">
          <Card className="bg-gradient-to-br from-blue-50 to-cyan-50 border-2 border-gray-800 shadow-lg">
            <CardHeader>
              <CardTitle className="font-serif text-2xl text-blue-900">Andaman Islands Reef Monitoring</CardTitle>
              <CardDescription>
                Real-time status of coral reef sites in Andaman Islands
                {lastUpdated && (
                  <span className="ml-2 text-xs text-green-600">
                    • Live (Updated {lastUpdated.toLocaleTimeString()})
                  </span>
                )}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="relative h-96 rounded-lg overflow-hidden">
                <GlobalMap reefSites={filteredSites} className="rounded-lg" />

                <div className="absolute bottom-4 left-4 bg-white p-3 rounded-lg shadow-lg border z-[1000]">
                  <div className="text-sm font-semibold mb-2 text-gray-800">Site Status</div>
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-emerald-500 border border-white shadow-sm"></div>
                      <span className="text-xs font-medium">Healthy</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-amber-500 border border-white shadow-sm"></div>
                      <span className="text-xs font-medium">At Risk</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-red-500 border border-white shadow-sm"></div>
                      <span className="text-xs font-medium">Critical</span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Site Details Panel */}
        <div className="space-y-4">
          {selectedSite ? (
            <Card className="border-2 border-gray-800 shadow-lg">
              <CardHeader>
                <CardTitle className="font-serif text-2xl">{selectedSite.name}</CardTitle>
                <CardDescription>Site details and current status</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Health Score</span>
                  <div className="flex items-center gap-2">
                    <span className="font-bold">{selectedSite.health}%</span>
                    <Badge variant={getStatusBadge(selectedSite.status)}>{selectedSite.status}</Badge>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Temperature</span>
                  <span className="font-bold">{selectedSite.temperature}°C</span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Active Alerts</span>
                  <Badge variant={selectedSite.alerts > 0 ? "destructive" : "default"}>{selectedSite.alerts}</Badge>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Last Update</span>
                  <span className="text-sm text-muted-foreground">{selectedSite.lastUpdate}</span>
                </div>

                <div className="pt-2">
                  <Button className="w-full" size="sm">
                    View Detailed Report
                  </Button>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card className="border-2 border-gray-800 shadow-lg">
              <CardContent className="p-6 text-center">
                <MapPin className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <div className="text-sm font-medium mb-2">Select a Site</div>
                <div className="text-xs text-muted-foreground">Click on a marker to view site details</div>
              </CardContent>
            </Card>
          )}

          {/* Site List */}
          <Card className="border-2 border-gray-800 shadow-lg">
            <CardHeader>
              <CardTitle className="font-serif text-2xl">All Sites ({filteredSites.length})</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {filteredSites.map((site) => (
                  <div
                    key={site.id}
                    className={`p-3 border rounded-lg cursor-pointer transition-colors hover:bg-gray-50 ${selectedSite?.id === site.id ? "bg-blue-50 border-blue-200" : ""
                      }`}
                    onClick={() => setSelectedSite(site)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className={`w-2 h-2 rounded-full ${getStatusColor(site.status)}`} />
                        <span className="text-sm font-medium">{site.name}</span>
                      </div>
                      <Badge variant={getStatusBadge(site.status)} className="text-xs">
                        {site.health}%
                      </Badge>
                    </div>
                    {site.alerts > 0 && (
                      <div className="text-xs text-red-600 mt-1">
                        {site.alerts} active alert{site.alerts > 1 ? "s" : ""}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
