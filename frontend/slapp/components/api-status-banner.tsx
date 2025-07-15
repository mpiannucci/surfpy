"use client"

import { useEffect, useState } from "react"
import { AlertCircle } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

export function ApiStatusBanner() {
  const [isOffline, setIsOffline] = useState(false)

  useEffect(() => {
    async function checkApiStatus() {
      try {
        const response = await fetch(
          "https://surfdata-b4vwwr6iw-martins-projects-383d438b.vercel.app/api/surf-sessions",
          { method: "HEAD", cache: "no-store" },
        )
        setIsOffline(!response.ok)
      } catch (error) {
        setIsOffline(true)
      }
    }

    checkApiStatus()
  }, [])

  if (!isOffline) return null

  return (
    <Alert variant="destructive" className="mb-6">
      <AlertCircle className="h-4 w-4" />
      <AlertTitle>API Offline</AlertTitle>
      <AlertDescription>The API server is currently offline. Showing fallback data instead.</AlertDescription>
    </Alert>
  )
}
