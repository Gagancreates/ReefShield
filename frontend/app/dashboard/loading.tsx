"use client"

import React, { useState, useEffect } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Waves, Activity, MapPin, Thermometer, Satellite, Database, Cpu } from "lucide-react"
import { cn } from "@/lib/utils"

// Local Skeleton component to avoid import issues
function Skeleton({
    className,
    ...props
}: React.HTMLAttributes<HTMLDivElement>) {
    return (
        <div
            className={cn("animate-pulse rounded-md bg-gray-200", className)}
            {...props}
        />
    )
}

const loadingSteps = [
    { icon: Satellite, text: "Connecting to satellite feeds...", progress: 20 },
    { icon: Database, text: "Loading reef monitoring data...", progress: 40 },
    { icon: Cpu, text: "Initializing AI analysis engine...", progress: 60 },
    { icon: MapPin, text: "Rendering interactive maps...", progress: 80 },
    { icon: Activity, text: "Finalizing dashboard components...", progress: 100 },
]

export default function DashboardLoading() {
    const [currentStep, setCurrentStep] = useState(0)
    const [progress, setProgress] = useState(0)

    useEffect(() => {
        const interval = setInterval(() => {
            setCurrentStep((prev) => {
                const nextStep = prev < loadingSteps.length - 1 ? prev + 1 : prev
                setProgress(loadingSteps[nextStep].progress)
                return nextStep
            })
        }, 800)

        return () => clearInterval(interval)
    }, [])
    return (
        <div className="space-y-6">
            {/* Loading Header */}
            <div className="text-center py-8">
                <div className="flex items-center justify-center mb-4">
                    <div className="relative">
                        <Waves className="h-12 w-12 text-blue-600 animate-pulse" />
                        <div className="absolute inset-0 animate-spin">
                            <Activity className="h-12 w-12 text-cyan-500 opacity-50" />
                        </div>
                    </div>
                </div>
                <h1 className="font-serif text-3xl font-bold text-gray-900 mb-2">Loading Dashboard</h1>
                <p className="text-gray-600">Initializing coral reef monitoring systems...</p>

                {/* Loading Progress Indicator */}
                <div className="mt-6 max-w-md mx-auto">
                    <div className="bg-gray-200 rounded-full h-3 overflow-hidden">
                        <div
                            className="bg-gradient-to-r from-blue-500 to-cyan-500 h-full rounded-full transition-all duration-700 ease-out"
                            style={{ width: `${progress}%` }}
                        />
                    </div>
                    <div className="flex justify-between text-xs text-gray-500 mt-2">
                        <div className="flex items-center gap-2">
                            {React.createElement(loadingSteps[currentStep].icon, {
                                className: "h-4 w-4 animate-pulse"
                            })}
                            <span>{loadingSteps[currentStep].text}</span>
                        </div>
                        <span>{progress}%</span>
                    </div>
                </div>
            </div>

            <div className="grid gap-6 lg:grid-cols-5">
                {/* Main Content Area Loading */}
                <div className="lg:col-span-3 space-y-6">
                    {/* Map Loading */}
                    <Card className="bg-gradient-to-br from-blue-50 to-cyan-50 border-2 border-gray-800 shadow-lg">
                        <CardContent className="p-6">
                            <div className="flex items-center justify-between mb-4">
                                <div>
                                    <Skeleton className="h-8 w-64 mb-2" />
                                    <Skeleton className="h-4 w-48" />
                                </div>
                                <Skeleton className="h-8 w-20" />
                            </div>
                            <div className="relative h-80 bg-gradient-to-br from-blue-100 to-blue-200 rounded-lg overflow-hidden">
                                <div className="absolute inset-0 flex items-center justify-center">
                                    <div className="text-center">
                                        <MapPin className="h-16 w-16 mx-auto mb-4 text-blue-400 animate-bounce" />
                                        <div className="text-blue-600 font-medium">Loading Interactive Map...</div>
                                        <div className="text-blue-500 text-sm mt-1">Fetching reef locations</div>
                                    </div>
                                </div>
                                {/* Animated loading dots on map */}
                                <div className="absolute top-1/4 left-1/4 w-4 h-4 bg-blue-400 rounded-full animate-ping" />
                                <div className="absolute top-1/3 right-1/3 w-4 h-4 bg-cyan-400 rounded-full animate-ping" style={{ animationDelay: '0.5s' }} />
                                <div className="absolute bottom-1/3 left-1/2 w-4 h-4 bg-blue-500 rounded-full animate-ping" style={{ animationDelay: '1s' }} />
                            </div>
                        </CardContent>
                    </Card>

                    {/* Temperature Chart Loading */}
                    <Card className="bg-gradient-to-br from-orange-50 to-red-50 border-2 border-gray-800 shadow-lg">
                        <CardContent className="p-6">
                            <div className="flex items-center mb-4">
                                <Thermometer className="h-6 w-6 text-orange-600 mr-2 animate-pulse" />
                                <Skeleton className="h-6 w-48" />
                            </div>
                            <Skeleton className="h-4 w-64 mb-4" />
                            <div className="h-64 bg-gradient-to-t from-orange-100 to-red-100 rounded-lg flex items-center justify-center">
                                <div className="text-center">
                                    <div className="flex space-x-1 justify-center mb-2">
                                        {[...Array(5)].map((_, i) => (
                                            <div
                                                key={i}
                                                className="w-2 h-8 bg-orange-400 rounded animate-pulse"
                                                style={{ animationDelay: `${i * 0.2}s` }}
                                            />
                                        ))}
                                    </div>
                                    <div className="text-orange-600 font-medium">Loading Temperature Data...</div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    {/* System Status & Quick Actions Loading */}
                    <div className="grid gap-6 md:grid-cols-2">
                        <Card className="bg-gradient-to-br from-emerald-50 to-green-50 border-2 border-gray-800 shadow-lg">
                            <CardContent className="p-6">
                                <Skeleton className="h-6 w-32 mb-4" />
                                <div className="space-y-3">
                                    {[...Array(4)].map((_, i) => (
                                        <div key={i} className="flex items-center justify-between p-3 bg-white rounded-lg border-2 border-gray-200">
                                            <Skeleton className="h-4 w-24" />
                                            <Skeleton className="h-5 w-16" />
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>

                        <Card className="bg-gradient-to-br from-purple-50 to-indigo-50 border-2 border-gray-800 shadow-lg">
                            <CardContent className="p-6">
                                <Skeleton className="h-6 w-28 mb-4" />
                                <div className="space-y-3">
                                    {[...Array(3)].map((_, i) => (
                                        <div key={i} className="p-3 bg-white rounded-lg border-2 border-gray-200">
                                            <Skeleton className="h-4 w-32 mb-1" />
                                            <Skeleton className="h-3 w-48" />
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </div>

                {/* Sidebar Loading */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Monitoring Locations Loading */}
                    <Card className="bg-gradient-to-br from-blue-50 to-cyan-50 border-2 border-gray-800 shadow-lg">
                        <CardContent className="p-6">
                            <Skeleton className="h-6 w-40 mb-2" />
                            <Skeleton className="h-4 w-56 mb-4" />
                            <div className="space-y-3">
                                {[...Array(4)].map((_, i) => (
                                    <div key={i} className="p-3 bg-white rounded-lg border-2 border-gray-200">
                                        <div className="flex items-center justify-between">
                                            <div className="flex-1">
                                                <Skeleton className="h-4 w-32 mb-1" />
                                                <Skeleton className="h-3 w-24" />
                                            </div>
                                            <div className="text-right">
                                                <Skeleton className="h-6 w-12 mb-1" />
                                                <Skeleton className="h-4 w-16" />
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>

                    {/* Alerts Loading */}
                    <Card className="bg-gradient-to-br from-red-50 to-orange-50 border-2 border-gray-800 shadow-lg">
                        <CardContent className="p-6">
                            <Skeleton className="h-6 w-32 mb-2" />
                            <Skeleton className="h-4 w-48 mb-4" />
                            <div className="space-y-4">
                                {[...Array(3)].map((_, i) => (
                                    <div key={i} className="border-l-4 border-red-300 pl-4 py-3 bg-white rounded-lg border-2 border-gray-200">
                                        <div className="flex items-center justify-between mb-2">
                                            <Skeleton className="h-4 w-32" />
                                            <Skeleton className="h-5 w-16" />
                                        </div>
                                        <Skeleton className="h-3 w-28 mb-1" />
                                        <Skeleton className="h-3 w-40 mb-2" />
                                        <Skeleton className="h-3 w-20" />
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