"use client"

import type React from "react"

import { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { BarChart3, Thermometer, Map, AlertTriangle, Menu, Bell, User, Home, X } from "lucide-react"

const navigation = [
  { name: "Overview", href: "/dashboard", icon: Home },
  { name: "Temperature", href: "/dashboard/temperature", icon: Thermometer },
  { name: "Metrics", href: "/dashboard/metrics", icon: BarChart3 },
  { name: "Map View", href: "/dashboard/map", icon: Map },
  { name: "Alerts", href: "/dashboard/alerts", icon: AlertTriangle },
]

const recentAlerts = [
  {
    id: 1,
    title: "High Temperature Alert",
    location: "Great Barrier Reef - Zone A",
    severity: "Critical",
    time: "2 minutes ago",
    description: "Water temperature exceeded 29°C threshold",
  },
  {
    id: 2,
    title: "Coral Bleaching Risk",
    location: "Maldives - Atoll B",
    severity: "Warning",
    time: "15 minutes ago",
    description: "Elevated stress indicators detected",
  },
  {
    id: 3,
    title: "Water Quality Alert",
    location: "Caribbean Reef - Sector C",
    severity: "Medium",
    time: "1 hour ago",
    description: "pH levels below optimal range",
  },
]

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar */}
      <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
        <SheetTrigger asChild>
          <Button variant="ghost" size="sm" className="lg:hidden fixed top-4 left-4 z-50">
            <Menu className="h-5 w-5" />
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="w-64 p-0">
          <div className="flex h-full flex-col">
            <div className="flex h-16 items-center px-6 border-b">
              <Link href="/" className="font-serif text-3xl font-bold text-blue-600">
                ReefShield
              </Link>
            </div>
            <nav className="flex-1 space-y-1 px-3 py-4">
              {navigation.map((item) => {
                const Icon = item.icon
                const isActive = pathname === item.href
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={cn(
                      "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                      isActive ? "bg-blue-600 text-white" : "text-gray-600 hover:bg-gray-100 hover:text-gray-900",
                    )}
                    onClick={() => setSidebarOpen(false)}
                  >
                    <Icon className="h-4 w-4" />
                    {item.name}
                  </Link>
                )
              })}
            </nav>
          </div>
        </SheetContent>
      </Sheet>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-64 lg:flex-col shadow-2xl">
        <div className="flex grow flex-col gap-y-5 overflow-y-auto border-r border-gray-200 bg-white px-6">
          <div className="flex h-16 shrink-0 items-center">
            <Link href="/" className="font-serif text-3xl font-bold text-blue-600">
              ReefShield
            </Link>
          </div>
          <nav className="flex flex-1 flex-col">
            <ul role="list" className="flex flex-1 flex-col gap-y-7">
              <li>
                <ul role="list" className="-mx-2 space-y-1">
                  {navigation.map((item) => {
                    const Icon = item.icon
                    const isActive = pathname === item.href
                    return (
                      <li key={item.name}>
                        <Link
                          href={item.href}
                          className={cn(
                            "group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-medium",
                            isActive ? "bg-blue-600 text-white" : "text-gray-700 hover:text-blue-700 hover:bg-gray-50",
                          )}
                        >
                          <Icon className="h-5 w-5 shrink-0" />
                          {item.name}
                        </Link>
                      </li>
                    )
                  })}
                </ul>
              </li>
            </ul>
          </nav>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top header */}
        <div className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-gray-200 bg-white px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-8">
          <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
            <div className="flex flex-1 items-center">
              <h1 className="font-serif text-3xl font-semibold text-gray-900">Coral Reef Monitoring Dashboard</h1>
            </div>
            <div className="flex items-center gap-x-4 lg:gap-x-6">
              <Dialog>
                <DialogTrigger asChild>
                  <Button variant="ghost" size="sm" className="relative text-gray-700 hover:text-gray-900">
                    <Bell className="h-5 w-5" />
                    <Badge className="absolute -top-2 -right-2 h-5 w-5 flex items-center justify-center text-xs bg-red-500 text-white border-2 border-white rounded-full">
                      3
                    </Badge>
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-md">
                  <DialogHeader>
                    <DialogTitle className="text-xl font-semibold flex items-center justify-between">
                      Recent Alerts
                      <X className="h-5 w-5 text-black cursor-pointer" />
                    </DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4 max-h-96 overflow-y-auto">
                    {recentAlerts.map((alert) => (
                      <div key={alert.id} className="border-l-4 border-red-500 pl-4 py-2">
                        <div className="flex items-center justify-between">
                          <h4 className="font-medium text-gray-900">{alert.title}</h4>
                          <Badge
                            variant={
                              alert.severity === "Critical"
                                ? "destructive"
                                : alert.severity === "Warning"
                                  ? "default"
                                  : "secondary"
                            }
                          >
                            {alert.severity}
                          </Badge>
                        </div>
                        <p className="text-sm text-gray-600 mt-1">{alert.location}</p>
                        <p className="text-sm text-gray-500 mt-1">{alert.description}</p>
                        <p className="text-xs text-gray-400 mt-2">{alert.time}</p>
                      </div>
                    ))}
                  </div>
                </DialogContent>
              </Dialog>
              <div className="hidden lg:block lg:h-6 lg:w-px lg:bg-gray-200" />
              <Button variant="ghost" size="sm" className="text-gray-700 hover:text-gray-900">
                <User className="h-5 w-5" />
              </Button>
              <div className="text-xs text-gray-500">Last updated: {new Date().toLocaleTimeString()}</div>
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="py-6">
          <div className="px-4 sm:px-6 lg:px-8">{children}</div>
        </main>
      </div>
    </div>
  )
}
