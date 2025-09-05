"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { MapPin, Search, Filter, Layers, ZoomIn, ZoomOut, RotateCcw } from "lucide-react"

// Dummy reef location data
const reefSites = [
  {
    id: 1,
    name: "Great Barrier Reef - North",
    lat: -16.2839,
    lng: 145.7781,
    health: 87,
    status: "healthy",
    temperature: 26.8,
    alerts: 0,
    lastUpdate: "2 hours ago",
  },
  {
    id: 2,
    name: "Great Barrier Reef - Central",
    lat: -20.3484,
    lng: 149.7781,
    health: 72,
    status: "at-risk",
    temperature: 28.9,
    alerts: 2,
    lastUpdate: "1 hour ago",
  },
  {
    id: 3,
    name: "Coral Triangle - Indonesia",
    lat: -8.3405,
    lng: 115.092,
    health: 91,
    status: "healthy",
    temperature: 27.2,
    alerts: 0,
    lastUpdate: "30 minutes ago",
  },
  {
    id: 4,
    name: "Caribbean Reef - Belize",
    lat: 17.1899,
    lng: -88.4976,
    health: 65,
    status: "critical",
    temperature: 29.5,
    alerts: 3,
    lastUpdate: "15 minutes ago",
  },
  {
    id: 5,
    name: "Red Sea Coral - Egypt",
    lat: 27.2946,
    lng: 33.8407,
    health: 78,
    status: "at-risk",
    temperature: 28.1,
    alerts: 1,
    lastUpdate: "45 minutes ago",
  },
  {
    id: 6,
    name: "Maldives Reef System",
    lat: 3.2028,
    lng: 73.2207,
    health: 94,
    status: "healthy",
    temperature: 26.5,
    alerts: 0,
    lastUpdate: "1 hour ago",
  },
]

export default function MapPage() {
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
        return "bg-green-500"
      case "at-risk":
        return "bg-yellow-500"
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
          <p className="text-muted-foreground">Interactive monitoring of global coral reef sites</p>
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
          <Card className="border-2 border-gray-800 shadow-lg">
            <CardHeader>
              <CardTitle className="font-serif text-2xl">Global Reef Monitoring</CardTitle>
              <CardDescription>Real-time status of monitored coral reef sites worldwide</CardDescription>
            </CardHeader>
            <CardContent>
              {/* Placeholder for interactive map */}
              <div className="relative h-96 bg-gradient-to-br from-blue-100 to-blue-200 rounded-lg overflow-hidden">
                {/* Map controls */}
                <div className="absolute top-4 right-4 flex flex-col gap-2 z-10">
                  <Button size="sm" variant="outline" className="bg-white">
                    <ZoomIn className="h-4 w-4" />
                  </Button>
                  <Button size="sm" variant="outline" className="bg-white">
                    <ZoomOut className="h-4 w-4" />
                  </Button>
                  <Button size="sm" variant="outline" className="bg-white">
                    <RotateCcw className="h-4 w-4" />
                  </Button>
                </div>

                {/* Simulated world map with reef markers */}
                <div className="absolute inset-0 bg-gradient-to-b from-blue-300 to-blue-400">
                  {/* Continent shapes (simplified) */}
                  <div className="absolute top-16 left-20 w-32 h-20 bg-green-200 rounded-lg opacity-60"></div>
                  <div className="absolute top-24 right-16 w-28 h-24 bg-green-200 rounded-lg opacity-60"></div>
                  <div className="absolute bottom-20 left-32 w-24 h-16 bg-green-200 rounded-lg opacity-60"></div>

                  {/* Reef site markers */}
                  {filteredSites.map((site, index) => (
                    <div
                      key={site.id}
                      className={`absolute w-4 h-4 rounded-full border-2 border-white cursor-pointer transform -translate-x-1/2 -translate-y-1/2 ${getStatusColor(site.status)} hover:scale-125 transition-transform`}
                      style={{
                        left: `${20 + index * 15}%`,
                        top: `${30 + index * 8}%`,
                      }}
                      onClick={() => setSelectedSite(site)}
                      title={site.name}
                    />
                  ))}
                </div>

                {/* Map legend */}
                <div className="absolute bottom-4 left-4 bg-white p-3 rounded-lg shadow-lg">
                  <div className="text-sm font-medium mb-2">Site Status</div>
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-green-500"></div>
                      <span className="text-xs">Healthy</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                      <span className="text-xs">At Risk</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-red-500"></div>
                      <span className="text-xs">Critical</span>
                    </div>
                  </div>
                </div>

                {/* Note about interactive map */}
                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center">
                  <div className="bg-white/90 p-4 rounded-lg shadow-lg">
                    <MapPin className="h-8 w-8 mx-auto mb-2 text-blue-600" />
                    <div className="text-sm font-medium">Interactive Map Placeholder</div>
                    <div className="text-xs text-muted-foreground">Production version would use Leaflet or Mapbox</div>
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
                    className={`p-3 border rounded-lg cursor-pointer transition-colors hover:bg-gray-50 ${
                      selectedSite?.id === site.id ? "bg-blue-50 border-blue-200" : ""
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
