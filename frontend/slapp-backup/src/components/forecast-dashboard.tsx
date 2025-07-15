"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"
import { ArrowLeft, TrendingUp, Wind, Waves, Clock } from "lucide-react"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"
import { getAuthToken } from "@/lib/auth"

interface ForecastData {
  timestamp: string
  breaking_wave_height: {
    min: number
    max: number
    unit: string
  }
  swell_components: Array<{
    direction: string
    direction_degrees: number
    height: number
    period: number
    unit: string
  }>
  wind: {
    speed: number
    direction: string
    unit: string
  }
  tide: {
    height: number
    unit: string
  }
}

interface ForecastDashboardProps {
  location: string
  onBack: () => void
}

export function ForecastDashboard({ location, onBack }: ForecastDashboardProps) {
  const [forecastData, setForecastData] = useState<ForecastData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchForecast = async () => {
      try {
        setLoading(true)
        setError(null)

        console.log("Fetching forecast for location:", location)

        const authToken = getAuthToken()
        if (!authToken) {
          throw new Error("Authentication required. Please log in.")
        }

        const response = await fetch("/api/proxy", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            url: `https://surfdata-njfslt1w3-martins-projects-383d438b.vercel.app/api/forecast/${location}`,
            method: "GET",
            authToken: authToken,
          }),
        })

        if (!response.ok) {
          const errorText = await response.text()
          console.error("Proxy response error:", errorText)
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const result = await response.json()
        console.log("Forecast API result:", result)

        if (result && result.data && Array.isArray(result.data)) {
          setForecastData(result.data)
        } else {
          throw new Error("Invalid response format - no forecast data found")
        }
      } catch (err) {
        console.error("Failed to fetch forecast:", err)
        setError(err instanceof Error ? err.message : "Failed to load forecast data")
      } finally {
        setLoading(false)
      }
    }

    fetchForecast()
  }, [location])

  const formatDateTime = (timestamp: string) => {
    const date = new Date(timestamp)
    const dateStr = date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    })
    const timeStr = date.toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    })
    return { date: dateStr, time: timeStr }
  }

  const getDirectionArrow = (degrees: number) => {
    return `rotate(${degrees}deg)`
  }

  // Create chart data from forecast data
  const chartData = forecastData.map((item, index) => {
    const { date, time } = formatDateTime(item.timestamp)
    const waveHeight = Math.max(item.breaking_wave_height?.max || 0, item.breaking_wave_height?.min || 0)

    return {
      index,
      date,
      time,
      dateTime: `${date} ${time}`,
      waveHeight,
      originalData: item,
    }
  })

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload.originalData as ForecastData
      const { date, time } = formatDateTime(data.timestamp)

      // Filter out N/A swell components
      const validSwells =
        data.swell_components?.filter(
          (swell) => swell.direction !== "N/A" && swell.height !== undefined && swell.height !== null,
        ) || []

      return (
        <div className="bg-background border rounded-lg p-4 shadow-lg max-w-sm">
          <div className="font-semibold mb-3 text-center">
            <div>{date}</div>
            <div className="text-sm text-muted-foreground">{time}</div>
          </div>

          <div className="space-y-3 text-sm">
            <div className="flex items-center gap-2">
              <Waves className="h-4 w-4 text-blue-500" />
              <span>
                <strong>Wave Height:</strong> {data.breaking_wave_height?.min || 0} -{" "}
                {data.breaking_wave_height?.max || 0} {data.breaking_wave_height?.unit || "ft"}
              </span>
            </div>

            {validSwells.length > 0 && (
              <div>
                <div className="font-medium mb-2">Swell Components:</div>
                {validSwells.map((swell, index) => (
                  <div key={index} className="flex items-center gap-2 ml-2 mb-1">
                    <div
                      className="text-xs w-4 h-4 flex items-center justify-center"
                      style={{ transform: getDirectionArrow(swell.direction_degrees) }}
                    >
                      ↑
                    </div>
                    <span>
                      {swell.height} {swell.unit} @ {swell.period}s from {swell.direction}
                    </span>
                  </div>
                ))}
              </div>
            )}

            {data.wind?.direction !== "N/A" && (
              <div className="flex items-center gap-2">
                <Wind className="h-4 w-4 text-gray-500" />
                <span>
                  <strong>Wind:</strong> {data.wind?.speed || 0} {data.wind?.unit || "mph"} from{" "}
                  {data.wind?.direction || "N/A"}
                </span>
              </div>
            )}

            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-green-500" />
              <span>
                <strong>Tide:</strong> {data.tide?.height || 0} {data.tide?.unit || "ft"}
              </span>
            </div>
          </div>
        </div>
      )
    }
    return null
  }

  const CustomXAxisTick = ({ x, y, payload }: any) => {
    if (!payload || !chartData[payload.index]) return null

    const data = chartData[payload.index]
    return (
      <g transform={`translate(${x},${y})`}>
        <text x={0} y={0} dy={16} textAnchor="middle" fill="#666" fontSize="12">
          {data.date}
        </text>
        <text x={0} y={16} dy={16} textAnchor="middle" fill="#666" fontSize="10">
          {data.time}
        </text>
      </g>
    )
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="space-y-6">
          <div className="flex items-center gap-4">
            <Button variant="outline" size="sm" onClick={onBack}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
            <div>
              <Skeleton className="h-8 w-48 mb-2" />
              <Skeleton className="h-4 w-64" />
            </div>
          </div>

          <Card>
            <CardHeader>
              <Skeleton className="h-6 w-32" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-64 w-full" />
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="space-y-6">
          <div className="flex items-center gap-4">
            <Button variant="outline" size="sm" onClick={onBack}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
            <div>
              <h1 className="text-3xl font-bold tracking-tight capitalize">{location.replace("-", " ")} Forecast</h1>
            </div>
          </div>

          <Alert variant="destructive">
            <AlertDescription>Failed to load forecast data: {error}</AlertDescription>
          </Alert>
        </div>
      </div>
    )
  }

  if (forecastData.length === 0) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="space-y-6">
          <div className="flex items-center gap-4">
            <Button variant="outline" size="sm" onClick={onBack}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
            <div>
              <h1 className="text-3xl font-bold tracking-tight capitalize">{location.replace("-", " ")} Forecast</h1>
            </div>
          </div>

          <Alert>
            <AlertDescription>No forecast data available for this location.</AlertDescription>
          </Alert>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="sm" onClick={onBack}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight capitalize">{location.replace("-", " ")} Forecast</h1>
            <p className="text-muted-foreground">{forecastData.length} hour forecast</p>
          </div>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Wave Height Forecast
            </CardTitle>
            <CardDescription>Hover over data points for detailed swell information</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 80 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="index"
                    tick={<CustomXAxisTick />}
                    height={80}
                    interval={Math.max(0, Math.floor(chartData.length / 8))}
                  />
                  <YAxis
                    label={{ value: "Wave Height (ft)", angle: -90, position: "insideLeft" }}
                    domain={[0, "dataMax + 1"]}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Line
                    type="monotone"
                    dataKey="waveHeight"
                    stroke="#3b82f6"
                    strokeWidth={2}
                    dot={{ fill: "#3b82f6", strokeWidth: 2, r: 4 }}
                    activeDot={{ r: 6, stroke: "#3b82f6", strokeWidth: 2 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {forecastData.slice(0, 6).map((item, index) => {
            const { date, time } = formatDateTime(item.timestamp)
            const validSwells =
              item.swell_components?.filter(
                (swell) => swell.direction !== "N/A" && swell.height !== undefined && swell.height !== null,
              ) || []

            return (
              <Card key={index}>
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg">
                    <div>{date}</div>
                    <div className="text-sm font-normal text-muted-foreground">{time}</div>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center gap-2">
                    <Waves className="h-4 w-4 text-blue-500" />
                    <span className="text-sm">
                      {item.breaking_wave_height?.min || 0} - {item.breaking_wave_height?.max || 0}{" "}
                      {item.breaking_wave_height?.unit || "ft"}
                    </span>
                  </div>

                  {validSwells.length > 0 && (
                    <div className="space-y-1">
                      <div className="text-xs font-medium text-muted-foreground">Swells:</div>
                      {validSwells.slice(0, 2).map((swell, swellIndex) => (
                        <div key={swellIndex} className="flex items-center gap-2">
                          <div
                            className="text-xs w-3 h-3 flex items-center justify-center"
                            style={{ transform: getDirectionArrow(swell.direction_degrees) }}
                          >
                            ↑
                          </div>
                          <span className="text-xs">
                            {swell.height} {swell.unit} @ {swell.period}s {swell.direction}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}

                  {item.wind?.direction !== "N/A" && (
                    <div className="flex items-center gap-2">
                      <Wind className="h-4 w-4 text-gray-500" />
                      <span className="text-sm">
                        {item.wind?.speed || 0} {item.wind?.unit || "mph"} {item.wind?.direction || "N/A"}
                      </span>
                    </div>
                  )}

                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-green-500" />
                    <span className="text-sm">
                      Tide: {item.tide?.height || 0} {item.tide?.unit || "ft"}
                    </span>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>
    </div>
  )
}
