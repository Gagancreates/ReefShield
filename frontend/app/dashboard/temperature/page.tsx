"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  AreaChart,
  Area,
  BarChart,
  Bar,
} from "recharts"
import { Thermometer, TrendingUp, TrendingDown, AlertTriangle, Download, RefreshCw } from "lucide-react"
import { useRealtimeLocations, useTemperatureAnalysis } from "@/lib/hooks/useRealtimeData"

// Dummy temperature data for 14 days
const temperatureData = [
  { date: "2024-01-01", temp: 26.2, threshold: 28.5, site: "Great Barrier Reef" },
  { date: "2024-01-02", temp: 26.8, threshold: 28.5, site: "Great Barrier Reef" },
  { date: "2024-01-03", temp: 27.1, threshold: 28.5, site: "Great Barrier Reef" },
  { date: "2024-01-04", temp: 27.5, threshold: 28.5, site: "Great Barrier Reef" },
  { date: "2024-01-05", temp: 28.2, threshold: 28.5, site: "Great Barrier Reef" },
  { date: "2024-01-06", temp: 28.9, threshold: 28.5, site: "Great Barrier Reef" },
  { date: "2024-01-07", temp: 29.1, threshold: 28.5, site: "Great Barrier Reef" },
  { date: "2024-01-08", temp: 28.7, threshold: 28.5, site: "Great Barrier Reef" },
  { date: "2024-01-09", temp: 28.3, threshold: 28.5, site: "Great Barrier Reef" },
  { date: "2024-01-10", temp: 27.9, threshold: 28.5, site: "Great Barrier Reef" },
  { date: "2024-01-11", temp: 27.4, threshold: 28.5, site: "Great Barrier Reef" },
  { date: "2024-01-12", temp: 27.0, threshold: 28.5, site: "Great Barrier Reef" },
  { date: "2024-01-13", temp: 26.8, threshold: 28.5, site: "Great Barrier Reef" },
  { date: "2024-01-14", temp: 26.5, threshold: 28.5, site: "Great Barrier Reef" },
]

// Dummy hourly temperature data for detailed analysis
const hourlyTempData = [
  { hour: "00:00", temp: 26.8 },
  { hour: "04:00", temp: 26.2 },
  { hour: "08:00", temp: 26.9 },
  { hour: "12:00", temp: 28.1 },
  { hour: "16:00", temp: 29.2 },
  { hour: "20:00", temp: 28.4 },
]

// Dummy monthly temperature comparison data
const monthlyComparisonData = [
  { month: "Oct", current: 27.2, historical: 26.8 },
  { month: "Nov", current: 27.8, historical: 27.1 },
  { month: "Dec", current: 28.4, historical: 27.6 },
  { month: "Jan", current: 28.9, historical: 28.1 },
]

const sites = [
  { id: "gbr", name: "Great Barrier Reef", avgTemp: 27.4, trend: "down", status: "normal" },
  { id: "ct", name: "Coral Triangle", avgTemp: 28.9, trend: "up", status: "warning" },
  { id: "cr", name: "Caribbean Reef", avgTemp: 26.8, trend: "stable", status: "normal" },
  { id: "rs", name: "Red Sea Coral", avgTemp: 29.2, trend: "up", status: "critical" },
]

