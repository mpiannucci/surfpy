"use client"

import { useState, useEffect } from "react"
import { DayNavigator } from "./day-navigator"
import { SwellChart } from "./swell-chart"
import { SwellDetailTile } from "./swell-detail-tile"
import { TideChart } from "./tide-chart"
import { WindBarChart } from "./wind-bar-chart"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"
import { getAuthToken } from "@/lib/auth"
import { addDays, startOfDay, isSameDay, getHours } from "date-fns"
import { useIsMobile } from "@/hooks/use-mobile"

import { ClientSessionsByLocation } from "./client-sessions-by-location"

// Types need to be defined here or imported
interface ForecastEntry {
  timestamp: string
  breaking_wave_height: { max: number; range_text: string; unit: string }
  swell_components: any[]
  tide: { height: number; unit: string }
  wind: { speed: number; direction: string; direction_degrees: number; unit: string }
}

interface ForecastApiResponse {
  data: {
    forecast_data: ForecastEntry[]
    timezone: string // Add timezone to the API response interface
  }
}

interface ForecastDashboardV2Props {
  location: string
  onBack: () => void
}

export function ForecastDashboardV2({ location, onBack }: ForecastDashboardV2Props) {
  const [allForecastData, setAllForecastData] = useState<ForecastEntry[]>([])
  const [currentDayIndex, setCurrentDayIndex] = useState(0)
  const [hoveredHourData, setHoveredHourData] = useState<ForecastEntry | null>(null)
  const [surfSpotTimezone, setSurfSpotTimezone] = useState<string | null>(null) // New state for timezone
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const isMobile = useIsMobile();

  useEffect(() => {
    const fetchForecast = async () => {
      setIsLoading(true)
      setError(null)
      try {
        const authToken = getAuthToken()
        if (!authToken) throw new Error("Authentication required.")

        const response = await fetch("/api/auth/cors-proxy", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            url: `https://surfdata-martins-projects-383d438b.vercel.app/api/forecast/${location}`,
            method: "GET",
            headers: { Authorization: `Bearer ${authToken}` },
          }),
        })

        if (!response.ok) throw new Error("Failed to fetch forecast data.")

        const result: ForecastApiResponse = await response.json()
        if (result.data && result.data.forecast_data) {
          setAllForecastData(result.data.forecast_data)
          setSurfSpotTimezone(result.data.timezone) // Set the timezone
          // Set initial hovered data to the current hour of the first day
          const now = new Date()
          const currentHour = getHours(now)
          const todayData = result.data.forecast_data.filter(d => isSameDay(new Date(d.timestamp), now))
          setHoveredHourData(todayData[currentHour] || todayData[0] || null)
        } else {
          throw new Error("Invalid forecast data format.")
        }
      } catch (err: any) {
        setError(err.message)
      } finally {
        setIsLoading(false)
      }
    }

    fetchForecast()
  }, [location])

  const handleDayChange = (direction: number) => {
    setCurrentDayIndex(prev => {
      const newIndex = prev + direction
      if (newIndex >= 0 && newIndex < 7) {
        return newIndex
      } 
      return prev
    })
  }

  const handleHourHover = (hourData: ForecastEntry | null) => {
    setHoveredHourData(hourData)
  }

  const dailyForecastData = allForecastData.filter(d => 
    isSameDay(new Date(d.timestamp), addDays(startOfDay(new Date()), currentDayIndex))
  )

  if (isLoading) {
    return <div>Loading...</div>
  }

  if (error) {
    return <Alert variant="destructive">
      <AlertTitle>Error</AlertTitle>
      <AlertDescription>{error}</AlertDescription>
    </Alert>
  }

  return (
    <div className="space-y-6 p-4">
      <h1 className="text-3xl font-bold tracking-tight capitalize">{location.replace("-", " ")} Forecast</h1>
      <DayNavigator 
        currentDayIndex={currentDayIndex} 
        onDayChange={handleDayChange} 
      />
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Swell Chart - order 1 on mobile, col-span-2 on large */}
        <div className="order-1 lg:col-span-2">
          <SwellChart dailyData={dailyForecastData} onHourHover={handleHourHover} isMobile={isMobile} />
        </div>

        {/* Swell Detail Tile - order 2 on mobile, col-span-1 on large */}
        <div className="order-2 lg:col-span-1">
          <SwellDetailTile hourData={hoveredHourData} surfSpotTimezone={surfSpotTimezone} isMobile={isMobile} />
        </div>

        {/* Tide Chart - order 3 on mobile, col-span-2 on large */}
        <div className="order-3 lg:col-span-2">
          <TideChart dailyData={dailyForecastData} />
        </div>
        {/* Wind Chart - order 4 on mobile, col-span-2 on large */}
        <div className="order-4 lg:col-span-2">
          <WindBarChart dailyData={dailyForecastData} />
        </div>
      </div>

      {/* <div className="mt-8">
        <ClientSessionsByLocation location={location} />
      </div> */}
    </div>
  )
}
