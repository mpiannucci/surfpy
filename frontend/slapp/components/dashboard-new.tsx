"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Users, Trophy, Clock, Timer, MapPin } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"
import { UserDashboardStats } from "@/components/user-dashboard-stats"
import { capitalizeLocation, formatMinutesToHours } from "@/lib/utils"

// Helper function to format minutes to hours (without "hours" text)
function formatMinutesToHoursValue(minutes: string | number | null): string {
  if (!minutes || minutes === "0") return "0.0"
  const hours = parseFloat(minutes.toString()) / 60
  return hours.toFixed(1)
}

interface YearlyStats {
  avg_fun_rating: string;
  avg_session_duration_minutes: string;
  sessions_per_week: string;
  total_sessions: number;
  total_surf_time_minutes: string;
  top_locations?: TopLocation[];
}

interface TopLocation {
  location: string;
  session_count: number;
}

interface CurrentUser {
  top_locations: TopLocation[];
  total_sessions_all_time: number;
  yearly_stats: { [year: string]: YearlyStats };
}

interface OtherUser {
  display_name: string;
  total_sessions_all_time: number;
  user_id: string;
  yearly_stats: { [year: string]: YearlyStats };
}

interface CommunityStats {
  avg_session_duration_minutes: string;
  top_location: TopLocation;
  total_sessions: number;
  total_stoke: string;
  total_surf_time_minutes: string;
}

interface DashboardApiResponse {
  data: {
    community: CommunityStats;
    current_user: CurrentUser;
    other_users: OtherUser[];
  };
  status: string;
}