export default function TemperaturePage() {
  // Real-time data hooks
  const { locations: realtimeLocations, loading, lastUpdated } = useRealtimeLocations()
  const { data: temperatureAnalysisData } = useTemperatureAnalysis()

  // Calculate real-time statistics
  const currentTemps = realtimeLocations.map(loc => loc.currentTemperature)
  const currentTemp = currentTemps.length > 0 ? currentTemps.reduce((a, b) => a + b) / currentTemps.length : 0
  const maxTemp = currentTemps.length > 0 ? Math.max(...currentTemps) : 0
  const minTemp = currentTemps.length > 0 ? Math.min(...currentTemps) : 0
  
  // Use real temperature analysis data
  const temperatureData = temperatureAnalysisData.map((item, index) => ({
    date: `2025-03-${String(index + 1).padStart(2, '0')}`,
    temp: item.temp,
    threshold: item.threshold,
    site: "Andaman Islands"
  }))

  const avgTemp = temperatureData.length > 0 ? 
    temperatureData.reduce((sum, data) => sum + data.temp, 0) / temperatureData.length : 0
  const tempChange = temperatureData.length >= 2 ? 
    temperatureData[temperatureData.length - 1].temp - temperatureData[temperatureData.length - 2].temp : 0

  // Convert locations to sites format
  const sites = realtimeLocations.map(loc => ({
    id: loc.id,
    name: loc.name,
    avgTemp: loc.currentTemperature,
    trend: loc.trend === 'increasing' ? 'up' : loc.trend === 'decreasing' ? 'down' : 'stable',
    status: loc.riskLevel === 'high' ? 'critical' : loc.riskLevel === 'moderate' ? 'warning' : 'normal'
  }))

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-serif text-4xl font-bold text-gray-900">Temperature Analysis</h1>
          <p className="text-muted-foreground">
            Real-time water temperature trends for Andaman Islands
            {lastUpdated && (
              <span className="ml-2 text-xs text-green-600">
                • Live (Updated {lastUpdated.toLocaleTimeString()})
              </span>
            )}
          </p>
        </div>
        <div className="flex gap-2">
          <Select defaultValue="14d">
            <SelectTrigger className="w-32 text-gray-900 border-2 border-gray-300 focus:border-blue-500">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-white border-2 border-gray-300">
              <SelectItem value="7d" className="text-gray-900 hover:bg-gray-100 focus:bg-blue-100 focus:text-blue-900">
                7 Days
              </SelectItem>
              <SelectItem value="14d" className="text-gray-900 hover:bg-gray-100 focus:bg-blue-100 focus:text-blue-900">
                14 Days
              </SelectItem>
              <SelectItem value="30d" className="text-gray-900 hover:bg-gray-100 focus:bg-blue-100 focus:text-blue-900">
                30 Days
              </SelectItem>
              <SelectItem value="90d" className="text-gray-900 hover:bg-gray-100 focus:bg-blue-100 focus:text-blue-900">
                90 Days
              </SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" size="sm">
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            {loading ? 'Updating...' : 'Live Data'}
          </Button>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="border-2 border-gray-800 shadow-lg">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-base font-medium">Current Temperature</CardTitle>
            <Thermometer className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{currentTemp.toFixed(1)}°C</div>
            <div className="flex items-center text-xs text-muted-foreground">
              {tempChange > 0 ? (
                <TrendingUp className="h-3 w-3 mr-1 text-red-500" />
              ) : (
                <TrendingDown className="h-3 w-3 mr-1 text-green-500" />
              )}
              {tempChange > 0 ? "+" : ""}
              {tempChange.toFixed(1)}°C from yesterday
            </div>
          </CardContent>
        </Card>

        <Card className="border-2 border-gray-800 shadow-lg">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-base font-medium">14-Day Average</CardTitle>
            <Thermometer className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{avgTemp.toFixed(1)}°C</div>
            <div className="text-xs text-muted-foreground">Within normal range</div>
          </CardContent>
        </Card>

        <Card className="border-2 border-gray-800 shadow-lg">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-base font-medium">Maximum</CardTitle>
            <TrendingUp className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{maxTemp.toFixed(1)}°C</div>
            <div className="text-xs text-muted-foreground">Recorded on Jan 7th</div>
          </CardContent>
        </Card>

        <Card className="border-2 border-gray-800 shadow-lg">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-base font-medium">Minimum</CardTitle>
            <TrendingDown className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{minTemp.toFixed(1)}°C</div>
            <div className="text-xs text-muted-foreground">Recorded on Jan 1st</div>
          </CardContent>
        </Card>
      </div>

      {/* Temperature Chart */}
      <Card className="border-2 border-gray-800 shadow-lg">
        <CardHeader>
          <CardTitle className="font-serif text-2xl">14-Day Temperature Trend</CardTitle>
          <CardDescription>Water temperature readings with bleaching threshold indicator</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={temperatureData}>
                <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                <XAxis
                  dataKey="date"
                  tickFormatter={(value) =>
                    new Date(value).toLocaleDateString("en-US", { month: "short", day: "numeric" })
                  }
                  className="text-xs"
                />
                <YAxis
                  domain={["dataMin - 1", "dataMax + 1"]}
                  tickFormatter={(value) => `${value}°C`}
                  className="text-xs"
                />
                <Tooltip
                  labelFormatter={(value) =>
                    new Date(value).toLocaleDateString("en-US", {
                      weekday: "long",
                      year: "numeric",
                      month: "long",
                      day: "numeric",
                    })
                  }
                  formatter={(value: number) => [`${value.toFixed(1)}°C`, "Temperature"]}
                />
                <ReferenceLine
                  y={28.5}
                  stroke="#ef4444"
                  strokeDasharray="5 5"
                  label={{ value: "Bleaching Threshold", position: "top" }}
                />
                <Line
                  type="monotone"
                  dataKey="temp"
                  stroke="#2563eb"
                  strokeWidth={3}
                  dot={{ fill: "#2563eb", strokeWidth: 2, r: 4 }}
                  activeDot={{ r: 6, stroke: "#2563eb", strokeWidth: 2 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="border-2 border-gray-800 shadow-lg">
          <CardHeader>
            <CardTitle className="font-serif text-2xl">Today's Hourly Temperature</CardTitle>
            <CardDescription>Temperature variations throughout the day</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={hourlyTempData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="hour" />
                  <YAxis tickFormatter={(value) => `${value}°C`} />
                  <Tooltip formatter={(value: number) => [`${value.toFixed(1)}°C`, "Temperature"]} />
                  <Area type="monotone" dataKey="temp" stroke="#10b981" fill="#10b981" fillOpacity={0.3} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card className="border-2 border-gray-800 shadow-lg">
          <CardHeader>
            <CardTitle className="font-serif text-2xl">Monthly Temperature Comparison</CardTitle>
            <CardDescription>Current vs historical monthly averages</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={monthlyComparisonData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis tickFormatter={(value) => `${value}°C`} />
                  <Tooltip formatter={(value: number) => [`${value.toFixed(1)}°C`, ""]} />
                  <Bar dataKey="current" fill="#3b82f6" name="Current Year" />
                  <Bar dataKey="historical" fill="#94a3b8" name="Historical Average" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Site Comparison */}
      <Card className="border-2 border-gray-800 shadow-lg">
        <CardHeader>
          <CardTitle className="font-serif text-2xl">Site Temperature Comparison</CardTitle>
          <CardDescription>Current temperature status across all monitored reef sites</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {sites.map((site) => (
              <div key={site.id} className="flex items-center justify-between p-4 border-2 border-gray-700 rounded-lg">
                <div className="flex items-center gap-4">
                  <div
                    className={`w-3 h-3 rounded-full ${
                      site.status === "critical"
                        ? "bg-red-500"
                        : site.status === "warning"
                          ? "bg-orange-500"
                          : "bg-green-500"
                    }`}
                  />
                  <div>
                    <div className="font-medium">{site.name}</div>
                    <div className="text-sm text-muted-foreground">Average: {site.avgTemp.toFixed(1)}°C</div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1">
                    {site.trend === "up" && <TrendingUp className="h-4 w-4 text-red-500" />}
                    {site.trend === "down" && <TrendingDown className="h-4 w-4 text-green-500" />}
                    {site.trend === "stable" && <div className="w-4 h-0.5 bg-gray-400" />}
                  </div>
                  <Badge
                    variant={
                      site.status === "critical" ? "destructive" : site.status === "warning" ? "secondary" : "default"
                    }
                  >
                    {site.status}
                  </Badge>
                  {site.status === "critical" && <AlertTriangle className="h-4 w-4 text-red-500" />}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
