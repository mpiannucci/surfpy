"use client"

import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowUp } from "lucide-react"

// Types need to be defined here or imported
interface ForecastEntry {
  timestamp: string
  wind: { speed: number; direction: string; direction_degrees: number; unit: string }
  type?: string // Add the type property
}

interface WindBarChartProps {
  dailyData: ForecastEntry[]
}

const ACTUAL_COLOR = "#009FB7";
const FORECAST_COLOR = "#E6E6EA";
const DEFAULT_COLOR = "grey";

// Helper to get cardinal direction from degrees
const getCardinalDirection = (degrees: number): string => {
  const directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"];
  const index = Math.round(degrees / 22.5) % 16;
  return directions[index];
};

// Custom Bar component to include the arrow
const CustomWindBar = (props: any) => {
  const { x, y, width, height, payload } = props;
  const windDirectionDegrees = payload.wind.direction_degrees;

  const barColor = payload.type === "actual" ? ACTUAL_COLOR : (payload.type === "forecast" ? FORECAST_COLOR : DEFAULT_COLOR);

  // Calculate rotation: 0 degrees is North (up), 90 East, 180 South, 270 West
  // Lucide-react ArrowUp points upwards (North), so we just rotate by the wind direction
  const rotation = (windDirectionDegrees + 180) % 360; 

  return (
    <g>
      <rect x={x} y={y} width={width} height={height} fill={barColor} /> {/* Bar color */}
      {payload.wind.speed > 0 && ( // Only show arrow if there's wind
        <g transform={`translate(${x + width / 2}, ${y + height / 2}) rotate(${rotation}) translate(-${width / 2}, -${height / 2})`}>
          <ArrowUp 
            x={width / 2 - 8} // Center the arrow horizontally
            y={height / 2 - 8} // Center the arrow vertically
            size={16} 
            color="#333" // Arrow color
          />
        </g>
      )}
    </g>
  );
};

// Custom Tooltip component
const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    const windData = payload[0].payload.wind;
    return (
      <div className="p-2 bg-background border rounded-md shadow-lg">
        <p className="font-bold">{`${new Date(label).toLocaleTimeString('en-US', { hour: 'numeric', hour12: true })}`}</p>
        <p className="text-sm">{`Wind Speed: ${windData.speed} ${windData.unit}`}</p>
        <p className="text-sm">{`Wind Direction: ${windData.direction_degrees}° ${getCardinalDirection(windData.direction_degrees)}`}</p>
      </div>
    );
  }
  return null;
};

const CustomChartLegend = (props: any) => {
  const { payload } = props;

  return (
    <ul className="flex justify-center gap-4 mt-4">
      <li className="flex items-center gap-1">
        <span className="w-3 h-3 inline-block rounded-full" style={{ backgroundColor: ACTUAL_COLOR }}></span>
        <span>Actual</span>
      </li>
      <li className="flex items-center gap-1">
        <span className="w-3 h-3 inline-block rounded-full" style={{ backgroundColor: FORECAST_COLOR }}></span>
        <span>Forecast</span>
      </li>
    </ul>
  );
};

export function WindBarChart({ dailyData }: WindBarChartProps) {
  const formatXAxis = (tickItem: string) => {
    const date = new Date(tickItem)
    return date.toLocaleTimeString('en-US', { hour: 'numeric', hour12: true })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Wind</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={150}>
          <BarChart data={dailyData}>
            <XAxis dataKey="timestamp" tickFormatter={formatXAxis} />
            <YAxis hide={true} domain={[0, 20]} />
            <Tooltip content={<CustomTooltip />} />
            <Legend content={<CustomChartLegend />} />
            <Bar dataKey="wind.speed" shape={<CustomWindBar />} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
