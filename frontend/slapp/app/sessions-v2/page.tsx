"use client"

import { useState, useEffect, useCallback } from "react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"
import { AlertCircle } from "lucide-react"
import { SessionGrid } from "@/components/session-grid"
import { SessionFilters, SessionFiltersState } from "@/components/session-filters"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"

// --- Types (based on API documentation) ---
// In a real app, these would likely live in a central `types.ts` file
type SwellComponent = {
  direction: number
  height: number
  period: number
}

type SwellData = {
  date: string
  significant_wave_height: number | null
  swell_components: {
    swell_1?: SwellComponent
    swell_2?: SwellComponent
    swell_3?: SwellComponent
    swell_4?: SwellComponent
  }
}

type MetData = {
  air_temperature: number
  date: string
  dewpoint_temperature: number
  pressure: number
  pressure_tendency: number
  water_temperature: number
  wind_direction: number
  wind_gust: number
  wind_speed: number
}

type TideData = {
  date: string
  water_level: number
}

export type SurfSession = {
  id: number
  date: string
  time: string
  end_time: string
  session_name: string
  session_notes: string
  fun_rating: string
  location: string
  user_id: string
  display_name: string
  participants: Array<{ display_name: string; user_id: string }>
  raw_swell: SwellData[]
  raw_met: MetData[]
  raw_tide: TideData
}

type CurrentUser = {
  userId: string
  displayName: string
}

// --- Constants ---
const API_URL = "https://surfdata-gwj6bowm5-martins-projects-383d438b.vercel.app/api/surf-sessions"

const initialFilterState: SessionFiltersState = {
  showOnlyMySessions: false,
  location: "",
  startDate: "",
  endDate: "",
  swellHeight: "any",
  swellPeriod: "any",
  swellDirection: "any",
  funRating: 1,
  surfer: "any",
}

