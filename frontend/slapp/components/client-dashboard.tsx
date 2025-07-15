"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Waves, Users, Trophy, Clock, Timer, MapPin } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"
import type { DashboardData } from "@/lib/types"

// Helper function to format minutes to hours
function formatMinutesToHours(minutes: number | null): string {
  if (minutes === null || minutes === undefined) {
    return "No data"
  }
  if (minutes === 0) {
    return "0.0 hours"
  }
  const hours = minutes / 60
  return `${hours.toFixed(1)} hours`
}

// Helper function to format minutes to hours (without "hours" text)
function formatMinutesToHoursValue(minutes: number | null): string {
  if (minutes === null || minutes === undefined) {
    return "No data"
  }
  if (minutes === 0) {
    return "0.0"
  }
  const hours = minutes / 60
  return hours.toFixed(1)
}

// Helper function to capitalize first letter of each word
function capitalizeLocation(location: string): string {
  return location
    .split(" ")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(" ")
}

export function ClientDashboard() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchDashboardData() {
      try {
        setIsLoading(true)
        setError(null)

        // Get auth token
        const token = localStorage.getItem("auth_token")
        if (!token) {
          setError("Authentication required")
          return
        }

        // Updated API URL for dashboard
        const apiUrl = "https://surfdata-hs9191va8-martins-projects-383d438b.vercel.app/api/dashboard"

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

          const responseData = await proxyResponse.json()

          if (responseData.status === "success" && responseData.data) {
            setDashboardData(responseData.data)
          } else {
            throw new Error("Invalid response format")
          }
        } catch (proxyError) {
          console.error("Proxy request failed:", proxyError)

          // Try direct fetch as fallback
          try {
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

            const responseData = await response.json()

            if (responseData.status === "success" && responseData.data) {
              setDashboardData(responseData.data)
            } else {
              throw new Error("Invalid response format")
            }
          } catch (directError) {
            console.error("Direct request failed:", directError)
            setError("Unable to load dashboard data. Please try again later.")
          }
        }
      } catch (e) {
        console.error("Dashboard fetch error:", e)
        setError("Unable to load dashboard data. Please try again later.")
      } finally {
        setIsLoading(false)
      }
    }

    fetchDashboardData()
  }, [])

  if (isLoading) {
    return (
      <div className="space-y-8">
        {/* Loading skeleton for hero section */}
        <div className="space-y-4">
          <Skeleton className="h-8 w-48" />
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
                    <Skeleton className="h-6 w-24" />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
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

  // Combine current user with other users and sort by sessions this year (descending)
  const allUsers = [dashboardData.current_user, ...dashboardData.other_users].sort((a, b) => {
    return b.total_sessions_this_year - a.total_sessions_this_year
  })

  return (
    <div className="space-y-8">
      {/* Section 1: Your Stats (Hero Section) - Now with 4 tiles */}
      <div className="space-y-4">
        <div className="flex flex-col gap-2">
          <h1 className="text-3xl font-bold tracking-tight">Your Stats</h1>
          <p className="text-muted-foreground">Your personal surf session statistics</p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {/* Sessions Tile */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Sessions</CardTitle>
              <Waves className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <div className="text-2xl font-bold">{dashboardData.current_user.total_sessions_this_year}</div>
                <p className="text-xs text-muted-foreground">This year ({new Date().getFullYear()})</p>
              </div>
              <div>
                <div className="text-lg font-semibold">
                  {Number.parseFloat(dashboardData.current_user.sessions_per_week_this_year).toFixed(1)}
                </div>
                <p className="text-xs text-muted-foreground">Sessions per week</p>
              </div>
              <div>
                <div className="text-lg font-semibold">{dashboardData.current_user.total_sessions_all_time}</div>
                <p className="text-xs text-muted-foreground">All-time sessions</p>
              </div>
            </CardContent>
          </Card>

          {/* Fun Tile */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Fun</CardTitle>
              <Trophy className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <div className="text-2xl font-bold">
                  {Number.parseFloat(dashboardData.current_user.avg_fun_rating_this_year).toFixed(1)}/10
                </div>
                <p className="text-xs text-muted-foreground">Average fun rating</p>
              </div>
            </CardContent>
          </Card>

          {/* Time Tile */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Time</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <div className="text-2xl font-bold">
                  {formatMinutesToHours(dashboardData.current_user.total_surf_time_minutes_this_year)}
                </div>
                <p className="text-xs text-muted-foreground">Total surf time this year</p>
              </div>
              <div>
                <div className="text-lg font-semibold">
                  {formatMinutesToHours(dashboardData.current_user.avg_session_duration_minutes_this_year)}
                </div>
                <p className="text-xs text-muted-foreground">Average session</p>
              </div>
            </CardContent>
          </Card>

          {/* Top Spots Tile */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Top Spots</CardTitle>
              <MapPin className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent className="space-y-3">
              {dashboardData.current_user.top_locations && dashboardData.current_user.top_locations.length > 0 ? (
                dashboardData.current_user.top_locations.slice(0, 3).map((location, index) => (
                  <div key={index}>
                    <div className={`${index === 0 ? "text-2xl font-bold" : "text-lg font-semibold"}`}>
                      {capitalizeLocation(location.location)}
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {location.session_count} session{location.session_count !== 1 ? "s" : ""}
                    </p>
                  </div>
                ))
              ) : (
                <div>
                  <div className="text-2xl font-bold">No sessions</div>
                  <p className="text-xs text-muted-foreground">logged yet</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Section 2: Sessions Leaderboard (Table) */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold tracking-tight">Sessions Leaderboard</h2>
            <p className="text-muted-foreground">{new Date().getFullYear()}</p>
          </div>
          <Link
            href="/sessions"
            className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2"
          >
            View All Sessions
          </Link>
        </div>

        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Rank</TableHead>
                <TableHead>Surfer</TableHead>
                <TableHead>Sessions</TableHead>
                <TableHead>Total Time (hours)</TableHead>
                <TableHead>Sessions/Week</TableHead>
                <TableHead>Avg Rating (out of 10)</TableHead>
                <TableHead>Avg Duration (hours)</TableHead>
                <TableHead>All-Time Sessions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {allUsers.length > 0 ? (
                allUsers.map((user, index) => (
                  <TableRow
                    key={user.user_id}
                    className={user.user_id === dashboardData.current_user.user_id ? "bg-muted/50" : ""}
                  >
                    <TableCell className="font-medium">#{index + 1}</TableCell>
                    <TableCell className="font-medium">
                      {user.display_name}
                      {user.user_id === dashboardData.current_user.user_id && (
                        <span className="ml-2 text-xs text-muted-foreground">(You)</span>
                      )}
                    </TableCell>
                    <TableCell className="font-semibold">{user.total_sessions_this_year}</TableCell>
                    <TableCell>{formatMinutesToHoursValue(user.total_surf_time_minutes_this_year)}</TableCell>
                    <TableCell>{Number.parseFloat(user.sessions_per_week_this_year).toFixed(2)}</TableCell>
                    <TableCell>{Number.parseFloat(user.avg_fun_rating_this_year).toFixed(1)}</TableCell>
                    <TableCell>{formatMinutesToHoursValue(user.avg_session_duration_minutes_this_year)}</TableCell>
                    <TableCell>{user.total_sessions_all_time}</TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={8} className="h-24 text-center">
                    No surfers found.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      </div>

      {/* Section 3: Community Stats (Footer Section) */}
      <div className="space-y-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Community Stats</h2>
          <p className="text-muted-foreground">Overall community metrics</p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Sessions</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.community.total_sessions}</div>
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
                {Number.parseFloat(dashboardData.community.total_stoke).toFixed(0)}
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
              {dashboardData.community.top_location ? (
                <>
                  <div className="text-2xl font-bold">
                    {capitalizeLocation(dashboardData.community.top_location.location)}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {dashboardData.community.top_location.session_count} sessions
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
                {formatMinutesToHours(dashboardData.community.total_surf_time_minutes)}
              </div>
              <p className="text-xs text-muted-foreground">All users combined</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
