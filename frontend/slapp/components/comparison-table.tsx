"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import type { SurfSession } from "@/lib/types"
import { formatDate, formatTime } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { ChevronDown, ChevronUp, ArrowUpDown, Mail, Waves, Wind } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { AlertCircle, Loader2 } from "lucide-react"

type SortField =
  | "date"
  | "start_time"
  | "end_time"
  | "location"
  | "session_name"
  | "fun_rating"
  | "display_name"
  | "swell1_height"
  | "swell1_period"
  | "swell1_direction"
  | "swell2_height"
  | "swell2_period"
  | "swell2_direction"
  | "swell3_height"
  | "swell3_period"
  | "swell3_direction"
  | "swell4_height"
  | "swell4_period"
  | "swell4_direction"
  | "wind_speed"
  | "wind_direction"
  | "tide_water_level"

type SortDirection = "asc" | "desc"

export function ComparisonTable() {
  const [sessions, setSessions] = useState<SurfSession[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [retryCount, setRetryCount] = useState(0)
  const [sortField, setSortField] = useState<SortField>("date")
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc")
  const [locationFilter, setLocationFilter] = useState<string>("")
  const [dateFilter, setDateFilter] = useState<string>("")
  const [userFilter, setUserFilter] = useState<string>("")
  const [swell1DirectionFilter, setSwell1DirectionFilter] = useState<string>("")
  const [swell1HeightFilter, setSwell1HeightFilter] = useState<string>("")
  const [swell1PeriodFilter, setSwell1PeriodFilter] = useState<string>("")

  useEffect(() => {
    async function fetchSessions() {
      try {
        setIsLoading(true)
        setError(null)

        // Get auth token
        const token = localStorage.getItem("auth_token")
        if (!token) {
          setError("No authentication token found")
          setIsLoading(false)
          return
        }

        // API URL - Updated to use the new backend URL
        const apiUrl = "https://surfdata-dyoiv3qio-martins-projects-383d438b.vercel.app/api/surf-sessions"

        // Try with proxy first
        try {
          console.log("ComparisonTable - Attempting fetch with proxy")
          const proxyResponse = await fetch("/api/auth/cors-proxy", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              url: apiUrl,
              method: "GET",
              headers: {
                Authorization: `Bearer ${token}`,
              },
            }),
            signal: AbortSignal.timeout(15000), // 15 seconds timeout
          })

          if (!proxyResponse.ok) {
            throw new Error(`Proxy request failed: ${proxyResponse.status} ${proxyResponse.statusText}`)
          }

          const responseText = await proxyResponse.text()
          console.log("ComparisonTable - Raw proxy response (first 200 chars):", responseText.substring(0, 200))

          // Parse the JSON
          const proxyData = JSON.parse(responseText)
          console.log("ComparisonTable - Proxy data received:", proxyData)

          processResponse(proxyData)
        } catch (proxyError) {
          console.error("ComparisonTable - Proxy fetch failed:", proxyError)

          // Try direct fetch as fallback
          try {
            console.log("ComparisonTable - Attempting direct fetch")
            const response = await fetch(apiUrl, {
              method: "GET",
              headers: {
                "Content-Type": "application/json",
                Accept: "application/json",
                Authorization: `Bearer ${token}`,
              },
              signal: AbortSignal.timeout(10000), // 10 seconds timeout
              cache: "no-store",
              mode: "cors",
            })

            if (!response.ok) {
              throw new Error(`API request failed: ${response.status} ${response.statusText}`)
            }

            const text = await response.text()
            console.log("ComparisonTable - Direct fetch response text (first 200 chars):", text.substring(0, 200))

            try {
              const data = JSON.parse(text)
              console.log("ComparisonTable - Direct fetch successful, parsed JSON:", data)
              processResponse(data)
            } catch (e) {
              console.error("ComparisonTable - Error parsing direct fetch response as JSON:", e)
              throw new Error("Invalid JSON response")
            }
          } catch (directError) {
            console.error("ComparisonTable - Direct fetch failed:", directError)
            // Fall back to mock data after all attempts fail
            setMockData()
          }
        }
      } catch (e) {
        console.error("ComparisonTable - Error in fetchSessions:", e)
        // Fall back to mock data
        setMockData()
      } finally {
        setIsLoading(false)
      }
    }

    // Helper function to set mock data when all fetch attempts fail
    function setMockData() {
      const mockSessions: SurfSession[] = [
        {
          id: 1,
          session_name: "Mock Beach Session",
          location: "Local Beach",
          date: new Date().toISOString().split("T")[0],
          time: "10:00:00",
          fun_rating: 8,
          session_notes: "This is mock data shown when the API is unreachable.",
          created_at: new Date().toISOString(),
          user_id: "mock-user-id-1",
          user_email: "mock-user1@example.com",
          raw_swell: [
            {
              date: "2025-04-10T09:50:00+00:00",
              swell_components: {
                swell_1: {
                  direction: 200.0,
                  height: 1.78,
                  period: 5.0,
                },
              },
            },
          ],
        },
        {
          id: 2,
          session_name: "Another Mock Session",
          location: "Surf Point",
          date: new Date(Date.now() - 86400000).toISOString().split("T")[0], // Yesterday
          time: "14:30:00",
          fun_rating: 7,
          session_notes: "Mock data for demonstration purposes.",
          created_at: new Date(Date.now() - 86400000).toISOString(),
          user_id: "mock-user-id-2",
          user_email: "mock-user2@example.com",
          raw_swell: [
            {
              date: "2025-04-09T11:20:00+00:00",
              swell_components: {
                swell_1: {
                  direction: 300.0,
                  height: 2.68,
                  period: 3.84,
                },
              },
            },
          ],
        },
        {
          id: 3,
          session_name: "Third Mock Session",
          location: "Wave Bay",
          date: new Date(Date.now() - 172800000).toISOString().split("T")[0], // 2 days ago
          time: "09:15:00",
          fun_rating: 9,
          session_notes: "Another mock session for testing.",
          created_at: new Date(Date.now() - 172800000).toISOString(),
          user_id: "mock-user-id-3",
          user_email: "mock-user3@example.com",
          raw_swell: [
            {
              date: "2025-04-08T00:00:00+00:00",
              swell_components: {
                swell_1: {
                  direction: 100.0,
                  height: 2.93,
                  period: 5.88,
                },
              },
            },
          ],
        },
      ]

      setSessions(mockSessions)
      setError("Using mock data because the API is currently unreachable.")
    }

    // Helper function to process the response and extract sessions
    function processResponse(data: any) {
      console.log("ComparisonTable - Processing response data:", data)

      // Extract sessions from the response
      let extractedSessions: SurfSession[] = []

      if (data) {
        if (Array.isArray(data)) {
          // Direct array
          extractedSessions = data
        } else if (typeof data === "object") {
          // Check for common response formats
          if (data.data && Array.isArray(data.data)) {
            // { data: [...] } format
            extractedSessions = data.data
          } else if (data.status === "success" && data.data && Array.isArray(data.data)) {
            // { status: "success", data: [...] } format
            extractedSessions = data.data
          } else {
            // Try to find any array property that might contain sessions
            for (const key in data) {
              if (Array.isArray(data[key]) && data[key].length > 0) {
                if (data[key][0] && (data[key][0].session_name || data[key][0].id)) {
                  extractedSessions = data[key]
                  break
                }
              }
            }
          }
        }
      }

      console.log("ComparisonTable - Extracted sessions:", extractedSessions)

      if (extractedSessions.length > 0) {
        setSessions(extractedSessions)
        setError(null)
      } else {
        console.warn("ComparisonTable - No sessions found in the response, using mock data")
        // If no sessions found, use mock data
        setMockData()
      }
    }

    fetchSessions()
  }, [retryCount])

  // Function to retry fetching data
  const handleRetry = () => {
    setRetryCount((prev) => prev + 1)
  }

  const handleSort = (field: SortField) => {
    if (field === sortField) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc")
    } else {
      setSortField(field)
      setSortDirection("asc")
    }
  }

  // Helper function to extract swell data from a session
  const getSwellData = (session: SurfSession) => {
    if (!session.raw_swell || !Array.isArray(session.raw_swell) || session.raw_swell.length === 0) {
      return {
        swell1: { direction: null, height: null, period: null },
        swell2: { direction: null, height: null, period: null },
        swell3: { direction: null, height: null, period: null },
        swell4: { direction: null, height: null, period: null },
      }
    }

    const swellData = session.raw_swell[0]
    if (!swellData.swell_components) {
      return {
        swell1: { direction: null, height: null, period: null },
        swell2: { direction: null, height: null, period: null },
        swell3: { direction: null, height: null, period: null },
        swell4: { direction: null, height: null, period: null },
      }
    }

    return {
      swell1: swellData.swell_components.swell_1
        ? {
            direction: swellData.swell_components.swell_1.direction,
            height: swellData.swell_components.swell_1.height,
            period: swellData.swell_components.swell_1.period,
          }
        : { direction: null, height: null, period: null },
      swell2: swellData.swell_components.swell_2
        ? {
            direction: swellData.swell_components.swell_2.direction,
            height: swellData.swell_components.swell_2.height,
            period: swellData.swell_components.swell_2.period,
          }
        : { direction: null, height: null, period: null },
      swell3: swellData.swell_components.swell_3
        ? {
            direction: swellData.swell_components.swell_3.direction,
            height: swellData.swell_components.swell_3.height,
            period: swellData.swell_components.swell_3.period,
          }
        : { direction: null, height: null, period: null },
      swell4: swellData.swell_components.swell_4
        ? {
            direction: swellData.swell_components.swell_4.direction,
            height: swellData.swell_components.swell_4.height,
            period: swellData.swell_components.swell_4.period,
          }
        : { direction: null, height: null, period: null },
    }
  }

  // Helper function to extract wind data from a session
  const getWindData = (session: SurfSession) => {
    // Check if raw_met data exists
    if (!session.raw_met || !Array.isArray(session.raw_met) || session.raw_met.length === 0) {
      return { speed: null, direction: null }
    }

    // Get the first meteorological data entry
    const metData = session.raw_met[0]

    return {
      speed: metData.wind_speed !== undefined ? metData.wind_speed : null,
      direction: metData.wind_direction !== undefined ? metData.wind_direction : null,
    }
  }

  // Add the getTideData function after the getWindData function
  // Helper function to extract tide data from a session
  const getTideData = (session: SurfSession) => {
    // Check if raw_tide data exists
    if (!session.raw_tide) {
      return { water_level: null, units: null }
    }

    return {
      water_level: session.raw_tide.water_level !== undefined ? session.raw_tide.water_level : null,
      units: session.raw_tide.units || "m",
    }
  }

  // Apply filters to sessions
  const filteredSessions = sessions.filter((session) => {
    // Apply location filter if set
    if (locationFilter && !session.location.toLowerCase().includes(locationFilter.toLowerCase())) {
      return false
    }

    // Apply date filter if set
    if (dateFilter) {
      const sessionDate = new Date(session.date).toISOString().split("T")[0]
      if (sessionDate !== dateFilter) {
        return false
      }
    }

    // Apply user filter if set (now using display_name)
    if (userFilter && session.display_name) {
      if (!session.display_name.toLowerCase().includes(userFilter.toLowerCase())) {
        return false
      }
    }

    // Apply swell1 direction filter if set
    if (swell1DirectionFilter && swell1DirectionFilter !== "") {
      const swellData = getSwellData(session)
      const direction = swellData.swell1.direction

      // Skip sessions without swell1 direction data
      if (direction === null) {
        return false
      }

      // Convert both to strings for comparison
      if (direction.toString() !== swell1DirectionFilter) {
        return false
      }
    }

    // Apply swell1 height filter if set
    if (swell1HeightFilter && swell1HeightFilter !== "") {
      const swellData = getSwellData(session)
      const height = swellData.swell1.height

      // Skip sessions without swell1 height data
      if (height === null) {
        return false
      }

      // Convert both to strings for comparison
      if (height.toString() !== swell1HeightFilter) {
        return false
      }
    }

    // Apply swell1 period filter if set
    if (swell1PeriodFilter && swell1PeriodFilter !== "") {
      const swellData = getSwellData(session)
      const period = swellData.swell1.period

      // Skip sessions without swell1 period data
      if (period === null) {
        return false
      }

      // Convert both to strings for comparison
      if (period.toString() !== swell1PeriodFilter) {
        return false
      }
    }

    return true
  })

  const sortedSessions = [...filteredSessions].sort((a, b) => {
    let comparison = 0

    switch (sortField) {
      case "date":
        const dateA = new Date(a.date)
        const dateB = new Date(b.date)
        comparison = dateA.getTime() - dateB.getTime()
        break
      case "start_time":
        const startTimeA = a.time || ""
        const startTimeB = b.time || ""
        comparison = startTimeA.localeCompare(startTimeB)
        break
      case "end_time":
        const endTimeA = a.end_time || ""
        const endTimeB = b.end_time || ""
        comparison = endTimeA.localeCompare(endTimeB)
        break
      case "location":
        comparison = (a.location || "").localeCompare(b.location || "")
        break
      case "session_name":
        comparison = (a.session_name || "").localeCompare(b.session_name || "")
        break
      case "fun_rating":
        comparison = (a.fun_rating || 0) - (b.fun_rating || 0)
        break
      case "display_name":
        // Use display_name for comparison, fallback to user_email if display_name is missing
        const nameA = a.display_name || a.user_email || ""
        const nameB = b.display_name || b.user_email || ""
        comparison = nameA.localeCompare(nameB)
        break
      case "swell1_height":
        const height1A = getSwellData(a).swell1.height || 0
        const height1B = getSwellData(b).swell1.height || 0
        comparison = height1A - height1B
        break
      case "swell1_period":
        const period1A = getSwellData(a).swell1.period || 0
        const period1B = getSwellData(b).swell1.period || 0
        comparison = period1A - period1B
        break
      case "swell1_direction":
        const dir1A = getSwellData(a).swell1.direction || 0
        const dir1B = getSwellData(b).swell1.direction || 0
        comparison = dir1A - dir1B
        break
      case "swell2_height":
        const height2A = getSwellData(a).swell2.height || 0
        const height2B = getSwellData(b).swell2.height || 0
        comparison = height2A - height2B
        break
      case "swell2_period":
        const period2A = getSwellData(a).swell2.period || 0
        const period2B = getSwellData(b).swell2.period || 0
        comparison = period2A - period2B
        break
      case "swell2_direction":
        const dir2A = getSwellData(a).swell2.direction || 0
        const dir2B = getSwellData(b).swell2.direction || 0
        comparison = dir2A - dir2B
        break
      case "swell3_height":
        const height3A = getSwellData(a).swell3.height || 0
        const height3B = getSwellData(b).swell3.height || 0
        comparison = height3A - height3B
        break
      case "swell3_period":
        const period3A = getSwellData(a).swell3.period || 0
        const period3B = getSwellData(b).swell3.period || 0
        comparison = period3A - period3B
        break
      case "swell3_direction":
        const dir3A = getSwellData(a).swell3.direction || 0
        const dir3B = getSwellData(b).swell3.direction || 0
        comparison = dir3A - dir3B
        break
      case "swell4_height":
        const height4A = getSwellData(a).swell4.height || 0
        const height4B = getSwellData(b).swell4.height || 0
        comparison = height4A - height4B
        break
      case "swell4_period":
        const period4A = getSwellData(a).swell4.period || 0
        const period4B = getSwellData(b).swell4.period || 0
        comparison = period4A - period4B
        break
      case "swell4_direction":
        const dir4A = getSwellData(a).swell4.direction || 0
        const dir4B = getSwellData(b).swell4.direction || 0
        comparison = dir4A - dir4B
        break
      case "wind_speed":
        const speedA = getWindData(a).speed || 0
        const speedB = getWindData(b).speed || 0
        comparison = speedA - speedB
        break
      case "wind_direction":
        const windDirA = getWindData(a).direction || 0
        const windDirB = getWindData(b).direction || 0
        comparison = windDirA - windDirB
        break
      case "tide_water_level":
        const waterLevelA = getTideData(a).water_level || 0
        const waterLevelB = getTideData(b).water_level || 0
        comparison = waterLevelA - waterLevelB
        break
    }

    return sortDirection === "asc" ? comparison : -comparison
  })

  const SortIcon = ({ field }: { field: SortField }) => {
    if (field !== sortField) return <ArrowUpDown className="ml-2 h-4 w-4" />
    return sortDirection === "asc" ? <ChevronUp className="ml-2 h-4 w-4" /> : <ChevronDown className="ml-2 h-4 w-4" />
  }

  // Get unique locations for filter dropdown
  const uniqueLocations = Array.from(new Set(sessions.map((session) => session.location)))
    .filter(Boolean)
    .sort()

  // Get unique users for filter dropdown (now using display_name)
  const uniqueUsers = Array.from(new Set(sessions.map((session) => session.display_name || session.user_email)))
    .filter(Boolean)
    .sort()

  // Get unique swell1 directions for filter dropdown
  const uniqueSwell1Directions = Array.from(
    new Set(
      sessions
        .map((session) => {
          const swellData = getSwellData(session)
          return swellData.swell1.direction !== null ? swellData.swell1.direction.toString() : null
        })
        .filter(Boolean),
    ),
  ).sort((a, b) => Number(a) - Number(b)) // Sort numerically

  // Get unique swell1 heights for filter dropdown
  const uniqueSwell1Heights = Array.from(
    new Set(
      sessions
        .map((session) => {
          const swellData = getSwellData(session)
          return swellData.swell1.height !== null ? swellData.swell1.height.toString() : null
        })
        .filter(Boolean),
    ),
  ).sort((a, b) => Number(a) - Number(b)) // Sort numerically

  // Get unique swell1 periods for filter dropdown
  const uniqueSwell1Periods = Array.from(
    new Set(
      sessions
        .map((session) => {
          const swellData = getSwellData(session)
          return swellData.swell1.period !== null ? swellData.swell1.period.toString() : null
        })
        .filter(Boolean),
    ),
  ).sort((a, b) => Number(a) - Number(b)) // Sort numerically

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <span className="ml-2">Loading sessions...</span>
      </div>
    )
  }

  return (
    <>
      {error && (
        <Alert variant="warning" className="mb-6">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>API Connection Issue</AlertTitle>
          <AlertDescription className="flex flex-col gap-2">
            <p>{error}</p>
            <Button onClick={handleRetry} variant="outline" className="self-start mt-2 bg-transparent">
              Retry Connection
            </Button>
          </AlertDescription>
        </Alert>
      )}

      <div className="space-y-4">
        {/* First row: User filter and Date filter */}
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <label htmlFor="user-filter" className="block text-sm font-medium text-muted-foreground mb-1">
              Filter by User Email
            </label>
            <select
              id="user-filter"
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={userFilter}
              onChange={(e) => setUserFilter(e.target.value)}
            >
              <option value="">All Users</option>
              {uniqueUsers.map((email) => (
                <option key={email} value={email}>
                  {email}
                </option>
              ))}
            </select>
          </div>
          <div className="flex-1">
            <label htmlFor="date-filter" className="block text-sm font-medium text-muted-foreground mb-1">
              Filter by Date
            </label>
            <input
              id="date-filter"
              type="date"
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={dateFilter}
              onChange={(e) => setDateFilter(e.target.value)}
            />
          </div>
        </div>

        {/* Second row: Location and Swell filters */}
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <label htmlFor="location-filter" className="block text-sm font-medium text-muted-foreground mb-1">
              Filter by Location
            </label>
            <select
              id="location-filter"
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={locationFilter}
              onChange={(e) => setLocationFilter(e.target.value)}
            >
              <option value="">All Locations</option>
              {uniqueLocations.map((location) => (
                <option key={location} value={location}>
                  {location}
                </option>
              ))}
            </select>
          </div>
          <div className="flex-1">
            <label htmlFor="swell1-direction-filter" className="block text-sm font-medium text-muted-foreground mb-1">
              Filter by Swell 1 Direction
            </label>
            <select
              id="swell1-direction-filter"
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={swell1DirectionFilter}
              onChange={(e) => setSwell1DirectionFilter(e.target.value)}
            >
              <option value="">All Directions</option>
              {uniqueSwell1Directions.map((direction) => (
                <option key={direction} value={direction}>
                  {direction}°
                </option>
              ))}
            </select>
          </div>
          <div className="flex-1">
            <label htmlFor="swell1-height-filter" className="block text-sm font-medium text-muted-foreground mb-1">
              Filter by Swell 1 Height
            </label>
            <select
              id="swell1-height-filter"
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={swell1HeightFilter}
              onChange={(e) => setSwell1HeightFilter(e.target.value)}
            >
              <option value="">All Heights</option>
              {uniqueSwell1Heights.map((height) => (
                <option key={height} value={height}>
                  {height} ft
                </option>
              ))}
            </select>
          </div>
          <div className="flex-1">
            <label htmlFor="swell1-period-filter" className="block text-sm font-medium text-muted-foreground mb-1">
              Filter by Swell 1 Period
            </label>
            <select
              id="swell1-period-filter"
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={swell1PeriodFilter}
              onChange={(e) => setSwell1PeriodFilter(e.target.value)}
            >
              <option value="">All Periods</option>
              {uniqueSwell1Periods.map((period) => (
                <option key={period} value={period}>
                  {period} s
                </option>
              ))}
            </select>
          </div>
          <div className="flex items-end">
            <Button
              variant="outline"
              onClick={() => {
                setLocationFilter("")
                setDateFilter("")
                setUserFilter("")
                setSwell1DirectionFilter("")
                setSwell1HeightFilter("")
                setSwell1PeriodFilter("")
              }}
              className="mb-0"
            >
              Clear Filters
            </Button>
          </div>
        </div>

        <div className="rounded-md border overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>
                  <button
                    onClick={() => handleSort("display_name")}
                    className="flex items-center p-0 font-medium bg-transparent border-none text-inherit cursor-pointer"
                  >
                    User
                    <SortIcon field="display_name" />
                  </button>
                </TableHead>
                <TableHead>
                  <button
                    onClick={() => handleSort("session_name")}
                    className="flex items-center p-0 font-medium bg-transparent border-none text-inherit cursor-pointer"
                  >
                    Session Name
                    <SortIcon field="session_name" />
                  </button>
                </TableHead>
                <TableHead>
                  <button
                    onClick={() => handleSort("location")}
                    className="flex items-center p-0 font-medium bg-transparent border-none text-inherit cursor-pointer"
                  >
                    Location
                    <SortIcon field="location" />
                  </button>
                </TableHead>
                <TableHead>
                  <button
                    onClick={() => handleSort("date")}
                    className="flex items-center p-0 font-medium bg-transparent border-none text-inherit cursor-pointer"
                  >
                    Date
                    <SortIcon field="date" />
                  </button>
                </TableHead>
                <TableHead>
                  <button
                    onClick={() => handleSort("start_time")}
                    className="flex items-center p-0 font-medium bg-transparent border-none text-inherit cursor-pointer"
                  >
                    Start Time
                    <SortIcon field="start_time" />
                  </button>
                </TableHead>
                <TableHead>
                  <button
                    onClick={() => handleSort("end_time")}
                    className="flex items-center p-0 font-medium bg-transparent border-none text-inherit cursor-pointer"
                  >
                    End Time
                    <SortIcon field="end_time" />
                  </button>
                </TableHead>
                <TableHead>
                  <button
                    onClick={() => handleSort("fun_rating")}
                    className="flex items-center p-0 font-medium bg-transparent border-none text-inherit cursor-pointer"
                  >
                    Rating
                    <SortIcon field="fun_rating" />
                  </button>
                </TableHead>
                {/* Swell 1 columns */}
                <TableHead>
                  <button
                    onClick={() => handleSort("swell1_height")}
                    className="flex items-center p-0 font-medium bg-transparent border-none text-inherit cursor-pointer whitespace-nowrap"
                  >
                    <Waves className="h-3 w-3 mr-1" />
                    Swell 1 Height (ft)
                    <SortIcon field="swell1_height" />
                  </button>
                </TableHead>
                <TableHead>
                  <button
                    onClick={() => handleSort("swell1_period")}
                    className="flex items-center p-0 font-medium bg-transparent border-none text-inherit cursor-pointer whitespace-nowrap"
                  >
                    <Waves className="h-3 w-3 mr-1" />
                    Swell 1 Period (s)
                    <SortIcon field="swell1_period" />
                  </button>
                </TableHead>
                <TableHead>
                  <button
                    onClick={() => handleSort("swell1_direction")}
                    className="flex items-center p-0 font-medium bg-transparent border-none text-inherit cursor-pointer whitespace-nowrap"
                  >
                    <Waves className="h-3 w-3 mr-1" />
                    Swell 1 Direction (°)
                    <SortIcon field="swell1_direction" />
                  </button>
                </TableHead>
                {/* Swell 2 columns */}
                <TableHead>
                  <button
                    onClick={() => handleSort("swell2_height")}
                    className="flex items-center p-0 font-medium bg-transparent border-none text-inherit cursor-pointer whitespace-nowrap"
                  >
                    <Waves className="h-3 w-3 mr-1" />
                    Swell 2 Height (ft)
                    <SortIcon field="swell2_height" />
                  </button>
                </TableHead>
                <TableHead>
                  <button
                    onClick={() => handleSort("swell2_period")}
                    className="flex items-center p-0 font-medium bg-transparent border-none text-inherit cursor-pointer whitespace-nowrap"
                  >
                    <Waves className="h-3 w-3 mr-1" />
                    Swell 2 Period (s)
                    <SortIcon field="swell2_period" />
                  </button>
                </TableHead>
                <TableHead>
                  <button
                    onClick={() => handleSort("swell2_direction")}
                    className="flex items-center p-0 font-medium bg-transparent border-none text-inherit cursor-pointer whitespace-nowrap"
                  >
                    <Waves className="h-3 w-3 mr-1" />
                    Swell 2 Direction (°)
                    <SortIcon field="swell2_direction" />
                  </button>
                </TableHead>
                {/* Swell 3 columns */}
                <TableHead>
                  <button
                    onClick={() => handleSort("swell3_height")}
                    className="flex items-center p-0 font-medium bg-transparent border-none text-inherit cursor-pointer whitespace-nowrap"
                  >
                    <Waves className="h-3 w-3 mr-1" />
                    Swell 3 Height (ft)
                    <SortIcon field="swell3_height" />
                  </button>
                </TableHead>
                <TableHead>
                  <button
                    onClick={() => handleSort("swell3_period")}
                    className="flex items-center p-0 font-medium bg-transparent border-none text-inherit cursor-pointer whitespace-nowrap"
                  >
                    <Waves className="h-3 w-3 mr-1" />
                    Swell 3 Period (s)
                    <SortIcon field="swell3_period" />
                  </button>
                </TableHead>
                <TableHead>
                  <button
                    onClick={() => handleSort("swell3_direction")}
                    className="flex items-center p-0 font-medium bg-transparent border-none text-inherit cursor-pointer whitespace-nowrap"
                  >
                    <Waves className="h-3 w-3 mr-1" />
                    Swell 3 Direction (°)
                    <SortIcon field="swell3_direction" />
                  </button>
                </TableHead>
                {/* Swell 4 columns */}
                <TableHead>
                  <button
                    onClick={() => handleSort("swell4_height")}
                    className="flex items-center p-0 font-medium bg-transparent border-none text-inherit cursor-pointer whitespace-nowrap"
                  >
                    <Waves className="h-3 w-3 mr-1" />
                    Swell 4 Height (ft)
                    <SortIcon field="swell4_height" />
                  </button>
                </TableHead>
                <TableHead>
                  <button
                    onClick={() => handleSort("swell4_period")}
                    className="flex items-center p-0 font-medium bg-transparent border-none text-inherit cursor-pointer whitespace-nowrap"
                  >
                    <Waves className="h-3 w-3 mr-1" />
                    Swell 4 Period (s)
                    <SortIcon field="swell4_period" />
                  </button>
                </TableHead>
                <TableHead>
                  <button
                    onClick={() => handleSort("swell4_direction")}
                    className="flex items-center p-0 font-medium bg-transparent border-none text-inherit cursor-pointer whitespace-nowrap"
                  >
                    <Waves className="h-3 w-3 mr-1" />
                    Swell 4 Direction (°)
                    <SortIcon field="swell4_direction" />
                  </button>
                </TableHead>
                {/* Wind data columns */}
                <TableHead>
                  <button
                    onClick={() => handleSort("wind_speed")}
                    className="flex items-center p-0 font-medium bg-transparent border-none text-inherit cursor-pointer whitespace-nowrap"
                  >
                    <Wind className="h-3 w-3 mr-1" />
                    Wind Speed (mph)
                    <SortIcon field="wind_speed" />
                  </button>
                </TableHead>
                <TableHead>
                  <button
                    onClick={() => handleSort("wind_direction")}
                    className="flex items-center p-0 font-medium bg-transparent border-none text-inherit cursor-pointer whitespace-nowrap"
                  >
                    <Wind className="h-3 w-3 mr-1" />
                    Wind Direction (°)
                    <SortIcon field="wind_direction" />
                  </button>
                </TableHead>
                {/* Tide data column */}
                <TableHead>
                  <button
                    onClick={() => handleSort("tide_water_level")}
                    className="flex items-center p-0 font-medium bg-transparent border-none text-inherit cursor-pointer whitespace-nowrap"
                  >
                    <Waves className="h-3 w-3 mr-1" />
                    Tide Level (m)
                    <SortIcon field="tide_water_level" />
                  </button>
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sortedSessions.length > 0 ? (
                sortedSessions.map((session) => {
                  const swellData = getSwellData(session)

                  return (
                    <TableRow key={session.id} className="cursor-pointer hover:bg-muted/50">
                      <TableCell>
                        <Link href={`/sessions/${session.id}`} className="block w-full">
                          <div className="flex items-center gap-1">
                            <Mail className="h-3 w-3 text-muted-foreground" />
                            {session.display_name || session.user_email || "Unknown User"}
                          </div>
                        </Link>
                      </TableCell>
                      <TableCell>
                        <Link href={`/sessions/${session.id}`} className="block w-full">
                          {session.session_name || "Unnamed Session"}
                        </Link>
                      </TableCell>
                      <TableCell>
                        <Link href={`/sessions/${session.id}`} className="block w-full">
                          {session.location || "N/A"}
                        </Link>
                      </TableCell>
                      <TableCell>
                        <Link href={`/sessions/${session.id}`} className="block w-full">
                          {formatDate(session.date)}
                        </Link>
                      </TableCell>
                      <TableCell>
                        <Link href={`/sessions/${session.id}`} className="block w-full">
                          {session.time ? formatTime(session.time) : "N/A"}
                        </Link>
                      </TableCell>
                      <TableCell>
                        <Link href={`/sessions/${session.id}`} className="block w-full">
                          {session.end_time ? formatTime(session.end_time) : "N/A"}
                        </Link>
                      </TableCell>
                      <TableCell>
                        <Link href={`/sessions/${session.id}`} className="block w-full">
                          <span className="font-medium">{session.fun_rating || 0}/10</span>
                        </Link>
                      </TableCell>
                      {/* Swell 1 data */}
                      <TableCell>
                        <Link href={`/sessions/${session.id}`} className="block w-full">
                          {swellData.swell1.height !== null ? swellData.swell1.height.toFixed(2) : "N/A"}
                        </Link>
                      </TableCell>
                      <TableCell>
                        <Link href={`/sessions/${session.id}`} className="block w-full">
                          {swellData.swell1.period !== null ? swellData.swell1.period.toFixed(2) : "N/A"}
                        </Link>
                      </TableCell>
                      <TableCell>
                        <Link href={`/sessions/${session.id}`} className="block w-full">
                          {swellData.swell1.direction !== null ? swellData.swell1.direction.toFixed(0) : "N/A"}
                        </Link>
                      </TableCell>
                      {/* Swell 2 data */}
                      <TableCell>
                        <Link href={`/sessions/${session.id}`} className="block w-full">
                          {swellData.swell2.height !== null ? swellData.swell2.height.toFixed(2) : "N/A"}
                        </Link>
                      </TableCell>
                      <TableCell>
                        <Link href={`/sessions/${session.id}`} className="block w-full">
                          {swellData.swell2.period !== null ? swellData.swell2.period.toFixed(2) : "N/A"}
                        </Link>
                      </TableCell>
                      <TableCell>
                        <Link href={`/sessions/${session.id}`} className="block w-full">
                          {swellData.swell2.direction !== null ? swellData.swell2.direction.toFixed(0) : "N/A"}
                        </Link>
                      </TableCell>
                      {/* Swell 3 data */}
                      <TableCell>
                        <Link href={`/sessions/${session.id}`} className="block w-full">
                          {swellData.swell3.height !== null ? swellData.swell3.height.toFixed(2) : "N/A"}
                        </Link>
                      </TableCell>
                      <TableCell>
                        <Link href={`/sessions/${session.id}`} className="block w-full">
                          {swellData.swell3.period !== null ? swellData.swell3.period.toFixed(2) : "N/A"}
                        </Link>
                      </TableCell>
                      <TableCell>
                        <Link href={`/sessions/${session.id}`} className="block w-full">
                          {swellData.swell3.direction !== null ? swellData.swell3.direction.toFixed(0) : "N/A"}
                        </Link>
                      </TableCell>
                      {/* Swell 4 data */}
                      <TableCell>
                        <Link href={`/sessions/${session.id}`} className="block w-full">
                          {swellData.swell4.height !== null ? swellData.swell4.height.toFixed(2) : "N/A"}
                        </Link>
                      </TableCell>
                      <TableCell>
                        <Link href={`/sessions/${session.id}`} className="block w-full">
                          {swellData.swell4.period !== null ? swellData.swell4.period.toFixed(2) : "N/A"}
                        </Link>
                      </TableCell>
                      <TableCell>
                        <Link href={`/sessions/${session.id}`} className="block w-full">
                          {swellData.swell4.direction !== null ? swellData.swell4.direction.toFixed(0) : "N/A"}
                        </Link>
                      </TableCell>
                      {/* Wind data */}
                      <TableCell>
                        <Link href={`/sessions/${session.id}`} className="block w-full">
                          {getWindData(session).speed !== null ? getWindData(session).speed.toFixed(1) : "N/A"}
                        </Link>
                      </TableCell>
                      <TableCell>
                        <Link href={`/sessions/${session.id}`} className="block w-full">
                          {getWindData(session).direction !== null ? getWindData(session).direction.toFixed(0) : "N/A"}
                        </Link>
                      </TableCell>
                      {/* Tide data */}
                      <TableCell>
                        <Link href={`/sessions/${session.id}`} className="block w-full">
                          {getTideData(session).water_level !== null
                            ? `${getTideData(session).water_level.toFixed(2)} ${getTideData(session).units}`
                            : "N/A"}
                        </Link>
                      </TableCell>
                    </TableRow>
                  )
                })
              ) : (
                <TableRow>
                  <TableCell colSpan={22} className="h-24 text-center">
                    {locationFilter ||
                    dateFilter ||
                    userFilter ||
                    swell1DirectionFilter ||
                    swell1HeightFilter ||
                    swell1PeriodFilter
                      ? "No sessions match your filters. Try adjusting or clearing your filters."
                      : "No sessions found."}
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>

        {/* Show filter summary if filters are applied */}
        {(locationFilter ||
          dateFilter ||
          userFilter ||
          swell1DirectionFilter ||
          swell1HeightFilter ||
          swell1PeriodFilter) && (
          <div className="text-sm text-muted-foreground">
            Showing {sortedSessions.length} of {sessions.length} sessions
            {locationFilter && <span> at {locationFilter}</span>}
            {dateFilter && <span> on {new Date(dateFilter).toLocaleDateString()}</span>}
            {userFilter && <span> by user {userFilter}</span>}
            {swell1DirectionFilter && <span> with swell 1 direction {swell1DirectionFilter}°</span>}
            {swell1HeightFilter && <span> with swell 1 height {swell1HeightFilter} ft</span>}
            {swell1PeriodFilter && <span> with swell 1 period {swell1PeriodFilter} s</span>}
          </div>
        )}
      </div>
    </>
  )
}
