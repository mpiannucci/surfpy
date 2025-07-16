"use client"

import { useState, useEffect, useRef } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ArrowLeft, Waves, Wind, Clock, CalendarDays, Star, NotebookPen, ArrowUpRight } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"
import { getAuthToken } from "@/lib/auth"
import { format, addDays, startOfDay, isSameDay } from "date-fns"
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, LineChart, Line, CartesianGrid, ReferenceLine, ReferenceArea } from "recharts"

// Define types for the new API responses
interface BreakingWaveHeight {
  max: number
  min: number
  unit: string
}

interface SwellComponent {
  direction: string
  direction_degrees: number
  height: number
  period: number
  unit: string
}

interface Tide {
  height: number
  unit: string
}

interface Wind {
  direction: string
  speed: number
  unit: string
}

interface ForecastEntry {
  breaking_wave_height: BreakingWaveHeight
  swell_components: SwellComponent[]
  tide: Tide
  timestamp: string
  type: string
  wind: Wind
}

interface ForecastData {
  forecast_data: ForecastEntry[]
  forecast_generated_at: string
  timezone: string
}

interface ForecastApiResponse {
  data: ForecastData
  status: string
}

interface SessionSwellComponent {
  direction: number
  height: number
  period: number
}

interface SessionRawSwellEntry {
  date: string
  swell_components: {
    swell_1?: SessionSwellComponent
    swell_2?: SessionSwellComponent
    swell_3?: SessionSwellComponent
    swell_4?: SessionSwellComponent
  }
}

interface SurfSession {
  id: number
  session_name: string
  display_name: string
  date: string
  time: string
  end_time: string
  fun_rating: string
  session_notes: string
  participants: any[] // Adjust if participants structure is known
  location: string
  raw_swell?: SessionRawSwellEntry[] // Optional, as not all sessions might have it
}

interface SessionsApiResponse {
  data: SurfSession[]
  status: string
}

interface NewForecastDashboardProps {
  location: string
  onBack: () => void
}

const NEW_API_BASE_URL = "https://surfdata-4kuzgt1ku-martins-projects-383d438b.vercel.app"

