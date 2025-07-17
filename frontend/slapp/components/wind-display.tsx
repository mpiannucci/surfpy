"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowUp } from "lucide-react"

interface ForecastEntry {
  timestamp: string
  wind: { speed: number; direction: string; direction_degrees: number; unit: string }
}

interface WindDisplayProps {
  dailyData: ForecastEntry[]
}

export function WindDisplay({ dailyData }: WindDisplayProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Wind</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-row justify-between overflow-x-auto">
        {dailyData.map((hour, index) => (
          <div key={index} className="flex flex-col items-center p-2 flex-shrink-0">
            <p className="text-xs text-muted-foreground">{new Date(hour.timestamp).toLocaleTimeString('en-US', { hour: 'numeric', hour12: true })}</p>
            <ArrowUp style={{ transform: `rotate(${hour.wind.direction_degrees}deg)` }} className="h-6 w-6 my-1" />
            <p className="text-sm font-bold">{hour.wind.speed.toFixed(0)}</p>
            <p className="text-xs text-muted-foreground">{hour.wind.unit}</p>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
