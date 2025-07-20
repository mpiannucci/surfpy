import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Cloud, Thermometer, Wind } from "lucide-react"
import type { MeteorologicalDataEntry } from "@/lib/types"
import { formatDateTime } from "@/lib/utils"

interface MeteorologicalDataDisplayProps {
  metData: MeteorologicalDataEntry[] | null | undefined
}

export function MeteorologicalDataDisplay({ metData }: MeteorologicalDataDisplayProps) {
  if (!metData || !Array.isArray(metData) || metData.length === 0) {
    return (
      <Card className="bg-background/10 border-border/30">
        <CardHeader>
          <CardTitle>Weather Conditions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2 text-muted-foreground">
            <Cloud className="h-4 w-4" />
            <p>No meteorological data available for this session.</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  // Use the first entry in the array
  const data = metData[0]
  const formattedDate = formatDateTime(data.date)

  return (
    <Card className="bg-background/10 border-border/30">
      <CardHeader>
        <CardTitle>Weather Conditions</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-sm text-muted-foreground mb-4">
          <p>Data recorded at {formattedDate}</p>
        </div>

        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
          {/* Prioritize wind speed and direction as requested */}
          {data.wind_speed !== undefined && (
            <div className="flex items-start gap-2">
              <Wind className="h-5 w-5 text-primary mt-0.5" />
              <div>
                <p className="text-sm font-medium text-muted-foreground">Wind Speed</p>
                <p className="text-lg font-semibold">{data.wind_speed.toFixed(1)} mph</p>
              </div>
            </div>
          )}

          {data.wind_direction !== undefined && (
            <div className="flex items-start gap-2">
              <Wind className="h-5 w-5 text-primary mt-0.5" />
              <div>
                <p className="text-sm font-medium text-muted-foreground">Wind Direction</p>
                <p className="text-lg font-semibold">{data.wind_direction.toFixed(0)}°</p>
              </div>
            </div>
          )}

          {data.air_temperature !== undefined && (
            <div className="flex items-start gap-2">
              <Thermometer className="h-5 w-5 text-primary mt-0.5" />
              <div>
                <p className="text-sm font-medium text-muted-foreground">Air Temperature</p>
                <p className="text-lg font-semibold">{data.air_temperature.toFixed(1)}°F</p>
              </div>
            </div>
          )}

          {data.water_temperature !== undefined && (
            <div className="flex items-start gap-2">
              <Thermometer className="h-5 w-5 text-primary mt-0.5" />
              <div>
                <p className="text-sm font-medium text-muted-foreground">Water Temperature</p>
                <p className="text-lg font-semibold">{data.water_temperature.toFixed(1)}°F</p>
              </div>
            </div>
          )}

          {data.wind_gust !== undefined && (
            <div className="flex items-start gap-2">
              <Wind className="h-5 w-5 text-primary mt-0.5" />
              <div>
                <p className="text-sm font-medium text-muted-foreground">Wind Gust</p>
                <p className="text-lg font-semibold">{data.wind_gust.toFixed(1)} mph</p>
              </div>
            </div>
          )}

          
        </div>
      </CardContent>
    </Card>
  )
}