export function DashboardNew() {
  const [dashboardData, setDashboardData] = useState<DashboardApiResponse | null>(null)
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear().toString())
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [availableYears, setAvailableYears] = useState<string[]>([])

  useEffect(() => {
    async function fetchDashboardData() {
      try {
        setIsLoading(true)
        setError(null)

        const token = localStorage.getItem("auth_token")
        if (!token) {
          setError("Authentication required")
          return
        }

        const apiUrl = "https://surfdata-ea901547g-martins-projects-383d438b.vercel.app/api/dashboard"

        let responseData: DashboardApiResponse | null = null

        // Try with proxy first
        try {
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
                "Content-Type": "application/json",
                Accept: "application/json",
              },
            }),
            signal: AbortSignal.timeout(15000), // 15 seconds timeout
          })

          if (!proxyResponse.ok) {
            throw new Error(`Proxy request failed: ${proxyResponse.status} ${proxyResponse.statusText}`)
          }

          const proxyJson = await proxyResponse.json()
          if (proxyJson.status === "success" && proxyJson.data) {
            responseData = proxyJson
          } else {
            throw new Error("Invalid proxy response format")
          }
        } catch (proxyError) {
          console.error("Proxy request failed:", proxyError)

          // Try direct fetch as fallback
          try {
            const directResponse = await fetch(apiUrl, {
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

            if (!directResponse.ok) {
              throw new Error(`API request failed: ${directResponse.status} ${directResponse.statusText}`)
            }

            const directJson = await directResponse.json()
            if (directJson.status === "success" && directJson.data) {
              responseData = directJson
            } else {
              throw new Error("Invalid direct response format")
            }
          } catch (directError) {
            console.error("Direct request failed:", directError)
            setError("Unable to load dashboard data. Please try again later.")
          }
        }

        if (responseData) {
          setDashboardData(responseData)
        }
      } catch (e: any) {
        console.error("Dashboard fetch error:", e)
        setError(e.message || "Unable to load dashboard data. Please try again later.")
      } finally {
        setIsLoading(false)
      }
    }

    fetchDashboardData()
  }, [])

  // Get available years from data and set up year selection
  useEffect(() => {
    if (dashboardData) {
      const years = new Set<string>()
      
      // Add years from current_user
      Object.keys(dashboardData.data.current_user.yearly_stats || {}).forEach(year => {
        years.add(year)
      })
      
      // Add years from other_users
      dashboardData.data.other_users.forEach(user => {
        Object.keys(user.yearly_stats || {}).forEach(year => {
          years.add(year)
        })
      })
      
      const sortedYears = Array.from(years).sort((a, b) => parseInt(b) - parseInt(a))
      setAvailableYears(sortedYears)
      
      // Set default year to current year if available, otherwise most recent
      const currentYear = new Date().getFullYear().toString()
      if (sortedYears.includes(currentYear)) {
        setSelectedYear(currentYear)
      } else if (sortedYears.length > 0) {
        setSelectedYear(sortedYears[0])
      }
    }
  }, [dashboardData])

  if (isLoading) {
    return (
      <div className="space-y-8">
        {/* Loading skeleton for Your Stats section */}
        <div className="space-y-4">
          <Skeleton className="h-8 w-48 mb-4" />
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {[...Array(4)].map((_, i) => (
              <Card key={i}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-4 w-4" />
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <Skeleton className="h-8 w-16" />
                    <Skeleton className="h-6 w-20" />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
          <Skeleton className="h-10 w-full md:w-48 mx-auto mt-4" />
        </div>

        {/* Loading skeleton for table */}
        <div className="space-y-4">
          <Skeleton className="h-8 w-32" />
          <div className="rounded-md border">
            <div className="p-4 space-y-3">
              {[...Array(5)].map((_, i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    )
  }

  if (!dashboardData) {
    return (
      <Alert>
        <AlertTitle>No Data</AlertTitle>
        <AlertDescription>No dashboard data available.</AlertDescription>
      </Alert>
    )
  }

  const currentUserYearStats = dashboardData.data.current_user.yearly_stats?.[selectedYear] || {
    avg_fun_rating: "0",
    avg_session_duration_minutes: "0",
    sessions_per_week: "0",
    total_sessions: 0,
    total_surf_time_minutes: "0"
  }

  const allUsersWithYearData = [
    { ...dashboardData.data.current_user, user_id: "current", display_name: "You" }, 
    ...dashboardData.data.other_users
  ].map(user => {
    const yearStats = user.yearly_stats?.[selectedYear] || {
      total_sessions: 0,
      sessions_per_week: "0",
      avg_fun_rating: "0",
      avg_session_duration_minutes: "0",
      total_surf_time_minutes: "0"
    }
    
    return {
      ...user,
      yearStats
    }
  }).sort((a, b) => b.yearStats.total_sessions - a.yearStats.total_sessions)

  return (
    <div className="space-y-8">
      <UserDashboardStats
        currentUserYearStats={currentUserYearStats}
        totalSessionsAllTime={dashboardData.data.current_user.total_sessions_all_time}
        selectedYear={selectedYear}
      />

      {/* Leaderboards Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Leaderboards ({selectedYear})</h2>
          </div>
          <div className="flex items-center gap-4">
            <Select value={selectedYear} onValueChange={setSelectedYear}>
              <SelectTrigger className="w-32">
                <SelectValue placeholder="Select a year" />
              </SelectTrigger>
              <SelectContent>
                {availableYears.map(year => (
                  <SelectItem key={year} value={year}>{year}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* Sessions Leaderboard */}
          <div className="space-y-2">
            <h3 className="text-xl font-semibold">Sessions</h3>
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-16">Rank</TableHead>
                    <TableHead className="w-48">Surfer</TableHead>
                    <TableHead>Sessions</TableHead>
                    <TableHead>Sessions/Week</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {allUsersWithYearData.sort((a, b) => b.yearStats.total_sessions - a.yearStats.total_sessions).map((user, index) => (
                    <TableRow key={user.user_id} className={user.user_id === "current" ? "bg-muted/50" : ""}>
                      <TableCell className="font-medium">#{index + 1}</TableCell>
                      <TableCell className="font-medium">
                        {user.display_name}
                        {user.user_id === "current" && (<span className="ml-2 text-xs text-muted-foreground">(You)</span>)}
                      </TableCell>
                      <TableCell className="font-semibold">{user.yearStats.total_sessions}</TableCell>
                      <TableCell>{parseFloat(user.yearStats.sessions_per_week).toFixed(2)}</TableCell>
                    </TableRow>
                  ))}
                  {allUsersWithYearData.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={4} className="h-24 text-center">
                        No surfers found for {selectedYear}.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </div>
          </div>

          {/* Total Surf Time Leaderboard */}
          <div className="space-y-2">
            <h3 className="text-xl font-semibold">Total Surf Time</h3>
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-16">Rank</TableHead>
                    <TableHead className="w-48">Surfer</TableHead>
                    <TableHead>Total Time (hours)</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {allUsersWithYearData.sort((a, b) => parseFloat(b.yearStats.total_surf_time_minutes) - parseFloat(a.yearStats.total_surf_time_minutes)).map((user, index) => (
                    <TableRow key={user.user_id} className={user.user_id === "current" ? "bg-muted/50" : ""}>
                      <TableCell className="font-medium">#{index + 1}</TableCell>
                      <TableCell className="font-medium">
                        {user.display_name}
                        {user.user_id === "current" && (<span className="ml-2 text-xs text-muted-foreground">(You)</span>)}
                      </TableCell>
                      <TableCell>{formatMinutesToHoursValue(user.yearStats.total_surf_time_minutes)}</TableCell>
                    </TableRow>
                  ))}
                  {allUsersWithYearData.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={3} className="h-24 text-center">
                        No surfers found for {selectedYear}.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </div>
          </div>

          {/* Average Fun Rating Leaderboard */}
          <div className="space-y-2">
            <h3 className="text-xl font-semibold">Fun</h3>
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-16">Rank</TableHead>
                    <TableHead className="w-48">Surfer</TableHead>
                    <TableHead>Avg Rating</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {allUsersWithYearData.sort((a, b) => parseFloat(b.yearStats.avg_fun_rating) - parseFloat(a.yearStats.avg_fun_rating)).map((user, index) => (
                    <TableRow key={user.user_id} className={user.user_id === "current" ? "bg-muted/50" : ""}>
                      <TableCell className="font-medium">#{index + 1}</TableCell>
                      <TableCell className="font-medium">
                        {user.display_name}
                        {user.user_id === "current" && (<span className="ml-2 text-xs text-muted-foreground">(You)</span>)}
                      </TableCell>
                      <TableCell>{parseFloat(user.yearStats.avg_fun_rating).toFixed(1)}</TableCell>
                    </TableRow>
                  ))}
                  {allUsersWithYearData.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={3} className="h-24 text-center">
                        No surfers found for {selectedYear}.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </div>
          </div>
        </div>
      </div>

      {/* Section 3: Community Stats (Footer Section) */}
      <div className="space-y-4">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Community Stats</h2>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Sessions</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.data.community.total_sessions}</div>
              <p className="text-xs text-muted-foreground">Sessions logged by all users</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Stoke</CardTitle>
              <Trophy className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {parseFloat(dashboardData.data.community.total_stoke).toFixed(0)}
              </div>
              <p className="text-xs text-muted-foreground">Combined fun ratings</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Community Favorite</CardTitle>
              <MapPin className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              {dashboardData.data.community.top_location && dashboardData.data.community.top_location.location ? (
                <>
                  <div className="text-2xl font-bold">
                    {capitalizeLocation(dashboardData.data.community.top_location.location)}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {dashboardData.data.community.top_location.session_count} sessions
                  </p>
                </>
              ) : (
                <>
                  <div className="text-2xl font-bold">No data available</div>
                  <p className="text-xs text-muted-foreground">Most popular spot</p>
                </>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Surf Time</CardTitle>
              <Timer className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatMinutesToHours(dashboardData.data.community.total_surf_time_minutes)}
              </div>
              <p className="text-xs text-muted-foreground">All users combined</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}