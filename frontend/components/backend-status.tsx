"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { 
  useBackendConnection, 
  useModelExecution, 
  useSchedulerStatus 
} from "@/lib/hooks/useRealtimeData"
import { 
  Wifi, 
  WifiOff, 
  AlertTriangle, 
  Play, 
  Clock, 
  Activity,
  RefreshCw
} from "lucide-react"

export function BackendStatus() {
  const { connectionStatus, lastChecked } = useBackendConnection()
  const { triggerRun, isRunning, lastResult } = useModelExecution()
  const { schedulerInfo, loading: schedulerLoading } = useSchedulerStatus()

  const getConnectionIcon = () => {
    switch (connectionStatus) {
      case 'connected':
        return <Wifi className="h-4 w-4 text-green-600" />
      case 'disconnected':
        return <WifiOff className="h-4 w-4 text-orange-600" />
      case 'error':
        return <AlertTriangle className="h-4 w-4 text-red-600" />
      default:
        return <WifiOff className="h-4 w-4 text-gray-600" />
    }
  }

  const getConnectionBadge = () => {
    switch (connectionStatus) {
      case 'connected':
        return <Badge className="bg-green-100 text-green-800 border-green-200">Connected</Badge>
      case 'disconnected':
        return <Badge className="bg-orange-100 text-orange-800 border-orange-200">Connecting...</Badge>
      case 'error':
        return <Badge className="bg-red-100 text-red-800 border-red-200">Error</Badge>
      default:
        return <Badge className="bg-gray-100 text-gray-800 border-gray-200">Unknown</Badge>
    }
  }

  const formatTime = (isoString: string | null) => {
    if (!isoString) return 'Not scheduled'
    try {
      return new Date(isoString).toLocaleString()
    } catch {
      return 'Invalid date'
    }
  }

  return (
    <Card className="bg-gradient-to-br from-slate-50 to-gray-50 border-2 border-gray-800 shadow-lg">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="font-serif text-xl text-slate-900 flex items-center gap-2">
            {getConnectionIcon()}
            Backend Status
          </CardTitle>
          {process.env.NEXT_PUBLIC_SHOW_CONNECTION_STATUS === 'true' && (
            <div className="flex items-center gap-2">
              {getConnectionBadge()}
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent className="pt-0 space-y-3">
        {/* Connection Status */}
        <div className="p-3 bg-white rounded-lg border-2 border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">FastAPI Backend</span>
            {getConnectionBadge()}
          </div>
          {lastChecked && (
            <div className="text-xs text-gray-500">
              Last checked: {lastChecked.toLocaleTimeString()}
            </div>
          )}
        </div>

        {/* Scheduler Status */}
        {!schedulerLoading && schedulerInfo && (
          <div className="p-3 bg-white rounded-lg border-2 border-gray-200">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium flex items-center gap-2">
                <Clock className="h-4 w-4" />
                Scheduler
              </span>
              <Badge className={`${
                schedulerInfo.scheduler?.is_running 
                  ? 'bg-green-100 text-green-800 border-green-200' 
                  : 'bg-red-100 text-red-800 border-red-200'
              }`}>
                {schedulerInfo.scheduler?.is_running ? 'Active' : 'Inactive'}
              </Badge>
            </div>
            {schedulerInfo.scheduler?.jobs?.[0] && (
              <div className="text-xs text-gray-600">
                Next run: {formatTime(schedulerInfo.scheduler.jobs[0].next_run_time)}
              </div>
            )}
          </div>
        )}

        {/* Model Execution Controls */}
        <div className="p-3 bg-white rounded-lg border-2 border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Model Execution
            </span>
            <Button 
              size="sm" 
              onClick={triggerRun} 
              disabled={isRunning || connectionStatus !== 'connected'}
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              {isRunning ? (
                <>
                  <RefreshCw className="h-3 w-3 mr-1 animate-spin" />
                  Running...
                </>
              ) : (
                <>
                  <Play className="h-3 w-3 mr-1" />
                  Trigger Run
                </>
              )}
            </Button>
          </div>
          {lastResult && (
            <div className={`text-xs p-2 rounded ${
              lastResult.includes('successfully') 
                ? 'bg-green-50 text-green-700' 
                : 'bg-red-50 text-red-700'
            }`}>
              {lastResult}
            </div>
          )}
        </div>

        {/* Connection Warning */}
        {connectionStatus === 'error' && (
          <div className="p-3 bg-orange-50 border border-orange-200 rounded-lg">
            <div className="flex items-center gap-2 text-orange-800 text-sm">
              <AlertTriangle className="h-4 w-4" />
              Backend connection lost. Using cached data.
            </div>
          </div>
        )}

        {/* Debug Information */}
        {process.env.NEXT_PUBLIC_DEBUG_API_CALLS === 'true' && (
          <div className="p-2 bg-gray-100 rounded text-xs">
            <div>Environment: {process.env.NEXT_PUBLIC_ENVIRONMENT}</div>
            <div>API URL: {process.env.NEXT_PUBLIC_API_BASE_URL}</div>
            <div>Connection: {connectionStatus}</div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}