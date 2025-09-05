"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"
import {
  AlertTriangle,
  Thermometer,
  Droplets,
  Fish,
  Search,
  Bell,
  Clock,
  MapPin,
  Settings,
  CheckCircle,
  XCircle,
} from "lucide-react"

// Dummy alerts data
const alerts = [
  {
    id: 1,
    type: "temperature",
    severity: "high",
    title: "Critical Temperature Spike",
    description: "Water temperature exceeded 29°C threshold at Great Barrier Reef - Sector 7",
    location: "Great Barrier Reef - Sector 7",
    timestamp: "2024-01-15T14:30:00Z",
    status: "active",
    value: "29.2°C",
    threshold: "28.5°C",
    impact: "High risk of coral bleaching",
  },
  {
    id: 2,
    type: "bleaching",
    severity: "medium",
    title: "Bleaching Risk Detected",
    description: "Elevated stress indicators and temperature patterns suggest bleaching risk",
    location: "Coral Triangle - Site B12",
    timestamp: "2024-01-15T08:15:00Z",
    status: "active",
    value: "Moderate Risk",
    threshold: "Low Risk",
    impact: "Potential coral stress",
  },
  {
    id: 3,
    type: "water_quality",
    severity: "medium",
    title: "pH Level Alert",
    description: "pH levels have dropped below optimal range for coral health",
    location: "Caribbean Reef - Zone 3",
    timestamp: "2024-01-14T16:45:00Z",
    status: "acknowledged",
    value: "7.9",
    threshold: "8.1-8.4",
    impact: "Acidification stress",
  },
  {
    id: 4,
    type: "pollution",
    severity: "high",
    title: "Oil Spill Detection",
    description: "Satellite imagery detected potential oil contamination near reef site",
    location: "Red Sea Coral - Egypt",
    timestamp: "2024-01-14T12:20:00Z",
    status: "resolved",
    value: "Detected",
    threshold: "None",
    impact: "Immediate threat to marine life",
  },
  {
    id: 5,
    type: "biodiversity",
    severity: "low",
    title: "Species Count Decline",
    description: "Minor decrease in fish species diversity observed",
    location: "Maldives Reef System",
    timestamp: "2024-01-14T09:30:00Z",
    status: "active",
    value: "15% decrease",
    threshold: "Stable",
    impact: "Ecosystem monitoring required",
  },
]

const alertTypes = [
  { id: "temperature", name: "Temperature", icon: Thermometer, color: "text-red-500" },
  { id: "bleaching", name: "Bleaching", icon: AlertTriangle, color: "text-orange-500" },
  { id: "water_quality", name: "Water Quality", icon: Droplets, color: "text-blue-500" },
  { id: "pollution", name: "Pollution", icon: XCircle, color: "text-purple-500" },
  { id: "biodiversity", name: "Biodiversity", icon: Fish, color: "text-green-500" },
]

const alertTrendData = [
  { date: "Jan 1", alerts: 12 },
  { date: "Jan 2", alerts: 8 },
  { date: "Jan 3", alerts: 15 },
  { date: "Jan 4", alerts: 6 },
  { date: "Jan 5", alerts: 18 },
  { date: "Jan 6", alerts: 9 },
  { date: "Jan 7", alerts: 14 },
]

