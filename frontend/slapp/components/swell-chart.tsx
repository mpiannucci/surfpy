"use client"

import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, Legend } from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface ForecastEntry {
  timestamp: string
  breaking_wave_height: { max: number; range_text: string; unit: string }
  type?: string // Add the type property
}

const ACTUAL_COLOR = "#009FB7";
const FORECAST_COLOR = "#E6E6EA";
const DEFAULT_COLOR = "grey";

interface SwellChartProps {
  dailyData: ForecastEntry[]
  onHourHover: (data: ForecastEntry | null) => void
}

export function SwellChart({ dailyData, onHourHover }: SwellChartProps) {
  const formatXAxis = (tickItem: string) => {
    const date = new Date(tickItem)
    return date.toLocaleTimeString('en-US', { hour: 'numeric', hour12: true })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Breaking Wave Height</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={dailyData} onMouseMove={(state) => {
            // Check if activeIndex is available and valid
            if (state.activeIndex !== undefined && dailyData[state.activeIndex]) {
              const hoveredData = dailyData[state.activeIndex];
              onHourHover(hoveredData);
            } else {
              // If no activeIndex or data, set to null
              onHourHover(null);
            }
          }} onMouseLeave={() => {
            onHourHover(null);
          }}>
            <XAxis dataKey="timestamp" tickFormatter={formatXAxis} />
            <YAxis hide={true} domain={[0, 12]} label={{ value: 'Height (ft)', angle: -90, position: 'insideLeft' }} width={30} />
            
            <Tooltip content={<CustomTooltip />} />
            <Legend content={<CustomChartLegend />} />
            <Bar dataKey="breaking_wave_height.max">
              {dailyData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.type === "actual" ? ACTUAL_COLOR : (entry.type === "forecast" ? FORECAST_COLOR : DEFAULT_COLOR)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

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

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    const rangeText = payload[0].payload.breaking_wave_height.range_text;
    return (
      <div className="p-2 bg-background border rounded-md shadow-lg">
        <p className="font-bold">{`${new Date(label).toLocaleTimeString('en-US', { hour: 'numeric', hour12: true })}`}</p>
        <p className="text-sm">{`Wave Height: ${rangeText}`}</p>
      </div>
    );
  }

  return null;
};