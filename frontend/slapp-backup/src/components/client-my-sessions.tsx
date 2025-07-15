"use client"

import { useState, useEffect } from "react"
import { MySessionsTable } from "./my-sessions-table"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"
import { AlertCircle } from "lucide-react"

// Updated API URL with the new endpoint
const API_BASE_URL = "https://surfdata-hs9191va8-martins-projects-383d438b.vercel.app"

// Get auth token from localStorage
function getAuthToken(): string | null {
  if (typeof window !== "undefined") {
    return localStorage.getItem("auth_token")
  }
  return null
}

// Check if user is authenticated
function isAuthenticated(): boolean {
  if (typeof window === "undefined") {
    return false
  }

  const token = getAuthToken()
  const userData = localStorage.getItem("user_data")

  return !!token && !!userData
}

// Helper function for fetching with proxy
async function fetchWithProxy(url: string, options: RequestInit) {
  const proxyResponse = await fetch("/api/auth/cors-proxy", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      url: url,
      method: options.method || "GET",
      headers: options.headers,
    }),
    cache: "no-store",
  })

  if (!proxyResponse.ok) {
    throw new Error(`Proxy request failed: ${proxyResponse.status} ${proxyResponse.statusText}`)
  }

  return await proxyResponse.json()
}

export function ClientMySessions() {
  const [sessions, setSessions] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchMySessions = async () => {
    try {
      setLoading(true)
      setError(null)

      // Check if user is authenticated first
      if (!isAuthenticated()) {
        setError("Authentication required to view your sessions")
        return
      }

      // Get auth token
      const token = getAuthToken()
      console.log("Fetching my sessions with auth token:", token ? "Present" : "Missing")

      // Prepare headers
      const headers = {
        "Content-Type": "application/json",
        Accept: "application/json",
        Authorization: token ? `Bearer ${token}` : "",
      }

      // Try proxy first (more reliable for CORS issues)
      try {
        console.log("Attempting fetch with proxy and user_only=true")
        const proxyData = await fetchWithProxy(`${API_BASE_URL}/api/surf-sessions?user_only=true`, {
          method: "GET",
          headers,
        })

        console.log("Proxy fetch successful")

        // Handle the proxy response format
        let sessionsData = []
        if (proxyData.data && Array.isArray(proxyData.data)) {
          sessionsData = proxyData.data
        } else if (Array.isArray(proxyData)) {
          sessionsData = proxyData
        } else {
          console.error("Unexpected proxy response format:", proxyData)
          throw new Error("Unexpected response format")
        }

        // Sort sessions by date and time in descending order (most recent first)
        sessionsData.sort((a, b) => {
          const dateA = new Date(a.date + "T" + (a.time || "00:00:00"))
          const dateB = new Date(b.date + "T" + (b.time || "00:00:00"))
          return dateB.getTime() - dateA.getTime()
        })

        console.log(`Fetched and sorted ${sessionsData.length} user sessions via proxy`)
        setSessions(sessionsData)
      } catch (proxyError) {
        console.error("Proxy fetch failed:", proxyError)

        // If proxy fails, try direct request
        try {
          console.log("Attempting direct fetch to API with user_only=true")
          const response = await fetch(`${API_BASE_URL}/api/surf-sessions?user_only=true`, {
            method: "GET",
            headers,
            cache: "no-store",
          })

          if (!response.ok) {
            throw new Error(`Direct fetch failed: ${response.status} ${response.statusText}`)
          }

          const text = await response.text()
          console.log("Direct fetch response text (first 100 chars):", text.substring(0, 100))

          try {
            // Try to parse as JSON
            const data = JSON.parse(text)
            console.log("Direct fetch successful, parsed JSON")

            // Handle the response format
            let sessionsData = []
            if (data.data && Array.isArray(data.data)) {
              sessionsData = data.data
            } else if (Array.isArray(data)) {
              sessionsData = data
            } else {
              console.error("Unexpected response format:", data)
              throw new Error("Unexpected response format")
            }

            // Sort sessions by date and time in descending order (most recent first)
            sessionsData.sort((a, b) => {
              const dateA = new Date(a.date + "T" + (a.time || "00:00:00"))
              const dateB = new Date(b.date + "T" + (b.time || "00:00:00"))
              return dateB.getTime() - dateA.getTime()
            })

            console.log(`Fetched and sorted ${sessionsData.length} user sessions`)
            setSessions(sessionsData)
          } catch (e) {
            console.error("Error parsing direct fetch response as JSON:", e)
            throw new Error("Invalid response format from server")
          }
        } catch (directError) {
          console.error("Direct fetch failed:", directError)
          throw new Error("Failed to fetch your sessions. Please check your connection and try again.")
        }
      }
    } catch (error) {
      console.error("Error in fetchMySessions:", error)
      setError(error instanceof Error ? error.message : "An error occurred while fetching your sessions")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchMySessions()
  }, [])

  if (loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-full" />
        <Skeleton className="h-8 w-full" />
        <Skeleton className="h-8 w-full" />
        <Skeleton className="h-8 w-full" />
        <Skeleton className="h-8 w-full" />
      </div>
    )
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    )
  }

  if (sessions.length === 0) {
    return (
      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          You haven't logged any surf sessions yet. Click "Add Session" to get started!
        </AlertDescription>
      </Alert>
    )
  }

  return <MySessionsTable sessions={sessions} onSessionsChange={fetchMySessions} />
}
