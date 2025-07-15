import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Waves } from "lucide-react"
import type { TideData } from "@/lib/types"
import { formatDateTime } from "@/lib/utils"

interface TideDataDisplayProps {
  tideData: TideData | null | undefined
}

export function TideDataDisplay({ tideData }: TideDataDisplayProps) {
  if (!tideData) {
    return (
      <Card className="bg-background/10 border-border/30">
        <CardHeader>
          <CardTitle>Tide Information</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2 text-muted-foreground">
            <Waves className="h-4 w-4" />
            <p>No tide data available for this session.</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  const formattedDate = formatDateTime(tideData.date)

  return (
    <Card className="bg-background/10 border-border/30">
      <CardHeader>
        <CardTitle>Tide Information</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-sm text-muted-foreground mb-4">
          <p>Data recorded at {formattedDate}</p>
        </div>

        <div className="space-y-4">
          {tideData.water_level !== undefined && (
            <div className="flex items-start gap-2">
              <Waves className="h-5 w-5 text-primary mt-0.5" />
              <div>
                <p className="text-sm font-medium text-muted-foreground">Water Level</p>
                <p className="text-lg font-semibold">
                  {tideData.water_level.toFixed(2)} {tideData.units || "meters"}
                </p>
              </div>
            </div>
          )}

          {tideData.state && (
            <div className="flex items-start gap-2">
              <Waves className="h-5 w-5 text-primary mt-0.5" />
              <div>
                <p className="text-sm font-medium text-muted-foreground">Tide State</p>
                <p className="text-lg font-semibold">{tideData.state || "Unknown"}</p>
              </div>
            </div>
          )}

          {tideData.station_id && (
            <div className="flex items-start gap-2">
              <Waves className="h-5 w-5 text-primary mt-0.5" />
              <div>
                <p className="text-sm font-medium text-muted-foreground">Station ID</p>
                <p className="text-lg font-semibold">{tideData.station_id}</p>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
