"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { ArrowUpRight } from "lucide-react"

interface ForecastEntry {
  timestamp: string
  breaking_wave_height: { max: number; range_text: string; unit: string }
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
  surfSpotTimezone: string | null
}

export function SwellDetailTile({ hourData, surfSpotTimezone }: SwellDetailTileProps) {
  console.log("SwellDetailTile: hourData prop received:", hourData);
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

  const displayTime = hourData.timestamp ? new Date(hourData.timestamp).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true, timeZone: surfSpotTimezone || undefined }) : 'N/A';

  return (
    <Card>
      <CardHeader>
        <CardTitle>Swell Details</CardTitle>
        <p className="text-sm text-muted-foreground">{displayTime}</p>
      </CardHeader>
      <CardContent className="space-y-4">
        {hourData.swell_components && hourData.swell_components.length > 0 ? (
          hourData.swell_components.map((swell, index) => (
            <div key={index} className="space-y-1">
              <p className="font-semibold">Swell {index + 1}:</p>
              <div className="flex items-center gap-2 ml-2">
                <span>{swell.height.toFixed(1)}{swell.unit} @ {swell.period.toFixed(1)}s from {swell.direction} ({swell.direction_degrees}°)</span>
                <ArrowUpRight style={{ transform: `rotate(${swell.direction_degrees}deg)` }} className="h-4 w-4 text-blue-500" />
              </div>
            </div>
          ))
        ) : (
          <p className="text-muted-foreground">No detailed swell components available.</p>
        )}
        
        {/* Display breaking wave height separately */}
        {hourData.breaking_wave_height && (
          <div className="space-y-1 mt-4">
            <p className="font-semibold">Breaking Wave Height:</p>
            <p className="ml-2">{hourData.breaking_wave_height.range_text}</p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

