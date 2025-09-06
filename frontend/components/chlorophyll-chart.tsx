"use client"

import { Bar, BarChart, XAxis, YAxis, CartesianGrid, ResponsiveContainer, ReferenceLine } from "recharts"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { Badge } from "@/components/ui/badge"

interface ChlorophyllChartProps {
  value: number;
  threshold: number;
  riskLevel: 'low' | 'moderate' | 'high';
}

export function ChlorophyllChart({ value, threshold, riskLevel }: ChlorophyllChartProps) {
  const chartData = [
    {
      name: 'Current',
      value: value,
      fill: riskLevel === 'high' ? '#ef4444' : riskLevel === 'moderate' ? '#f59e0b' : '#10b981'
    }
  ];

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200';
      case 'moderate': return 'bg-amber-100 text-amber-800 border-amber-200';
      default: return 'bg-emerald-100 text-emerald-800 border-emerald-200';
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="text-lg font-semibold">Chlorophyll-a Levels</h4>
        <Badge className={getRiskColor(riskLevel)}>
          {riskLevel.charAt(0).toUpperCase() + riskLevel.slice(1)} Risk
        </Badge>
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <div className="text-2xl font-bold text-blue-600">{value.toFixed(3)}</div>
          <div className="text-sm text-gray-600">mg/m³</div>
          <div className="text-xs text-gray-500">Current Level</div>
        </div>
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <div className="text-2xl font-bold text-gray-600">{threshold}</div>
          <div className="text-sm text-gray-600">mg/m³</div>
          <div className="text-xs text-gray-500">Threshold</div>
        </div>
      </div>

      <ChartContainer
        config={{
          value: {
            label: "Chlorophyll-a (mg/m³)",
            color: "hsl(var(--chart-1))",
          },
        }}
        className="h-32"
      >
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 10, right: 10, left: 10, bottom: 10 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis domain={[0, Math.max(value * 1.2, threshold * 1.2)]} />
            <ChartTooltip content={<ChartTooltipContent />} />
            <ReferenceLine 
              y={threshold} 
              stroke="#ef4444" 
              strokeDasharray="5 5" 
              label={{ value: "Threshold", position: "top" }}
            />
            <Bar dataKey="value" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </ChartContainer>

      <div className="text-xs text-gray-500 space-y-1">
        <p>• Threshold: {threshold} mg/m³ (elevated risk level)</p>
        <p>• Values above threshold indicate potential water quality concerns</p>
        <p>• Current status: {riskLevel === 'low' ? 'Normal levels' : riskLevel === 'moderate' ? 'Elevated levels' : 'High levels - monitoring required'}</p>
      </div>
    </div>
  );
}