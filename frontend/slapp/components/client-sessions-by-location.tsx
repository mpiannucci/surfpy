"use client"

import { useState, useEffect, useMemo } from "react"
import { LocationSessionsTable } from "./location-sessions-table"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Card } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Slider } from "@/components/ui/slider"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { AlertCircle, ListFilter } from "lucide-react"
import { subDays, startOfDay } from "date-fns"
import type { SurfSession } from "@/lib/types"

interface ClientSessionsByLocationProps {
  location: string
}

export function ClientSessionsByLocation({ location }: ClientSessionsByLocationProps) {
  const [masterSessionList, setMasterSessionList] = useState<SurfSession[]>([])
  const [displayedSessions, setDisplayedSessions] = useState<SurfSession[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Filter states
  const [dateRange, setDateRange] = useState("all")
  const [minRating, setMinRating] = useState(0)
  const [sortBy, setSortBy] = useState("newest")

  useEffect(() => {
    const fetchSessionsByLocation = async () => {
      if (!location) return

      setIsLoading(true)
      setError(null)

      try {
        const token = localStorage.getItem("auth_token")
        if (!token) throw new Error("Authentication token not found.")

        const response = await fetch("/api/auth/cors-proxy", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            url: `https://surfdata-4kuzgt1ku-martins-projects-383d438b.vercel.app/api/surf-sessions/location/${location}`,
            method: "GET",
            headers: { Authorization: `Bearer ${token}` },
          }),
        })

        if (!response.ok) {
          if (response.status === 404) {
            setMasterSessionList([]) // No sessions found, not an error
          } else {
            throw new Error(`Failed to fetch sessions: ${response.statusText}`)
          }
        } else {
            const result = await response.json()
            if (result.status === 'success') {
                 setMasterSessionList(result.data || [])
            } else if (result.message === 'No sessions found for location') {
                setMasterSessionList([])
            } else {
                throw new Error(result.message || 'Invalid data format from API')
            }
        }
      } catch (err: any) {
        setError(err.message)
      } finally {
        setIsLoading(false)
      }
    }

    fetchSessionsByLocation()
  }, [location])

  useEffect(() => {
    let filtered = [...masterSessionList]

    // Apply date range filter
    if (dateRange !== "all") {
      const now = new Date()
      const days = parseInt(dateRange, 10)
      const cutoffDate = startOfDay(subDays(now, days))
      filtered = filtered.filter(s => new Date(s.date) >= cutoffDate)
    }

    // Apply minimum rating filter
    if (minRating > 0) {
      filtered = filtered.filter(s => parseInt(s.fun_rating, 10) >= minRating)
    }

    // Apply sorting
    if (sortBy === "newest") {
      filtered.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
    } else if (sortBy === "highest_rated") {
      filtered.sort((a, b) => parseInt(b.fun_rating, 10) - parseInt(a.fun_rating, 10))
    }

    setDisplayedSessions(filtered)
  }, [masterSessionList, dateRange, minRating, sortBy])

  if (isLoading) {
    return <Skeleton className="h-48 w-full" />
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    )
  }

  return (
    <div className="space-y-6">
        <h2 className="text-2xl font-bold tracking-tight">Logged Sessions at this Spot</h2>
        <Card className="p-4 bg-background/20 border-border/30">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
                 <div className="col-span-1 md:col-span-3 font-semibold flex items-center gap-2">
                    <ListFilter className="h-5 w-5"/>
                    Filter & Sort
                </div>
                <div>
                    <Label htmlFor="date-range">Date Range</Label>
                    <Select value={dateRange} onValueChange={setDateRange}>
                        <SelectTrigger id="date-range"><SelectValue /></SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">All Time</SelectItem>
                            <SelectItem value="30">Last 30 Days</SelectItem>
                            <SelectItem value="90">Last 90 Days</SelectItem>
                            <SelectItem value="365">Last Year</SelectItem>
                        </SelectContent>
                    </Select>
                </div>
                <div>
                    <Label htmlFor="min-rating">Min Fun Rating: {minRating}</Label>
                    <Slider id="min-rating" min={0} max={10} step={1} value={[minRating]} onValueChange={(value) => setMinRating(value[0])} />
                </div>
                <div>
                    <Label htmlFor="sort-by">Sort By</Label>
                    <Select value={sortBy} onValueChange={setSortBy}>
                        <SelectTrigger id="sort-by"><SelectValue /></SelectTrigger>
                        <SelectContent>
                            <SelectItem value="newest">Newest First</SelectItem>
                            <SelectItem value="highest_rated">Highest Rated</SelectItem>
                        </SelectContent>
                    </Select>
                </div>
            </div>
        </Card>

        <LocationSessionsTable sessions={displayedSessions} />
    </div>
  )
}
