"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"

interface ForecastEntry {
  timestamp: string
  swell_components: Array<{
    height: number
    period: number
    direction: string
    direction_degrees: number
    unit: string
  }>
}

interface SwellDetailTileProps {
  hourData: ForecastEntry | null
}

export function SwellDetailTile({ hourData }: SwellDetailTileProps) {
  if (!hourData) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Swell Details</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">Hover over the chart for details.</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Swell Details</CardTitle>
        <p className="text-sm text-muted-foreground">{new Date(hourData.timestamp).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })}</p>
      </CardHeader>
      <CardContent className="space-y-4">
        {hourData.swell_components.map((swell, index) => (
          <div key={index} className="grid grid-cols-3 gap-2 text-center">
            <div>
              <p className="text-xs text-muted-foreground">Height</p>
              <p className="font-bold text-lg">{hourData.breaking_wave_height.range_text}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Period</p>
              <p className="font-bold text-lg">{swell.period.toFixed(1)}s</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Direction</p>
              <p className="font-bold text-lg">{swell.direction} ({swell.direction_degrees}°)</p>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
