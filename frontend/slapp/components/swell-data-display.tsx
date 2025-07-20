import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Waves, ArrowUp } from "lucide-react"
import { SwellDataTable } from "@/components/swell-data-table"

interface SwellComponent {
  height: number
  period: number
  direction: number
}

interface SwellComponents {
  swell_1?: SwellComponent
  swell_2?: SwellComponent
  swell_3?: SwellComponent
  swell_4?: SwellComponent
  [key: string]: SwellComponent | undefined
}

interface SwellData {
  date: string
  swell_components: SwellComponents
  buoy_id?: string
}

interface Swell {
  height: number
  period: number
  direction: number
}

interface SwellDataDisplayProps {
  swellData: SwellData | null | undefined
  swells: Swell[]
  buoyId: string
}

export function SwellDataDisplay({ swellData, swells, buoyId }: SwellDataDisplayProps) {
  const hasLegacySwells = swells && swells.length > 0

  return (
    <Card className="bg-background/10 border-border/30">
      <CardHeader>
        <CardTitle>Swell Data</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="mb-4">
          <h3 className="text-sm font-medium text-muted-foreground">Buoy ID</h3>
          <p>{buoyId}</p>
        </div>
        {swellData ? (
          <SwellDataTable swellData={swellData} buoyId={buoyId} />
        ) : hasLegacySwells ? (
          <div className="space-y-4">
            {swells.map((swell, index) => (
              <div key={index} className="grid grid-cols-3 gap-4">
                <div>
                  <h3 className="text-sm font-medium text-muted-foreground">Height</h3>
                  <p>{swell.height.toFixed(1)} ft</p>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-muted-foreground">Period</h3>
                  <p>{swell.period.toFixed(1)} sec</p>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-muted-foreground">Direction</h3>
                  <div className="flex items-center gap-1">
                    <ArrowUp
                      className="h-4 w-4 text-muted-foreground"
                      style={{ transform: `rotate(${(swell.direction + 180) % 360}deg)` }}
                    />
                    <p>{swell.direction.toFixed(0)}°</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex items-center gap-2 text-muted-foreground">
            <Waves className="h-4 w-4" />
            <p>No swell data available for this session.</p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