export default function AlertsPage() {
  const [selectedTab, setSelectedTab] = useState("all")
  const [searchTerm, setSearchTerm] = useState("")
  const [severityFilter, setSeverityFilter] = useState("all")
  const [statusFilter, setStatusFilter] = useState("all")

  const filteredAlerts = alerts.filter((alert) => {
    const matchesSearch =
      alert.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      alert.location.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesSeverity = severityFilter === "all" || alert.severity === severityFilter
    const matchesStatus = statusFilter === "all" || alert.status === statusFilter
    const matchesTab = selectedTab === "all" || alert.type === selectedTab

    return matchesSearch && matchesSeverity && matchesStatus && matchesTab
  })

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "high":
        return "text-red-600 bg-red-50 border-red-200"
      case "medium":
        return "text-orange-600 bg-orange-50 border-orange-200"
      case "low":
        return "text-yellow-600 bg-yellow-50 border-yellow-200"
      default:
        return "text-gray-600 bg-gray-50 border-gray-200"
    }
  }

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case "high":
        return "destructive"
      case "medium":
        return "secondary"
      case "low":
        return "outline"
      default:
        return "secondary"
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "active":
        return "destructive"
      case "acknowledged":
        return "secondary"
      case "resolved":
        return "default"
      default:
        return "secondary"
    }
  }

  const getTypeIcon = (type: string) => {
    const alertType = alertTypes.find((t) => t.id === type)
    return alertType ? alertType.icon : AlertTriangle
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60))

    if (diffHours < 1) return "Less than 1 hour ago"
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? "s" : ""} ago`
    const diffDays = Math.floor(diffHours / 24)
    return `${diffDays} day${diffDays > 1 ? "s" : ""} ago`
  }

  const activeAlerts = alerts.filter((a) => a.status === "active")
  const highSeverityAlerts = alerts.filter((a) => a.severity === "high")

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-serif text-4xl font-bold text-gray-900">Alert System</h1>
          <p className="text-muted-foreground">Real-time monitoring and threat detection</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Settings className="h-4 w-4 mr-2" />
            Configure
          </Button>
          <Button variant="outline" size="sm">
            <Bell className="h-4 w-4 mr-2" />
            Notifications
          </Button>
        </div>
      </div>

      {/* Alert Summary Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="border-2 border-gray-800 shadow-lg">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Alerts</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{activeAlerts.length}</div>
            <div className="text-xs text-muted-foreground">Requiring attention</div>
          </CardContent>
        </Card>

        <Card className="border-2 border-gray-800 shadow-lg">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">High Severity</CardTitle>
            <XCircle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{highSeverityAlerts.length}</div>
            <div className="text-xs text-muted-foreground">Critical threats</div>
          </CardContent>
        </Card>

        <Card className="border-2 border-gray-800 shadow-lg">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Response Time</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">12m</div>
            <div className="text-xs text-muted-foreground">Average response</div>
          </CardContent>
        </Card>

        <Card className="border-2 border-gray-800 shadow-lg">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Resolution Rate</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">94%</div>
            <div className="text-xs text-muted-foreground">Last 30 days</div>
          </CardContent>
        </Card>
      </div>

      <Card className="border-2 border-gray-800 shadow-lg">
        <CardHeader>
          <CardTitle className="font-serif text-2xl">7-Day Alert Trend</CardTitle>
          <CardDescription>Daily alert volume over the past week</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={alertTrendData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="alerts" stroke="#3b82f6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Filters */}
      <div className="flex gap-4 items-center flex-wrap">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-600" />
          <Input
            placeholder="Search alerts..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 text-gray-900 placeholder:text-gray-500 border-2 border-gray-300 focus:border-blue-500"
          />
        </div>

        <Select value={severityFilter} onValueChange={setSeverityFilter}>
          <SelectTrigger className="w-32 text-gray-900 border-2 border-gray-300 focus:border-blue-500">
            <SelectValue placeholder="Severity" />
          </SelectTrigger>
          <SelectContent className="bg-white border-2 border-gray-300">
            <SelectItem
              value="all"
              className="text-gray-900 hover:bg-gray-100 data-[state=checked]:bg-blue-600 data-[state=checked]:text-white"
            >
              All Severity
            </SelectItem>
            <SelectItem
              value="high"
              className="text-gray-900 hover:bg-gray-100 data-[state=checked]:bg-blue-600 data-[state=checked]:text-white"
            >
              High
            </SelectItem>
            <SelectItem
              value="medium"
              className="text-gray-900 hover:bg-gray-100 data-[state=checked]:bg-blue-600 data-[state=checked]:text-white"
            >
              Medium
            </SelectItem>
            <SelectItem
              value="low"
              className="text-gray-900 hover:bg-gray-100 data-[state=checked]:bg-blue-600 data-[state=checked]:text-white"
            >
              Low
            </SelectItem>
          </SelectContent>
        </Select>

        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-32 text-gray-900 border-2 border-gray-300 focus:border-blue-500">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent className="bg-white border-2 border-gray-300">
            <SelectItem
              value="all"
              className="text-gray-900 hover:bg-gray-100 data-[state=checked]:bg-blue-600 data-[state=checked]:text-white"
            >
              All Status
            </SelectItem>
            <SelectItem
              value="active"
              className="text-gray-900 hover:bg-gray-100 data-[state=checked]:bg-blue-600 data-[state=checked]:text-white"
            >
              Active
            </SelectItem>
            <SelectItem
              value="acknowledged"
              className="text-gray-900 hover:bg-gray-100 data-[state=checked]:bg-blue-600 data-[state=checked]:text-white"
            >
              Acknowledged
            </SelectItem>
            <SelectItem
              value="resolved"
              className="text-gray-900 hover:bg-gray-100 data-[state=checked]:bg-blue-600 data-[state=checked]:text-white"
            >
              Resolved
            </SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Alert Tabs */}
      <Tabs value={selectedTab} onValueChange={setSelectedTab}>
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger
            value="all"
            className="text-black data-[state=active]:text-black data-[state=inactive]:text-black"
          >
            All Alerts
          </TabsTrigger>
          {alertTypes.map((type) => {
            const Icon = type.icon
            return (
              <TabsTrigger
                key={type.id}
                value={type.id}
                className="flex items-center gap-2 text-black data-[state=active]:text-black data-[state=inactive]:text-black"
              >
                <Icon className="h-4 w-4 text-black" />
                <span>{type.name}</span>
              </TabsTrigger>
            )
          })}
        </TabsList>

        <TabsContent value={selectedTab} className="mt-6">
          <Card className="border-2 border-gray-800 shadow-lg">
            <CardHeader>
              <CardTitle className="font-serif text-2xl">
                {selectedTab === "all" ? "All Alerts" : alertTypes.find((t) => t.id === selectedTab)?.name + " Alerts"}
              </CardTitle>
              <CardDescription>
                {filteredAlerts.length} alert{filteredAlerts.length !== 1 ? "s" : ""} found
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {filteredAlerts.length === 0 ? (
                  <div className="text-center py-8">
                    <AlertTriangle className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                    <div className="text-sm font-medium mb-2">No alerts found</div>
                    <div className="text-xs text-muted-foreground">Try adjusting your filters or search terms</div>
                  </div>
                ) : (
                  filteredAlerts.map((alert) => {
                    const Icon = getTypeIcon(alert.type)
                    return (
                      <div key={alert.id} className={`p-4 border rounded-lg ${getSeverityColor(alert.severity)}`}>
                        <div className="flex items-start justify-between">
                          <div className="flex items-start gap-3 flex-1">
                            <Icon className="h-5 w-5 mt-0.5 flex-shrink-0" />
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-1">
                                <h3 className="font-semibold">{alert.title}</h3>
                                <Badge variant={getSeverityBadge(alert.severity)}>{alert.severity}</Badge>
                                <Badge variant={getStatusBadge(alert.status)}>{alert.status}</Badge>
                              </div>
                              <p className="text-sm mb-2">{alert.description}</p>
                              <div className="flex items-center gap-4 text-xs text-muted-foreground">
                                <div className="flex items-center gap-1">
                                  <MapPin className="h-3 w-3" />
                                  {alert.location}
                                </div>
                                <div className="flex items-center gap-1">
                                  <Clock className="h-3 w-3" />
                                  {formatTimestamp(alert.timestamp)}
                                </div>
                              </div>
                              <div className="mt-2 text-xs">
                                <span className="font-medium">Current: </span>
                                {alert.value}
                                <span className="mx-2">•</span>
                                <span className="font-medium">Threshold: </span>
                                {alert.threshold}
                              </div>
                              <div className="mt-1 text-xs text-muted-foreground">
                                <span className="font-medium">Impact: </span>
                                {alert.impact}
                              </div>
                            </div>
                          </div>
                          <div className="flex gap-2 ml-4">
                            {alert.status === "active" && (
                              <>
                                <Button size="sm" variant="outline">
                                  Acknowledge
                                </Button>
                                <Button size="sm">Resolve</Button>
                              </>
                            )}
                            {alert.status === "acknowledged" && <Button size="sm">Resolve</Button>}
                          </div>
                        </div>
                      </div>
                    )
                  })
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