export function NewForecastDashboard({ location, onBack }: NewForecastDashboardProps) {
  const [forecastData, setForecastData] = useState<ForecastApiResponse | null>(null)
  const [sessionsData, setSessionsData] = useState<SessionsApiResponse | null>(null)
  const [isLoadingForecast, setIsLoadingForecast] = useState(true)
  const [isLoadingSessions, setIsLoadingSessions] = useState(true)
  const [forecastError, setForecastError] = useState<string | null>(null)
  const [sessionsError, setSessionsError] = useState<string | null>(null)

  const [hoveredForecastEntry, setHoveredForecastEntry] = useState<ForecastEntry | null>(null)
  const [activeForecastEntry, setActiveForecastEntry] = useState<ForecastEntry | null>(null)

  useEffect(() => {
    const fetchForecast = async () => {
      setIsLoadingForecast(true)
      setForecastError(null)
      try {
        const authToken = getAuthToken()
        if (!authToken) {
          throw new Error("Authentication token not found for forecast.")
        }

        const response = await fetch("/api/auth/cors-proxy", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            url: `${NEW_API_BASE_URL}/api/forecast/${location}`,
            method: "GET",
            headers: {
              Authorization: `Bearer ${authToken}`,
            },
          }),
        })

        if (!response.ok) {
          const errorBody = await response.text()
          throw new Error(`Failed to fetch forecast: ${response.status} - ${errorBody}`)
        }

        const data: ForecastApiResponse = await response.json()
        if (data.status === "success") {
          setForecastData(data)
          // Set the first entry as the default for dynamic tiles
          if (data.data.forecast_data.length > 0) {
            setHoveredForecastEntry(data.data.forecast_data[0])
          }
        } else {
          throw new Error(data.status || "Unknown error fetching forecast.")
        }
      } catch (err: any) {
        console.error("Error fetching forecast:", err)
        setForecastError(err.message || "Failed to load forecast data.")
      } finally {
        setIsLoadingForecast(false)
      }
    }

    const fetchSessions = async () => {
      setIsLoadingSessions(true)
      setSessionsError(null)
      try {
        const authToken = getAuthToken()
        if (!authToken) {
          throw new Error("Authentication token not found for sessions.")
        }

        const response = await fetch("/api/auth/cors-proxy", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            url: `${NEW_API_BASE_URL}/api/surf-sessions/location/${location}`,
            method: "GET",
            headers: {
              Authorization: `Bearer ${authToken}`,
            },
          }),
        })

        if (!response.ok) {
          const errorBody = await response.text()
          throw new Error(`Failed to fetch sessions: ${response.status} - ${errorBody}`)
        }

        const data: SessionsApiResponse = await response.json()
        if (data.status === "success") {
          setSessionsData(data)
        } else {
          throw new Error(data.status || "Unknown error fetching sessions.")
        }
      } catch (err: any) {
        console.error("Error fetching sessions:", err)
        setSessionsError(err.message || "Failed to load sessions data.")
      } finally {
        setIsLoadingSessions(false)
      }
    }

    fetchForecast()
    fetchSessions()
  }, [location])

  const capitalizeLocation = (loc: string) => {
    return loc.split("-").map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(" ")
  }

  const formatTimestamp = (timestamp: string) => {
    return format(new Date(timestamp), "MMM d, h a")
  }

  const getAverageWaveHeight = (entry: ForecastEntry) => {
    return (entry.breaking_wave_height.min + entry.breaking_wave_height.max) / 2
  }

  const getDirectionArrowStyle = (degrees: number) => {
    return { transform: `rotate(${degrees}deg)` }
  }

  // Filter forecast data for 3 days
  const filteredForecastData = forecastData?.data.forecast_data.filter(entry => {
    const entryDate = new Date(entry.timestamp);
    const today = startOfDay(new Date());
    const threeDaysFromNow = addDays(today, 3);
    return entryDate >= today && entryDate < threeDaysFromNow;
  }) || [];

  // Prepare data for chart X-axis day delineation and labels
  const dayMarkers: { timestamp: number; label: string; color: string; isNewDay: boolean }[] = [];
  let lastDay: Date | null = null;
  let dayCount = 0;

  filteredForecastData.forEach((entry, index) => {
    const currentDate = startOfDay(new Date(entry.timestamp));
    if (!lastDay || !isSameDay(currentDate, lastDay)) {
      dayCount++;
      let label = "";
      if (isSameDay(currentDate, startOfDay(new Date()))) {
        label = "Today";
      } else if (isSameDay(currentDate, addDays(startOfDay(new Date()), 1))) {
        label = "Tomorrow";
      } else {
        label = format(currentDate, "EEEE, MMM d");
      }
      dayMarkers.push({
        timestamp: new Date(entry.timestamp).getTime(),
        label: label,
        color: dayCount % 2 === 0 ? "#f0f9ff" : "#e0f2fe", // Alternating light blue shades
        isNewDay: true,
      });
      lastDay = currentDate;
    } else {
      dayMarkers.push({
        timestamp: new Date(entry.timestamp).getTime(),
        label: "",
        color: dayCount % 2 === 0 ? "#f0f9ff" : "#e0f2fe",
        isNewDay: false,
      });
    }
  });

  const CustomXAxisTick = (props: any) => {
    const { x, y, payload } = props;
    const marker = dayMarkers.find(m => m.timestamp === payload.value);

    if (marker && marker.isNewDay) {
      return (
        <g transform={`translate(${x},${y})`}>
          <text x={0} y={0} dy={16} textAnchor="middle" fill="#666" fontSize="12">
            {format(new Date(payload.value), "h a")}
          </text>
          <text x={0} y={-10} textAnchor="middle" fill="#333" fontWeight="bold" fontSize="14">
            {marker.label}
          </text>
        </g>
      );
    }
    return (
      <g transform={`translate(${x},${y})`}>
        <text x={0} y={0} dy={16} textAnchor="middle" fill="#666" fontSize="12">
          {format(new Date(payload.value), "h a")}
        </text>
      </g>
    );
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const entry = payload[0].payload as ForecastEntry;
      return (
        <Card className="shadow-lg max-w-sm overflow-y-auto max-h-[300px]">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">{formatTimestamp(entry.timestamp)}</CardTitle>
            <CardDescription>
              Wave Height: {entry.breaking_wave_height.min.toFixed(1)} - {entry.breaking_wave_height.max.toFixed(1)} {entry.breaking_wave_height.unit}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="space-y-1">
              <p className="font-semibold">Swell Components:</p>
              {entry.swell_components && entry.swell_components.length > 0 ? (
                entry.swell_components.map((swell, sIdx) => (
                  <div key={sIdx} className="flex items-center gap-2 ml-2">
                    <ArrowUpRight style={getDirectionArrowStyle(swell.direction_degrees)} className="h-4 w-4 text-blue-500" />
                    <span>{swell.height.toFixed(1)}{swell.unit} @ {swell.period.toFixed(1)}s from {swell.direction} ({swell.direction_degrees}°)</span>
                  </div>
                ))
              ) : (
                <p className="text-muted-foreground ml-2">No swell data available.</p>
              )}
            </div>
            <div className="space-y-1">
              <p className="font-semibold">Wind Conditions:</p>
              {entry.wind ? (
                <div className="flex items-center gap-2 ml-2">
                  <ArrowUpRight style={getDirectionArrowStyle(entry.wind.direction_degrees || 0)} className="h-4 w-4 text-gray-500" />
                  <span>{entry.wind.speed.toFixed(1)}{entry.wind.unit} from {entry.wind.direction}</span>
                </div>
              ) : (
                <p className="text-muted-foreground ml-2">No wind data available.</p>
              )}
            </div>
          </CardContent>
        </Card>
      );
    }
    return null;
  };

  const handleChartMouseMove = (state: any) => {
    if (state.isTooltipActive && state.activePayload && state.activePayload.length > 0) {
      setActiveForecastEntry(state.activePayload[0].payload);
      setHoveredForecastEntry(state.activePayload[0].payload);
    } else {
      // This else block is intentionally left empty to maintain the sticky behavior
      // setActiveForecastEntry(null); // Do NOT uncomment this for sticky behavior
    }
  };

  const handleChartMouseLeave = () => {
    setActiveForecastEntry(null);
  };

  const currentDisplayEntry = hoveredForecastEntry;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="sm" onClick={onBack}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight capitalize">{capitalizeLocation(location)} Forecast</h1>
            {forecastData?.data?.forecast_generated_at && (
              <p className="text-muted-foreground text-sm">
                Forecast generated: {format(new Date(forecastData.data.forecast_generated_at), "MMM d, yyyy h:mm a z")}
              </p>
            )}
          </div>
        </div>

        {/* Wave Height Forecast Section */}
        <section>
          <h2 className="text-2xl font-bold tracking-tight mb-4">Wave Height Forecast</h2>
          {forecastError && (
            <Alert variant="destructive" className="mb-4">
              <AlertTitle>Forecast Error</AlertTitle>
              <AlertDescription>{forecastError}</AlertDescription>
            </Alert>
          )}
          {isLoadingForecast ? (
            <Skeleton className="h-64 w-full" />
          ) : filteredForecastData.length > 0 ? (
            <div className="space-y-4">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart
                  data={filteredForecastData}
                  margin={{
                    top: 5,
                    right: 30,
                    left: 20,
                    bottom: 5,
                  }}
                  onMouseMove={handleChartMouseMove}
                  onMouseLeave={handleChartMouseLeave}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey={(data) => new Date(data.timestamp).getTime()}
                    tick={CustomXAxisTick}
                    minTickGap={20}
                    scale="time"
                    type="number"
                    domain={[
                      new Date(filteredForecastData[0].timestamp).getTime(),
                      new Date(filteredForecastData[filteredForecastData.length - 1].timestamp).getTime(),
                    ]}
                  />
                  <YAxis label={{ value: 'Wave Height (ft)', angle: -90, position: 'insideLeft' }} />
                  <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(0,0,0,0.1)' }} />
                  <Bar dataKey={getAverageWaveHeight} fill="#3b82f6" />

                  {dayMarkers.filter(marker => marker.isNewDay).map((marker, index) => (
                    <ReferenceLine key={`line-${index}`} x={marker.timestamp} stroke="#ccc" strokeDasharray="3 3" />
                  ))}
                  {dayMarkers.map((marker, index) => {
                    if (marker.isNewDay && index < dayMarkers.length -1) {
                      const nextDayMarker = dayMarkers[index + 1] || filteredForecastData[filteredForecastData.length -1];
                      const x1 = marker.timestamp;
                      const x2 = nextDayMarker.timestamp || new Date(filteredForecastData[filteredForecastData.length -1].timestamp).getTime();
                      return (
                        <ReferenceArea
                          key={`area-${index}`}
                          x1={x1}
                          x2={x2}
                          fill={marker.color}
                          fillOpacity={0.2}
                          ifOverflow="extendDomain"
                        />
                      );
                    } else if (marker.isNewDay && index === dayMarkers.length -1) {
                       // Handle the last day's background if it's a new day marker
                       const x1 = marker.timestamp;
                       const x2 = new Date(filteredForecastData[filteredForecastData.length -1].timestamp).getTime();
                       return (
                        <ReferenceArea
                          key={`area-${index}`}
                          x1={x1}
                          x2={x2}
                          fill={marker.color}
                          fillOpacity={0.2}
                          ifOverflow="extendDomain"
                        />
                      );
                    }
                    return null;
                  })}
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <Alert>
              <AlertTitle>No Forecast Data</AlertTitle>
              <AlertDescription>No hourly forecast data available for this location.</AlertDescription>
            </Alert>
          )}
        </section>

        {/* Tide Forecast Section */}
        <section>
          <h2 className="text-2xl font-bold tracking-tight mb-4">Tide Forecast</h2>
          {forecastError && (
            <Alert variant="destructive" className="mb-4">
              <AlertTitle>Tide Forecast Error</AlertTitle>
              <AlertDescription>{forecastError}</AlertDescription>
            </Alert>
          )}
          {isLoadingForecast ? (
            <Skeleton className="h-64 w-full" />
          ) : filteredForecastData.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <LineChart
                data={filteredForecastData}
                margin={{
                  top: 5,
                  right: 30,
                  left: 20,
                  bottom: 5,
                }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey={(data) => new Date(data.timestamp).getTime()}
                  tick={CustomXAxisTick}
                  minTickGap={20}
                  scale="time"
                  type="number"
                  domain={[
                    new Date(filteredForecastData[0].timestamp).getTime(),
                    new Date(filteredForecastData[filteredForecastData.length - 1].timestamp).getTime(),
                  ]}
                />
                <YAxis label={{ value: 'Tide Height (ft)', angle: -90, position: 'insideLeft' }} />
                <Tooltip formatter={(value: number) => [`${value.toFixed(2)} ft`, 'Tide Height']} />
                <Line type="monotone" dataKey="tide.height" stroke="#8884d8" activeDot={{ r: 8 }} />

                {dayMarkers.filter(marker => marker.isNewDay).map((marker, index) => (
                    <ReferenceLine key={`line-${index}`} x={marker.timestamp} stroke="#ccc" strokeDasharray="3 3" />
                  ))}
                  {dayMarkers.map((marker, index) => {
                    if (marker.isNewDay && index < dayMarkers.length -1) {
                      const nextDayMarker = dayMarkers[index + 1] || filteredForecastData[filteredForecastData.length -1];
                      const x1 = marker.timestamp;
                      const x2 = nextDayMarker.timestamp || new Date(filteredForecastData[filteredForecastData.length -1].timestamp).getTime();
                      return (
                        <ReferenceArea
                          key={`area-${index}`}
                          x1={x1}
                          x2={x2}
                          fill={marker.color}
                          fillOpacity={0.2}
                          ifOverflow="extendDomain"
                        />
                      );
                    } else if (marker.isNewDay && index === dayMarkers.length -1) {
                       const x1 = marker.timestamp;
                       const x2 = new Date(filteredForecastData[filteredForecastData.length -1].timestamp).getTime();
                       return (
                        <ReferenceArea
                          key={`area-${index}`}
                          x1={x1}
                          x2={x2}
                          fill={marker.color}
                          fillOpacity={0.2}
                          ifOverflow="extendDomain"
                        />
                      );
                    }
                    return null;
                  })}
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <Alert>
              <AlertTitle>No Tide Data</AlertTitle>
              <AlertDescription>No tide forecast data available for this location.</AlertDescription>
            </Alert>
          )}
        </section>

        {/* Recent Sessions Section */}
        <section>
          <h2 className="text-2xl font-bold tracking-tight mb-4">Recent Sessions</h2>
          {sessionsError && (
            <Alert variant="destructive" className="mb-4">
              <AlertTitle>Sessions Error</AlertTitle>
              <AlertDescription>{sessionsError}</AlertDescription>
            </Alert>
          )}
          {isLoadingSessions ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {[...Array(3)].map((_, i) => (
                <Card key={i}>
                  <CardHeader>
                    <Skeleton className="h-6 w-3/4" />
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-4 w-5/6" />
                    <Skeleton className="h-4 w-2/3" />
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : sessionsData && sessionsData.data.length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {sessionsData.data.map((session) => (
                <Card key={session.id}>
                  <CardHeader>
                    <CardTitle className="text-lg">{session.session_name}</CardTitle>
                    <CardDescription>by {session.display_name || "Unknown User"}</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-2 text-sm">
                    <div className="flex items-center gap-2">
                      <CalendarDays className="h-4 w-4 text-muted-foreground" />
                      <span>{format(new Date(session.date), "MMM d, yyyy")}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Star className="h-4 w-4 text-yellow-500" />
                      <span>Fun Rating: {session.fun_rating}/10</span>
                    </div>
                    {session.session_notes && (
                      <div className="flex items-start gap-2">
                        <NotebookPen className="h-4 w-4 text-muted-foreground mt-1" />
                        <p className="flex-1 line-clamp-3">{session.session_notes}</p>
                      </div>
                    )}
                    {session.raw_swell && session.raw_swell.length > 0 && session.raw_swell[0].swell_components && (
                      <div className="space-y-1">
                        <p className="font-medium">Main Swell:</p>
                        <div className="flex items-center gap-2 ml-2">
                          <Waves className="h-3 w-3" />
                          <span>
                            {session.raw_swell[0].swell_components.swell_1?.height?.toFixed(1)}ft @ 
                            {session.raw_swell[0].swell_components.swell_1?.period?.toFixed(1)}s from 
                            {session.raw_swell[0].swell_components.swell_1?.direction}°
                          </span>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Alert>
              <AlertTitle>No Sessions Data</AlertTitle>
              <AlertDescription>No recent surf sessions available for this location.</AlertDescription>
            </Alert>
          )}
        </section>
      </div>
    </div>
  )
}