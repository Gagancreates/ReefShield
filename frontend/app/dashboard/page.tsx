"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import { Line, LineChart, XAxis, YAxis, CartesianGrid, ResponsiveContainer, DotProps } from "recharts"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { useState } from "react"
import { ZoomIn, ZoomOut, RotateCcw, Layers, RefreshCw } from "lucide-react"
import { GlobalMap } from "@/components/global-map"
import { Map } from "@/components/map"
import { ChlorophyllChart } from "@/components/chlorophyll-chart"
import { useRealtimeLocations, useTemperatureAnalysis, useRealtimeAlerts, useSystemStatus } from "@/lib/hooks/useRealtimeData"
import jsPDF from "jspdf";
// If not installed, also install html2canvas: npm install html2canvas
import html2canvas from "html2canvas";
import { useRef } from "react";

// Fallback temperature data for 14 days - shows immediately when backend unavailable
const fallbackTemperatureData = [
  { day: "Day 1", temp: 28.2, threshold: 29.0, source: "Observed" },
  { day: "Day 2", temp: 28.8, threshold: 29.0, source: "Observed" },
  { day: "Day 3", temp: 29.1, threshold: 29.0, source: "Observed" },
  { day: "Day 4", temp: 28.5, threshold: 29.0, source: "Observed" },
  { day: "Day 5", temp: 28.2, threshold: 29.0, source: "Observed" },
  { day: "Day 6", temp: 28.9, threshold: 29.0, source: "Observed" },
  { day: "Day 7", temp: 29.3, threshold: 29.0, source: "Observed" },
  { day: "Day 8", temp: 28.7, threshold: 29.0, source: "Forecast" },
  { day: "Day 9", temp: 28.3, threshold: 29.0, source: "Forecast" },
  { day: "Day 10", temp: 27.9, threshold: 29.0, source: "Forecast" },
  { day: "Day 11", temp: 28.4, threshold: 29.0, source: "Forecast" },
  { day: "Day 12", temp: 28.0, threshold: 29.0, source: "Forecast" },
  { day: "Day 13", temp: 28.8, threshold: 29.0, source: "Forecast" },
  { day: "Day 14", temp: 28.5, threshold: 29.0, source: "Forecast" },
]

// Custom dot for highlighting today's temperature
interface CustomDotProps extends DotProps {
  index?: number;           // Recharts gives us this automatically
  highlightIndex: number;   // we’ll pass this manually
}

const HighlightDot = ({ cx, cy, index, highlightIndex }: CustomDotProps) => {
  if (cx == null || cy == null) return null; // safety check

  if (index === highlightIndex) {
    // highlighted dot (for the 7th day)
    return (
      <circle
        cx={cx}
        cy={cy}
        r={8}
        fill="#f59e42"
        stroke="#d97706"
        strokeWidth={3}
      />
    );
  }

  // normal small dot
  return (
    <circle
      cx={cx}
      cy={cy}
      r={3}
      fill="var(--color-temp)"
      strokeWidth={2}
    />
  );
};


