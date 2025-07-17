"use client"

import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface ForecastEntry {
  timestamp: string
  breaking_wave_height: { max: number; range_text: string; unit: string }
}

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
            console.log("SwellChart: Mouse moved, state:", state);
            // Check if activeIndex is available and valid
            if (state.activeIndex !== undefined && dailyData[state.activeIndex]) {
              const hoveredData = dailyData[state.activeIndex];
              console.log("SwellChart: Mouse moved, hoveredData from activeIndex:", hoveredData);
              onHourHover(hoveredData);
            } else {
              // If no activeIndex or data, set to null
              onHourHover(null);
            }
          }} onMouseLeave={() => {
            console.log("SwellChart: Mouse left chart, setting hoveredData to null");
            onHourHover(null);
          }}>
            <XAxis dataKey="timestamp" tickFormatter={formatXAxis} interval={2} />
            <YAxis label={{ value: 'Height (ft)', angle: -90, position: 'insideLeft' }} domain={[0, 10]} />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="breaking_wave_height.max" fill="#3b82f6">
              {dailyData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={index % 2 === 0 ? '#3b82f6' : '#60a5fa'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

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