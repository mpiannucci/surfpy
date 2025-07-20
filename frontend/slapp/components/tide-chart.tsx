"use client"

import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface ForecastEntry {
  timestamp: string
  tide: { height: number; unit: string }
}

interface TideChartProps {
  dailyData: ForecastEntry[]
  sessionDate?: string
  sessionStartTime?: string
  sessionEndTime?: string
}

export function TideChart({ dailyData, sessionDate, sessionStartTime, sessionEndTime }: TideChartProps) {
  const formatXAxis = (tickItem: string) => {
    const date = new Date(tickItem)
    return date.toLocaleTimeString('en-US', { hour: 'numeric', hour12: true })
  }

  let formattedSessionStartTimestamp: string | undefined;
  let formattedSessionEndTimestamp: string | undefined;

  if (sessionDate && sessionStartTime && sessionEndTime) {
    const sessionStartDateTime = new Date(`${sessionDate}T${sessionStartTime}`);
    const sessionEndDateTime = new Date(`${sessionDate}T${sessionEndTime}`);

    formattedSessionStartTimestamp = sessionStartDateTime.toISOString().split('.')[0] + '+00:00';
    formattedSessionEndTimestamp = sessionEndDateTime.toISOString().split('.')[0] + '+00:00';
  }

  console.log('TideChart - dailyData timestamps (first 5):', dailyData.slice(0, 5).map(d => d.timestamp));
  console.log('TideChart - formattedSessionStartTimestamp:', formattedSessionStartTimestamp);
  console.log('TideChart - formattedSessionEndTimestamp:', formattedSessionEndTimestamp);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Tide</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={150}>
          <LineChart data={dailyData}>
            <XAxis dataKey="timestamp" tickFormatter={formatXAxis} />
            <YAxis hide={true} domain={[0, 7]} />
            <Tooltip content={<CustomTooltip />} />
            <Line type="monotone" dataKey="tide.height" stroke="#8884d8" dot={false} />
            {formattedSessionStartTimestamp && (
              <ReferenceLine x={formattedSessionStartTimestamp} stroke="#FF0000" label="Start" />
            )}
            {formattedSessionEndTimestamp && (
              <ReferenceLine x={formattedSessionEndTimestamp} stroke="#00FF00" label="End" />
            )}
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="p-2 bg-background border rounded-md shadow-lg">
        <p className="font-bold">{`${new Date(label).toLocaleTimeString('en-US', { hour: 'numeric', hour12: true })}`}</p>
        <p className="text-sm">{`Tide: ${payload[0].value.toFixed(1)} ft`}</p>
      </div>
    );
  }

  return null;
};