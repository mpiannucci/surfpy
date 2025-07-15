"use client"

import { useState, useEffect } from "react"
import { SessionsTable } from "./sessions-table"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { AlertCircle } from "lucide-react"
import type { SurfSession } from "@/lib/types"

export function ClientSessions() {
  const [sessions, setSessions] = useState<SurfSession[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchSessions()
  }, [])

  const fetchSessions = async () => {
    try {
      setLoading(true)
      setError(null)

      const token = localStorage.getItem("auth_token")
      if (!token) {
        throw new Error("No authentication token found")
      }

      console.log("ClientSessions - Fetching sessions...")

      const response = await fetch("/api/auth/cors-proxy", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({
          url: "https://surfdata-dyoiv3qio-martins-projects-383d438b.vercel.app/api/surf-sessions",
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }),
      })

      if (!response.ok) {
        const errorText = await response.text()
        console.error("ClientSessions - Proxy response not ok:", response.status, errorText)
        throw new Error(`Proxy request failed: ${response.status}`)
      }

      const data = await response.json()
      console.log("ClientSessions - Raw proxy response:", data)

      if (data.error) {
        throw new Error(data.error)
      }

      // Handle different response formats
      let sessionsData: SurfSession[]
      if (data.data && Array.isArray(data.data)) {
        sessionsData = data.data
      } else if (Array.isArray(data)) {
        sessionsData = data
      } else {
        console.error("ClientSessions - Unexpected response format:", data)
        throw new Error("Unexpected response format")
      }

      // Sort sessions by date and time in descending order (most recent first)
      sessionsData.sort((a, b) => {
        const dateA = new Date(a.date + "T" + (a.time || "00:00:00"))
        const dateB = new Date(b.date + "T" + (b.time || "00:00:00"))
        return dateB.getTime() - dateA.getTime()
      })

      console.log("ClientSessions - Processed and sorted sessions:", sessionsData)
      setSessions(sessionsData)
    } catch (error) {
      console.error("ClientSessions - Error fetching sessions:", error)
      setError(error instanceof Error ? error.message : "Failed to fetch sessions")
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="rounded-md border">
          <div className="p-4">
            <Skeleton className="h-4 w-full mb-2" />
            <Skeleton className="h-4 w-3/4 mb-2" />
            <Skeleton className="h-4 w-1/2" />
          </div>
        </div>
        <div className="rounded-md border">
          <div className="p-4">
            <Skeleton className="h-4 w-full mb-2" />
            <Skeleton className="h-4 w-3/4 mb-2" />
            <Skeleton className="h-4 w-1/2" />
          </div>
        </div>
        <div className="rounded-md border">
          <div className="p-4">
            <Skeleton className="h-4 w-full mb-2" />
            <Skeleton className="h-4 w-3/4 mb-2" />
            <Skeleton className="h-4 w-1/2" />
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          Error loading sessions: {error}
          <button onClick={fetchSessions} className="ml-2 underline hover:no-underline">
            Try again
          </button>
        </AlertDescription>
      </Alert>
    )
  }

  return <SessionsTable sessions={sessions} />
}
