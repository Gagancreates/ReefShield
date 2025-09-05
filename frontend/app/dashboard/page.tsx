"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import { Line, LineChart, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from "recharts"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { useState } from "react"
import { ZoomIn, ZoomOut, RotateCcw, Layers } from "lucide-react"
import { GlobalMap } from "@/components/global-map"
import { Map } from "@/components/map"

export default function DashboardPage() {
  const [selectedLocation, setSelectedLocation] = useState<string | null>(null)

  const locations = [
    {
      id: "north-andaman",
      name: "North Andaman",
      temperature: 28.5,
      coordinates: { lat: 13.2389, lng: 93.0317 },
      temperatureData: [
        { day: "Day 1", temp: 27.8 },
        { day: "Day 2", temp: 28.1 },
        { day: "Day 3", temp: 28.3 },
        { day: "Day 4", temp: 28.5 },
        { day: "Day 5", temp: 28.7 },
        { day: "Day 6", temp: 28.9 },
        { day: "Day 7", temp: 28.5 },
      ],
      dhwAnalysis: {
        current: 2.3,
        trend: "increasing",
        riskLevel: "moderate",
      },
    },
    {
      id: "neel-islands",
      name: "Neel Islands",
      temperature: 27.9,
      coordinates: { lat: 11.8333, lng: 93.0333 },
      temperatureData: [
        { day: "Day 1", temp: 27.2 },
        { day: "Day 2", temp: 27.5 },
        { day: "Day 3", temp: 27.8 },
        { day: "Day 4", temp: 27.9 },
        { day: "Day 5", temp: 28.1 },
        { day: "Day 6", temp: 28.0 },
        { day: "Day 7", temp: 27.9 },
      ],
      dhwAnalysis: {
        current: 1.8,
        trend: "stable",
        riskLevel: "low",
      },
    },
    {
      id: "mahatma-gandhi",
      name: "Mahatma Gandhi Marine National Park",
      temperature: 29.2,
      coordinates: { lat: 11.5833, lng: 92.6167 },
      temperatureData: [
        { day: "Day 1", temp: 28.8 },
        { day: "Day 2", temp: 29.0 },
        { day: "Day 3", temp: 29.1 },
        { day: "Day 4", temp: 29.2 },
        { day: "Day 5", temp: 29.4 },
        { day: "Day 6", temp: 29.3 },
        { day: "Day 7", temp: 29.2 },
      ],
      dhwAnalysis: {
        current: 3.1,
        trend: "increasing",
        riskLevel: "high",
      },
    },
    {
      id: "havelock",
      name: "Havelock",
      temperature: 28.1,
      coordinates: { lat: 12.0167, lng: 92.9833 },
      temperatureData: [
        { day: "Day 1", temp: 27.6 },
        { day: "Day 2", temp: 27.8 },
        { day: "Day 3", temp: 28.0 },
        { day: "Day 4", temp: 28.1 },
        { day: "Day 5", temp: 28.2 },
        { day: "Day 6", temp: 28.0 },
        { day: "Day 7", temp: 28.1 },
      ],
      dhwAnalysis: {
        current: 2.0,
        trend: "stable",
        riskLevel: "moderate",
      },
    },
  ]

  const temperatureData = [
    { day: "Day 1", temp: 26.8, threshold: 29.0 },
    { day: "Day 2", temp: 27.1, threshold: 29.0 },
    { day: "Day 3", temp: 27.5, threshold: 29.0 },
    { day: "Day 4", temp: 28.2, threshold: 29.0 },
    { day: "Day 5", temp: 28.9, threshold: 29.0 },
    { day: "Day 6", temp: 29.3, threshold: 29.0 },
    { day: "Day 7", temp: 29.1, threshold: 29.0 },
    { day: "Day 8", temp: 28.7, threshold: 29.0 },
    { day: "Day 9", temp: 28.4, threshold: 29.0 },
    { day: "Day 10", temp: 27.9, threshold: 29.0 },
    { day: "Day 11", temp: 27.6, threshold: 29.0 },
    { day: "Day 12", temp: 27.3, threshold: 29.0 },
    { day: "Day 13", temp: 27.8, threshold: 29.0 },
    { day: "Day 14", temp: 28.1, threshold: 29.0 },
  ]

  const reefSites = [
    { id: 1, name: "North Andaman", health: 87, status: "at-risk" as const, temperature: 28.5, alerts: 1, coordinates: [13.2500, 92.9167] as [number, number] },
    { id: 2, name: "Neel Islands", health: 92, status: "healthy" as const, temperature: 27.9, alerts: 0, coordinates: [11.832919, 93.052612] as [number, number] },
    { id: 3, name: "Mahatma Gandhi Marine National Park", health: 65, status: "critical" as const, temperature: 29.2, alerts: 3, coordinates: [11.5690, 92.6542] as [number, number] },
    { id: 4, name: "Havelock", health: 78, status: "at-risk" as const, temperature: 28.1, alerts: 1, coordinates: [11.960000, 93.000000] as [number, number] },
  ]

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

  return (
    <div className="space-y-3">
      <div className="grid gap-3 lg:grid-cols-5">
        <div className="lg:col-span-3 space-y-3">
          <Card className="bg-gradient-to-br from-blue-50 to-cyan-50 border-2 border-gray-800 shadow-lg">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="font-serif text-2xl text-blue-900">Global Reef Monitoring</CardTitle>
                  <CardDescription>Real-time status of monitored coral reef sites worldwide</CardDescription>
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
              <div className="relative h-80 rounded-lg overflow-hidden">
                <GlobalMap reefSites={reefSites} className="rounded-lg" />

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

          <Card className="bg-gradient-to-br from-orange-50 to-red-50 border-2 border-gray-800 shadow-lg">
            <CardHeader className="pb-2">
              <CardTitle className="font-serif text-2xl text-orange-900">14 Day Temperature Analysis</CardTitle>
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
                    <YAxis domain={[26, 30]} />
                    <ChartTooltip content={<ChartTooltipContent />} />
                    <Line type="monotone" dataKey="temp" stroke="var(--color-temp)" strokeWidth={2} />
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
                <CardTitle className="font-serif text-xl text-emerald-900">System Status</CardTitle>
              </CardHeader>
              <CardContent className="pt-0 space-y-2">
                <div className="flex items-center justify-between p-2 bg-white rounded-lg border-2 border-gray-700">
                  <span className="text-sm font-medium">Satellite Data Feed</span>
                  <Badge className="bg-emerald-100 text-emerald-800 border-emerald-200">Online</Badge>
                </div>
                <div className="flex items-center justify-between p-2 bg-white rounded-lg border-2 border-gray-700">
                  <span className="text-sm font-medium">AI Processing Engine</span>
                  <Badge className="bg-emerald-100 text-emerald-800 border-emerald-200">Active</Badge>
                </div>
                <div className="flex items-center justify-between p-2 bg-white rounded-lg border-2 border-gray-700">
                  <span className="text-sm font-medium">Alert System</span>
                  <Badge className="bg-emerald-100 text-emerald-800 border-emerald-200">Operational</Badge>
                </div>
                <div className="flex items-center justify-between p-2 bg-white rounded-lg border-2 border-gray-700">
                  <span className="text-sm font-medium">Data Sync</span>
                  <Badge className="bg-amber-100 text-amber-800 border-amber-200">Syncing</Badge>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-purple-50 to-indigo-50 border-2 border-gray-800 shadow-lg">
              <CardHeader className="pb-2">
                <CardTitle className="font-serif text-xl text-purple-900">Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="pt-0 space-y-2">
                <Button className="w-full justify-start bg-white text-gray-900 border-2 border-gray-700 hover:bg-purple-50 transition-colors">
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
                <Button className="w-full justify-start bg-white text-gray-900 border-2 border-gray-700 hover:bg-purple-50 transition-colors">
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
              <CardTitle className="font-serif text-xl text-blue-900">Monitoring Locations</CardTitle>
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
                                        <p class="text-xs text-gray-600">Temperature: ${location.temperature}°C</p>
                                        <p class="text-xs text-gray-600">DHW: ${location.dhwAnalysis.current}</p>
                                        <p class="text-xs text-gray-600">Risk: ${location.dhwAnalysis.riskLevel}</p>
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

                      {/* DHW Analysis */}
                      <div>
                        <Card className="border-2 border-gray-800 shadow-lg h-full">
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
                      </div>
                    </div>
                  </DialogContent>
                </Dialog>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