// --- Main Page Component ---
export default function SessionsV2Page() {
  const [allSessions, setAllSessions] = useState<SurfSession[]>([])
  const [filteredSessions, setFilteredSessions] = useState<SurfSession[]>([])
  const [filters, setFilters] = useState<SessionFiltersState>(initialFilterState)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null)
  const [availableSurferNames, setAvailableSurferNames] = useState<string[]>([])

  useEffect(() => {
    // --- Get Current User Info ---
    try {
      const userDataString = localStorage.getItem("user_data")
      if (userDataString) {
        if (userDataString) {
        const userData = JSON.parse(userDataString)
        console.log("DEBUG: User data from localStorage:", userData);
        setCurrentUser({
          userId: userData.id, // Corrected from userData.user_id
          displayName: userData.display_name,
        })
      }
      }
    } catch (e) {
      console.error("Failed to parse user data from localStorage", e)
    }

    // --- Fetch All Session Data ---
    const fetchSessions = async () => {
      setLoading(true)
      setError(null)
      try {
        const token = localStorage.getItem("auth_token")

        const response = await fetch("/api/auth/cors-proxy", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            url: API_URL,
            method: "GET",
            headers: { Authorization: `Bearer ${token}` },
          }),
        })

        if (!response.ok) {
          throw new Error(`API request failed: ${response.statusText}`)
        }

        const result = await response.json()
        const sessions = result.data || []

        // Sort by date descending by default
        sessions.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())

        setAllSessions(sessions)

        // Extract unique surfer names
        const uniqueSurfers = Array.from(new Set(sessions.map(s => s.display_name)))
        setAvailableSurferNames(uniqueSurfers)

      } catch (err) {
        setError(err instanceof Error ? err.message : "An unknown error occurred.")
        console.error("Failed to fetch surf sessions:", err)
      } finally {
        setLoading(false)
      }
    }

    fetchSessions()
  }, [])

  // --- Filtering Logic ---
  const applyFilters = useCallback(() => {
    let sessionsToFilter = [...allSessions]

    // My Sessions toggle
    if (filters.showOnlyMySessions && currentUser) {
      sessionsToFilter = sessionsToFilter.filter(s => s.user_id === currentUser.userId)
    }

    // Location
    if (filters.location) {
      sessionsToFilter = sessionsToFilter.filter(s => s.location.toLowerCase().includes(filters.location.toLowerCase()))
    }
    
    // Date Range
    if (filters.dateRange !== 'any') {
        const now = new Date();
        let startDate: Date | null = null;
        let endDate: Date | null = null;

        switch (filters.dateRange) {
            case 'past7':
                startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 7);
                break;
            case 'past30':
                startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 30);
                break;
            case 'thisMonth':
                startDate = new Date(now.getFullYear(), now.getMonth(), 1);
                endDate = new Date(now.getFullYear(), now.getMonth() + 1, 0);
                break;
            case 'thisYear':
                startDate = new Date(now.getFullYear(), 0, 1);
                endDate = new Date(now.getFullYear(), 11, 31);
                break;
            case 'lastYear':
                startDate = new Date(now.getFullYear() - 1, 0, 1);
                endDate = new Date(now.getFullYear() - 1, 11, 31);
                break;
            case '2023':
                startDate = new Date(2023, 0, 1);
                endDate = new Date(2023, 11, 31);
                break;
            case '2022':
                startDate = new Date(2022, 0, 1);
                endDate = new Date(2022, 11, 31);
                break;
        }

        if (startDate) {
            sessionsToFilter = sessionsToFilter.filter(s => new Date(s.date) >= startDate!)
        }
        if (endDate) {
            sessionsToFilter = sessionsToFilter.filter(s => new Date(s.date) <= endDate!)
        }
    }

    // Fun Rating
    sessionsToFilter = sessionsToFilter.filter(s => parseInt(s.fun_rating, 10) >= filters.funRating)

    

    // Surfer
    if (filters.surfer !== 'any') {
        sessionsToFilter = sessionsToFilter.filter(s => s.display_name === filters.surfer)
    }

    // Swell Filters
    if (filters.swellHeight !== 'any') {
        const [min, max] = filters.swellHeight.split('-').map(v => v === '' ? Infinity : Number(v))
        sessionsToFilter = sessionsToFilter.filter(s => {
            const h = s.raw_swell?.[0]?.swell_components?.swell_1?.height
            if (h === undefined) return false
            if (max) return h >= min && h < max
            return h >= min // For "5+" case
        })
    }
    if (filters.swellPeriod !== 'any') {
        const [min, max] = filters.swellPeriod.split('-').map(v => v === '' ? Infinity : Number(v))
        sessionsToFilter = sessionsToFilter.filter(s => {
            const p = s.raw_swell?.[0]?.swell_components?.swell_1?.period
            if (p === undefined) return false
            if (max) return p >= min && p < max
            return p >= min // For "12+" case
        })
    }
    if (filters.swellDirection !== 'any') {
        sessionsToFilter = sessionsToFilter.filter(s => {
            const d = s.raw_swell?.[0]?.swell_components?.swell_1?.direction
            if (d === undefined) return false
            // Simple N/E/S/W check
            if (filters.swellDirection === 'N') return (d >= 315 || d < 45)
            if (filters.swellDirection === 'E') return (d >= 45 && d < 135)
            if (filters.swellDirection === 'S') return (d >= 135 && d < 225)
            if (filters.swellDirection === 'W') return (d >= 225 && d < 315)
            return false
        })
    }

    setFilteredSessions(sessionsToFilter)
  }, [allSessions, filters, currentUser])

  useEffect(() => {
    applyFilters()
  }, [applyFilters])


  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
            <h1 className="text-3xl font-bold tracking-tight">Surf Sessions</h1>
            <p className="text-muted-foreground">Browse, filter, and explore all sessions.</p>
        </div>
        <div className="flex items-center space-x-2">
            <Switch 
                id="my-sessions-toggle"
                checked={filters.showOnlyMySessions}
                onCheckedChange={(checked) => setFilters(prev => ({ ...prev, showOnlyMySessions: checked }))}
            />
            <Label htmlFor="my-sessions-toggle" className="text-lg">My Sessions</Label>
        </div>
      </div>

      <SessionFilters filters={filters} setFilters={setFilters} initialState={initialFilterState} availableSurferNames={availableSurferNames} />

      {/* Display Grid or Loading/Error States */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <Skeleton key={i} className="h-64 w-full" />
          ))}
        </div>
      ) : error ? (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Error loading sessions: {error}. Please try refreshing the page.
          </AlertDescription>
        </Alert>
      ) : (
        <SessionGrid sessions={filteredSessions} />
      )}
    </div>
  )
}