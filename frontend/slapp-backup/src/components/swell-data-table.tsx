"use client"

import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { AlertCircle } from "lucide-react"
import { formatDateTime } from "@/lib/utils"

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

interface SwellDataTableProps {
  swellData: SwellData | null | undefined
  buoyId?: string
}

export function SwellDataTable({ swellData, buoyId }: SwellDataTableProps) {
  // Check if we have valid swell data
  const hasSwellData = swellData && swellData.swell_components && Object.keys(swellData.swell_components).length > 0

  // Get the buoy ID from either the swell data or the prop
  const displayBuoyId = swellData?.buoy_id || buoyId || "Unknown"

  // Format the date if available using our new formatter
  const formattedDate = swellData?.date ? formatDateTime(swellData.date) : "Unknown"

  // Extract swell components into an array for easier rendering
  const swellComponents = hasSwellData
    ? Object.entries(swellData!.swell_components)
        .filter(([_, component]) => component !== undefined)
        .map(([key, component]) => ({
          name: key.replace("_", " ").toUpperCase(),
          ...component,
        }))
    : []

  return (
    <div className="space-y-4">
      {hasSwellData ? (
        <div className="rounded-md border border-border/30 overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow className="bg-background/20 hover:bg-background/30">
                <TableHead>Component</TableHead>
                <TableHead>Height (ft)</TableHead>
                <TableHead>Period (sec)</TableHead>
                <TableHead>Direction (°)</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {swellComponents.map((component, index) => (
                <TableRow key={index} className="hover:bg-background/20">
                  <TableCell className="font-medium">{component.name}</TableCell>
                  <TableCell>{component.height.toFixed(2)}</TableCell>
                  <TableCell>{component.period.toFixed(2)}</TableCell>
                  <TableCell>{component.direction}°</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      ) : (
        <div className="flex items-center gap-2 text-muted-foreground py-4">
          <AlertCircle className="h-4 w-4" />
          <p>No swell data available for this session.</p>
        </div>
      )}
    </div>
  )
}
