"use client"

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import dynamic from "next/dynamic";
import React from "react";

// Dynamically import the Leaflet map component to avoid SSR issues
const OilSpillMap = dynamic(() => import("./OilSpillMap"), { ssr: false });

export default function OilSpillTrajectoryPage() {
  return (
    <div className="space-y-3">
      <Card className="bg-gradient-to-br from-blue-50 to-cyan-50 border-2 border-gray-800 shadow-lg">
        <CardHeader>
          <CardTitle className="font-serif text-2xl text-blue-900">
            Oil Spill Trajectory
          </CardTitle>
        </CardHeader>
        <CardContent>
          {/* Oil Spill Map and Controls */}
          <OilSpillMap />
        </CardContent>
      </Card>
    </div>
  );
} 