"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Progress } from "@/components/ui/progress"
import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
} from "recharts"
import { Activity, Droplets, Fish, Waves, TrendingUp, TrendingDown, Download, RefreshCw } from "lucide-react"

// Dummy data for various metrics
const healthScoreData = [
  { month: "Jan", score: 85 },
  { month: "Feb", score: 87 },
  { month: "Mar", score: 84 },
  { month: "Apr", score: 89 },
  { month: "May", score: 91 },
  { month: "Jun", score: 87 },
]

const biodiversityData = [
  { species: "Hard Coral", count: 45, percentage: 35 },
  { species: "Soft Coral", count: 32, percentage: 25 },
  { species: "Fish Species", count: 28, percentage: 22 },
  { species: "Other Marine Life", count: 23, percentage: 18 },
]

const waterQualityMetrics = [
  { parameter: "pH Level", value: 8.2, optimal: "8.1-8.4", status: "good", trend: "stable" },
  { parameter: "Dissolved Oxygen", value: 7.8, optimal: "6.0-8.0", status: "excellent", trend: "up" },
  { parameter: "Turbidity", value: 2.1, optimal: "<3.0 NTU", status: "good", trend: "down" },
  { parameter: "Salinity", value: 35.2, optimal: "34-36 ppt", status: "good", trend: "stable" },
  { parameter: "Nitrate", value: 0.8, optimal: "<1.0 mg/L", status: "good", trend: "down" },
  { parameter: "Phosphate", value: 0.03, optimal: "<0.05 mg/L", status: "excellent", trend: "stable" },
]

const coralCoverageData = [
  { month: "Jan", coverage: 76 },
  { month: "Feb", coverage: 77 },
  { month: "Mar", coverage: 76.5 },
  { month: "Apr", coverage: 77.8 },
  { month: "May", coverage: 78.2 },
  { month: "Jun", coverage: 78 },
]

const waterQualityTrendData = [
  { week: "Week 1", ph: 8.1, oxygen: 7.5, turbidity: 2.3 },
  { week: "Week 2", ph: 8.2, oxygen: 7.6, turbidity: 2.1 },
  { week: "Week 3", ph: 8.0, oxygen: 7.8, turbidity: 2.4 },
  { week: "Week 4", ph: 8.2, oxygen: 7.8, turbidity: 2.1 },
]

const speciesCountData = [
  { site: "Site A", fish: 45, coral: 32, other: 18 },
  { site: "Site B", fish: 38, coral: 28, other: 15 },
  { site: "Site C", fish: 52, coral: 35, other: 22 },
  { site: "Site D", fish: 41, coral: 30, other: 19 },
]

const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"]

