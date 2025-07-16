"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ArrowLeft, Waves, Wind, Clock, CalendarDays, Star, NotebookPen } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"
import { getAuthToken } from "@/lib/auth"
import { format } from "date-fns"

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

  const formatSwellComponent = (swell?: SessionSwellComponent) => {
    if (!swell) return "N/A"
    return `${swell.height?.toFixed(1)}ft @ ${swell.period?.toFixed(1)}s from ${swell.direction}°`
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
            <h1 className="text-3xl font-bold tracking-tight capitalize">{capitalizeLocation(location)} Forecast</h1>
            <p className="text-muted-foreground">Detailed forecast and recent sessions</p>
          </div>
        </div>

        {/* Forecast Section */}
        <section>
          <h2 className="text-2xl font-bold tracking-tight mb-4">Hourly Forecast</h2>
          {forecastError && (
            <Alert variant="destructive" className="mb-4">
              <AlertTitle>Forecast Error</AlertTitle>
              <AlertDescription>{forecastError}</AlertDescription>
            </Alert>
          )}
          {isLoadingForecast ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {[...Array(6)].map((_, i) => (
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
          ) : forecastData && forecastData.data.forecast_data.length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {forecastData.data.forecast_data.map((entry, index) => (
                <Card key={index}>
                  <CardHeader>
                    <CardTitle className="text-lg">{formatTimestamp(entry.timestamp)}</CardTitle>
                    <CardDescription>Type: {entry.type}</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-2 text-sm">
                    <div className="flex items-center gap-2">
                      <Waves className="h-4 w-4 text-blue-500" />
                      <span>Wave Height: {entry.breaking_wave_height.min.toFixed(1)} - {entry.breaking_wave_height.max.toFixed(1)} {entry.breaking_wave_height.unit}</span>
                    </div>
                    {entry.swell_components && entry.swell_components.length > 0 && (
                      <div className="space-y-1">
                        <p className="font-medium">Swells:</p>
                        {entry.swell_components.map((swell, sIdx) => (
                          <div key={sIdx} className="flex items-center gap-2 ml-2">
                            <Waves className="h-3 w-3" />
                            <span>{swell.height.toFixed(1)}{swell.unit} @ {swell.period.toFixed(1)}s from {swell.direction} ({swell.direction_degrees}°)</span>
                          </div>
                        ))}
                      </div>
                    )}
                    <div className="flex items-center gap-2">
                      <Wind className="h-4 w-4 text-gray-500" />
                      <span>Wind: {entry.wind.speed.toFixed(1)}{entry.wind.unit} from {entry.wind.direction}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4 text-green-500" />
                      <span>Tide: {entry.tide.height.toFixed(2)}{entry.tide.unit}</span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Alert>
              <AlertTitle>No Forecast Data</AlertTitle>
              <AlertDescription>No hourly forecast data available for this location.</AlertDescription>
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
                          <span>{formatSwellComponent(session.raw_swell[0].swell_components.swell_1)}</span>
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