export default function DashboardPage() {
  const [selectedLocation, setSelectedLocation] = useState<string | null>(null)
  const dashboardRef = useRef<HTMLDivElement>(null);

  // Real-time data hooks
  const { locations: realtimeLocations, loading: locationsLoading, lastUpdated, forceRefresh: refreshLocations } = useRealtimeLocations()
  const { data: temperatureAnalysisData, forceRefresh: refreshTempAnalysis } = useTemperatureAnalysis()
  const { alerts: realtimeAlerts } = useRealtimeAlerts()
  const { status: systemStatus } = useSystemStatus()

  // Use real temperature data if available, otherwise fallback
  const temperatureData = temperatureAnalysisData.length > 0 ? temperatureAnalysisData : fallbackTemperatureData

  // Convert real-time data to component format
  const locations = realtimeLocations.map(loc => ({
    id: loc.id,
    name: loc.name,
    temperature: loc.currentTemperature,
    coordinates: loc.coordinates,
    temperatureData: loc.temperatureHistory.slice(-7).map((reading, index) => ({
      day: `Day ${index + 1}`,
      temp: Number(reading.temperature.toFixed(1))
    })),
    dhwAnalysis: {
      current: loc.dhw,
      trend: loc.trend,
      riskLevel: loc.riskLevel,
    },
    chlorophyll: loc.chlorophyll,
  }))

  const reefSites = realtimeLocations.map((loc, index) => ({
    id: index + 1,
    name: loc.name,
    health: loc.riskLevel === 'low' ? 90 : loc.riskLevel === 'moderate' ? 75 : 60,
    status: loc.riskLevel === 'low' ? 'healthy' as const : loc.riskLevel === 'moderate' ? 'at-risk' as const : 'critical' as const,
    temperature: loc.currentTemperature,
    alerts: loc.riskLevel === 'high' ? 3 : loc.riskLevel === 'moderate' ? 1 : 0,
    coordinates: [loc.coordinates.lat, loc.coordinates.lng] as [number, number],
  }))

  const handleRefreshAll = async () => {
    await Promise.all([refreshLocations(), refreshTempAnalysis()])
  }

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

  const handleGenerateReport = async () => {
    if (!dashboardRef.current) return;
    const input = dashboardRef.current;
    // Use html2canvas to render the dashboard to a canvas
    const canvas = await html2canvas(input, { scale: 2 });
    const imgData = canvas.toDataURL("image/png");
    const pdf = new jsPDF({ orientation: "landscape", unit: "pt", format: "a4" });
    const pdfWidth = pdf.internal.pageSize.getWidth();
    const pdfHeight = pdf.internal.pageSize.getHeight();
    // Fit image to PDF page
    pdf.addImage(imgData, "PNG", 0, 0, pdfWidth, pdfHeight);
    pdf.save("reef-dashboard-report.pdf");
  };

  return (
    <div className="space-y-3">
      <div ref={dashboardRef}>
        <div className="grid gap-3 lg:grid-cols-5">
          <div className="lg:col-span-3 space-y-3">
            <Card className="bg-gradient-to-br from-blue-50 to-cyan-50 border-2 border-gray-800 shadow-lg">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="font-serif text-2xl text-blue-900">
                      Andaman Islands Reef Monitoring
                    </CardTitle>
                    <CardDescription>
                      Real-time status of coral reef sites in Andaman Islands
                      {lastUpdated && (
                        <span className="ml-2 text-xs text-green-600">
                          Updated {lastUpdated.toLocaleTimeString()}
                        </span>
                      )}
                    </CardDescription>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" className="bg-white">
                      <Layers className="h-4 w-4 mr-2" />
                      Layers
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="space-y-3">
                  <div className="relative h-80 rounded-lg overflow-hidden">
                    <GlobalMap reefSites={reefSites} className="rounded-lg" />
                  </div>

                  {/* Site Status Legend - Now positioned below the map */}
                  <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-200">
                    <div className="text-sm font-semibold mb-2 text-gray-800">Site Status</div>
                    <div className="flex items-center gap-6">
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

            <Card className="bg-gradient-to-br from-orange-50 to-red-50 border-2 border-gray-800 shadow-lg">
              <CardHeader className="pb-2">
                <CardTitle className="font-serif text-2xl text-orange-900">
                  14 Day Temperature Analysis
                </CardTitle>
                <CardDescription>Recent temperature trends with bleaching threshold monitoring</CardDescription>
              </CardHeader>
              <CardContent className="pt-0">
                <ChartContainer
                  config={{
                    temp: {
                      label: "Temperature (°C)",
                      color: "hsl(var(--chart-1))",
                    },
                    threshold: {
                      label: "Bleaching Threshold",
                      color: "hsl(var(--chart-5))",
                    },
                  }}
                  className="h-64"
                >
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={temperatureData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="day" />
                      <YAxis domain={[26, 31]} />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Line 
                        type="monotone" 
                        dataKey="temp" 
                        stroke="var(--color-temp)" 
                        strokeWidth={2}
                        dot={(dotProps) => (
                          <HighlightDot {...dotProps} highlightIndex={6} /> // 7th day = index 6 (0-based)
                        )}
                      />
                      <Line
                        type="monotone"
                        dataKey="threshold"
                        stroke="var(--color-threshold)"
                        strokeWidth={2}
                        strokeDasharray="5 5"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </ChartContainer>
              </CardContent>
            </Card>

            <div className="grid gap-3 md:grid-cols-2">
              <Card className="bg-gradient-to-br from-emerald-50 to-green-50 border-2 border-gray-800 shadow-lg">
                <CardHeader className="pb-2">
                  <CardTitle className="font-serif text-xl text-emerald-900">
                    System Status
                  </CardTitle>
                </CardHeader>
                <CardContent className="pt-0 space-y-2">
                  <div className="flex items-center justify-between p-2 bg-white rounded-lg border-2 border-gray-700">
                    <span className="text-sm font-medium">Satellite Data Feed</span>
                    <Badge className="bg-emerald-100 text-emerald-800 border-emerald-200">
                      {systemStatus.satelliteDataFeed}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-white rounded-lg border-2 border-gray-700">
                    <span className="text-sm font-medium">AI Processing Engine</span>
                    <Badge className="bg-emerald-100 text-emerald-800 border-emerald-200">
                      {systemStatus.aiProcessingEngine}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-white rounded-lg border-2 border-gray-700">
                    <span className="text-sm font-medium">Alert System</span>
                    <Badge className="bg-emerald-100 text-emerald-800 border-emerald-200">
                      {systemStatus.alertSystem}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-white rounded-lg border-2 border-gray-700">
                    <span className="text-sm font-medium">Data Sync</span>
                    <Badge className={`${systemStatus.dataSync === 'Syncing' ? 'bg-amber-100 text-amber-800 border-amber-200' : 'bg-emerald-100 text-emerald-800 border-emerald-200'}`}>
                      {systemStatus.dataSync}
                    </Badge>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-purple-50 to-indigo-50 border-2 border-gray-800 shadow-lg">
                <CardHeader className="pb-2">
                  <CardTitle className="font-serif text-xl text-purple-900">Quick Actions</CardTitle>
                </CardHeader>
                <CardContent className="pt-0 space-y-2">
                  <Button className="w-full justify-start bg-white text-gray-900 border-2 border-gray-700 hover:bg-purple-50 transition-colors" onClick={handleGenerateReport}>
                    <div className="text-left">
                      <div className="font-medium text-sm">Generate Report</div>
                      <div className="text-xs text-muted-foreground">Create weekly reef health summary</div>
                    </div>
                  </Button>
                  <Button className="w-full justify-start bg-white text-gray-900 border-2 border-gray-700 hover:bg-purple-50 transition-colors">
                    <div className="text-left">
                      <div className="font-medium text-sm">Configure Alerts</div>
                      <div className="text-xs text-muted-foreground">Adjust monitoring thresholds</div>
                    </div>
                  </Button>
                  <Button className="w-full justify-start bg-white text-gray-900 border-2 border-gray-700 hover:bg-purple-50 transition-colors" onClick={handleGenerateReport}>
                    <div className="text-left">
                      <div className="font-medium text-sm">Export Data</div>
                      <div className="text-xs text-muted-foreground">Download monitoring datasets</div>
                    </div>
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>

          <div className="lg:col-span-2 space-y-3">
            <Card className="bg-gradient-to-br from-blue-50 to-cyan-50 border-2 border-gray-800 shadow-lg">
              <CardHeader className="pb-2">
                <CardTitle className="font-serif text-xl text-blue-900">
                  Monitoring Locations
                </CardTitle>
                <CardDescription>Current temperatures at key reef sites</CardDescription>
              </CardHeader>
              <CardContent className="pt-0 space-y-2">
                {locations.map((location) => (
                  <Dialog key={location.id}>
                    <DialogTrigger asChild>
                      <Card className="cursor-pointer hover:shadow-md transition-shadow border-2 border-gray-700 bg-white">
                        <CardContent className="p-3">
                          <div className="flex items-center justify-between">
                            <div>
                              <div className="font-medium text-sm text-gray-900">{location.name}</div>
                              <div className="text-xs text-gray-600">
                                Lat: {location.coordinates.lat}, Lng: {location.coordinates.lng}
                              </div>
                            </div>
                            <div className="text-right">
                              <div className="text-lg font-bold text-blue-600">{location.temperature}°C</div>
                              <Badge
                                variant={
                                  location.dhwAnalysis.riskLevel === "high"
                                    ? "destructive"
                                    : location.dhwAnalysis.riskLevel === "moderate"
                                      ? "default"
                                      : "secondary"
                                }
                                className="text-xs"
                              >
                                {location.dhwAnalysis.riskLevel}
                              </Badge>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </DialogTrigger>
                    <DialogContent className="w-[85vw] !max-w-none max-h-[90vh] overflow-y-auto sm:!max-w-none" showCloseButton={true}>
                      <DialogHeader>
                        <DialogTitle className="text-2xl font-semibold">{location.name}</DialogTitle>
                        <div className="text-sm text-gray-600">
                          Coordinates: {location.coordinates.lat.toFixed(6)}°N, {location.coordinates.lng.toFixed(6)}°E
                        </div>
                      </DialogHeader>
                      <div className="grid gap-4 lg:grid-cols-3">
                        {/* Map View */}
                        <div className="lg:col-span-2">
                          <Card className="border-2 border-gray-800 shadow-lg">
                            <CardHeader className="pb-2">
                              <CardTitle className="text-lg">Location Map</CardTitle>
                            </CardHeader>
                            <CardContent>
                              <div className="h-64 rounded-lg overflow-hidden">
                                <Map
                                  center={[location.coordinates.lat, location.coordinates.lng]}
                                  zoom={12}
                                  markers={[
                                    {
                                      position: [location.coordinates.lat, location.coordinates.lng],
                                      popup: `
                                        <div class="p-2">
                                          <h3 class="font-semibold text-sm">${location.name}</h3>
                                          <p class="text-xs text-gray-600">Lat: ${location.coordinates.lat.toFixed(4)}°, Lng: ${location.coordinates.lng.toFixed(4)}°</p>
                                          <p class="text-xs text-gray-600">Temperature: ${location.temperature}°C</p>
                                          <p class="text-xs text-gray-600">DHW: ${location.dhwAnalysis.current}</p>
                                          <p class="text-xs text-gray-600">Risk: ${location.dhwAnalysis.riskLevel}</p>
                                          ${location.chlorophyll ? `<p class="text-xs text-gray-600">Chlorophyll: ${location.chlorophyll.value.toFixed(3)} mg/m³</p>` : ''}
                                        </div>  
                                      `,
                                      status: location.dhwAnalysis.riskLevel === "high" ? "critical" : location.dhwAnalysis.riskLevel === "moderate" ? "at-risk" : "healthy"
                                    }
                                  ]}
                                  className="rounded-lg"
                                />
                              </div>
                            </CardContent>
                          </Card>

                          {/* Temperature Chart */}
                          <Card className="border-2 border-gray-800 shadow-lg mt-4">
                            <CardHeader className="pb-2">
                              <CardTitle className="text-lg">7-Day Temperature Trend</CardTitle>
                            </CardHeader>
                            <CardContent>
                              <ChartContainer
                                config={{
                                  temp: {
                                    label: "Temperature (°C)",
                                    color: "hsl(var(--chart-1))",
                                  },
                                }}
                                className="h-48"
                              >
                                <ResponsiveContainer width="100%" height="100%">
                                  <LineChart data={location.temperatureData}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="day" />
                                    <YAxis domain={[26, 30]} />
                                    <ChartTooltip content={<ChartTooltipContent />} />
                                    <Line type="monotone" dataKey="temp" stroke="var(--color-temp)" strokeWidth={2} />
                                  </LineChart>
                                </ResponsiveContainer>
                              </ChartContainer>
                            </CardContent>
                          </Card>
                        </div>

                        {/* DHW Analysis and Chlorophyll */}
                        <div className="space-y-4">
                          <Card className="border-2 border-gray-800 shadow-lg">
                            <CardHeader className="pb-2">
                              <CardTitle className="text-lg">DHW Analysis</CardTitle>
                              <CardDescription>Degree Heating Weeks Assessment</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                              <div className="text-center">
                                <div className="text-3xl font-bold text-blue-600">{location.dhwAnalysis.current}</div>
                                <div className="text-sm text-gray-600">Current DHW</div>
                              </div>

                              <div className="space-y-3">
                                <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                                  <span className="text-sm font-medium">Trend</span>
                                  <Badge
                                    variant={location.dhwAnalysis.trend === "increasing" ? "destructive" : "secondary"}
                                  >
                                    {location.dhwAnalysis.trend}
                                  </Badge>
                                </div>

                                <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                                  <span className="text-sm font-medium">Risk Level</span>
                                  <Badge
                                    variant={
                                      location.dhwAnalysis.riskLevel === "high"
                                        ? "destructive"
                                        : location.dhwAnalysis.riskLevel === "moderate"
                                          ? "default"
                                          : "secondary"
                                    }
                                  >
                                    {location.dhwAnalysis.riskLevel}
                                  </Badge>
                                </div>

                                <div className="p-2 bg-gray-50 rounded-lg">
                                  <div className="text-sm font-medium mb-1">Temperature</div>
                                  <div className="text-lg font-bold text-blue-600">{location.temperature}°C</div>
                                </div>

                                <div className="p-2 bg-gray-50 rounded-lg">
                                  <div className="text-sm font-medium mb-1">Bleaching Risk</div>
                                  <Progress value={location.dhwAnalysis.current * 20} className="h-2" />
                                  <div className="text-xs text-gray-600 mt-1">
                                    {location.dhwAnalysis.current > 4
                                      ? "High Risk"
                                      : location.dhwAnalysis.current > 2
                                        ? "Moderate Risk"
                                        : "Low Risk"}
                                  </div>
                                </div>
                              </div>
                            </CardContent>
                          </Card>

                          {/* Chlorophyll Analysis */}
                          {location.chlorophyll && (
                            <Card className="border-2 border-gray-800 shadow-lg">
                              <CardContent className="p-4">
                                <ChlorophyllChart
                                  value={location.chlorophyll.value}
                                  threshold={location.chlorophyll.threshold}
                                  riskLevel={location.chlorophyll.riskLevel}
                                />
                              </CardContent>
                            </Card>
                          )}
                        </div>
                      </div>
                    </DialogContent>
                  </Dialog>
                ))}
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-red-50 to-orange-50 border-2 border-gray-800 shadow-lg">
              <CardHeader className="pb-2">
                <CardTitle className="font-serif text-xl text-red-900">
                  Recent Alerts
                </CardTitle>
                <CardDescription>Latest monitoring alerts and warnings</CardDescription>
              </CardHeader>
              <CardContent className="pt-0 space-y-3">
                {realtimeAlerts.length > 0 ? (
                  realtimeAlerts.map((alert) => (
                    <div
                      key={alert.id}
                      className={`border-l-4 pl-4 py-3 bg-white rounded-lg border-2 border-gray-700 ${alert.severity === 'Critical' ? 'border-red-500' :
                        alert.severity === 'Warning' ? 'border-amber-500' :
                          'border-blue-500'
                        }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium text-gray-900">{alert.title}</h4>
                        <Badge variant={
                          alert.severity === 'Critical' ? 'destructive' :
                            alert.severity === 'Warning' ? 'default' :
                              'secondary'
                        }>
                          {alert.severity}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600 mb-1">{alert.location}</p>
                      <p className="text-sm text-gray-500 mb-2">{alert.description}</p>
                      <p className="text-xs text-gray-400">{alert.time}</p>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <p className="text-sm">No active alerts</p>
                    <p className="text-xs">All reef sites are operating normally</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}