export default function MetricsPage() {
  const currentHealthScore = healthScoreData[healthScoreData.length - 1]?.score || 0
  const previousHealthScore = healthScoreData[healthScoreData.length - 2]?.score || 0
  const healthTrend = currentHealthScore - previousHealthScore

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-serif text-4xl font-bold text-gray-900">Key Metrics</h1>
          <p className="text-muted-foreground">Comprehensive reef health and environmental indicators</p>
        </div>
        <div className="flex gap-2">
          <Select defaultValue="30d">
            <SelectTrigger className="w-32 text-gray-900 border-2 border-gray-300 focus:border-blue-500">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-white border-2 border-gray-300">
              <SelectItem value="7d" className="text-gray-900 hover:bg-gray-100 focus:bg-blue-100 focus:text-blue-900">
                7 Days
              </SelectItem>
              <SelectItem value="30d" className="text-gray-900 hover:bg-gray-100 focus:bg-blue-100 focus:text-blue-900">
                30 Days
              </SelectItem>
              <SelectItem value="90d" className="text-gray-900 hover:bg-gray-100 focus:bg-blue-100 focus:text-blue-900">
                90 Days
              </SelectItem>
              <SelectItem value="1y" className="text-gray-900 hover:bg-gray-100 focus:bg-blue-100 focus:text-blue-900">
                1 Year
              </SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Key Performance Indicators */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="border-2 border-gray-800 shadow-lg">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-base font-medium">Overall Health Score</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{currentHealthScore}%</div>
            <div className="flex items-center text-xs text-muted-foreground">
              {healthTrend > 0 ? (
                <TrendingUp className="h-3 w-3 mr-1 text-green-500" />
              ) : (
                <TrendingDown className="h-3 w-3 mr-1 text-red-500" />
              )}
              {healthTrend > 0 ? "+" : ""}
              {healthTrend}% from last month
            </div>
            <Progress value={currentHealthScore} className="mt-2" />
          </CardContent>
        </Card>

        <Card className="border-2 border-gray-800 shadow-lg">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-base font-medium">Biodiversity Index</CardTitle>
            <Fish className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">128</div>
            <div className="flex items-center text-xs text-muted-foreground">
              <TrendingUp className="h-3 w-3 mr-1 text-green-500" />
              +5 species this month
            </div>
            <div className="text-xs text-muted-foreground mt-1">Species count</div>
          </CardContent>
        </Card>

        <Card className="border-2 border-gray-800 shadow-lg">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-base font-medium">Water Quality</CardTitle>
            <Droplets className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">92%</div>
            <div className="flex items-center text-xs text-muted-foreground">
              <TrendingUp className="h-3 w-3 mr-1 text-green-500" />
              +2% improvement
            </div>
            <Progress value={92} className="mt-2" />
          </CardContent>
        </Card>

        <Card className="border-2 border-gray-800 shadow-lg">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-base font-medium">Coral Coverage</CardTitle>
            <Waves className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">78%</div>
            <div className="flex items-center text-xs text-muted-foreground">
              <TrendingUp className="h-3 w-3 mr-1 text-green-500" />
              +1.2% growth
            </div>
            <Progress value={78} className="mt-2" />
          </CardContent>
        </Card>
      </div>

      {/* Charts Row */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Health Score Trend */}
        <Card className="border-2 border-gray-800 shadow-lg">
          <CardHeader>
            <CardTitle className="font-serif text-2xl">Health Score Trend</CardTitle>
            <CardDescription>6-month reef health progression</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={healthScoreData}>
                  <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                  <XAxis dataKey="month" className="text-xs" />
                  <YAxis domain={[80, 95]} className="text-xs" />
                  <Tooltip formatter={(value: number) => [`${value}%`, "Health Score"]} />
                  <Line
                    type="monotone"
                    dataKey="score"
                    stroke="#10b981"
                    strokeWidth={3}
                    dot={{ fill: "#10b981", strokeWidth: 2, r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Biodiversity Distribution */}
        <Card className="border-2 border-gray-800 shadow-lg">
          <CardHeader>
            <CardTitle className="font-serif text-2xl">Biodiversity Distribution</CardTitle>
            <CardDescription>Species composition across reef sites</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={biodiversityData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percentage }) => `${name}: ${percentage}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="count"
                  >
                    {biodiversityData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: number) => [`${value}`, "Species Count"]} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Additional Charts Section */}
      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="border-2 border-gray-800 shadow-lg">
          <CardHeader>
            <CardTitle className="font-serif text-2xl">Coral Coverage Trend</CardTitle>
            <CardDescription>Monthly coral coverage percentage</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={coralCoverageData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis domain={[75, 80]} tickFormatter={(value) => `${value}%`} />
                  <Tooltip formatter={(value: number) => [`${value}%`, "Coverage"]} />
                  <Area type="monotone" dataKey="coverage" stroke="#06b6d4" fill="#06b6d4" fillOpacity={0.3} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card className="border-2 border-gray-800 shadow-lg">
          <CardHeader>
            <CardTitle className="font-serif text-2xl">Water Quality Trends</CardTitle>
            <CardDescription>Weekly water parameter measurements</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={waterQualityTrendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="week" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="ph" stroke="#8b5cf6" strokeWidth={2} name="pH Level" />
                  <Line type="monotone" dataKey="oxygen" stroke="#10b981" strokeWidth={2} name="Oxygen (mg/L)" />
                  <Line type="monotone" dataKey="turbidity" stroke="#f59e0b" strokeWidth={2} name="Turbidity (NTU)" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Species Count Comparison Chart */}
      <Card className="border-2 border-gray-800 shadow-lg">
        <CardHeader>
          <CardTitle className="font-serif text-2xl">Species Count by Site</CardTitle>
          <CardDescription>Biodiversity comparison across monitoring sites</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={speciesCountData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="site" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="fish" fill="#3b82f6" name="Fish Species" />
                <Bar dataKey="coral" fill="#10b981" name="Coral Species" />
                <Bar dataKey="other" fill="#f59e0b" name="Other Marine Life" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Environmental Factors */}
      <div className="grid gap-6 md:grid-cols-3">
        <Card className="border-2 border-gray-800 shadow-lg">
          <CardHeader>
            <CardTitle className="font-serif text-xl">Coral Bleaching Risk</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600 mb-2">Low</div>
              <Progress value={25} className="mb-2" />
              <div className="text-sm text-muted-foreground">Current conditions favorable for coral health</div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-2 border-gray-800 shadow-lg">
          <CardHeader>
            <CardTitle className="font-serif text-xl">Ocean Acidification</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center">
              <div className="text-3xl font-bold text-yellow-600 mb-2">Moderate</div>
              <Progress value={45} className="mb-2" />
              <div className="text-sm text-muted-foreground">pH levels within acceptable range</div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-2 border-gray-800 shadow-lg">
          <CardHeader>
            <CardTitle className="font-serif text-xl">Pollution Index</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600 mb-2">Low</div>
              <Progress value={20} className="mb-2" />
              <div className="text-sm text-muted-foreground">Minimal human impact detected</div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
