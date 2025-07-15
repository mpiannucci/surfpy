"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export function DebugAuth() {
  const [showDebug, setShowDebug] = useState(false)
  const [authData, setAuthData] = useState<any>(null)
  const [apiResponse, setApiResponse] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Only show in development or if forced
  if (process.env.NODE_ENV !== "development" && !showDebug) {
    return (
      <Button variant="outline" size="sm" onClick={() => setShowDebug(true)}>
        Show Debug
      </Button>
    )
  }

  const checkAuth = () => {
    try {
      const token = localStorage.getItem("auth_token")
      const userData = localStorage.getItem("user_data")

      setAuthData({
        token: token ? "Present (hidden)" : "Missing",
        userData: userData ? JSON.parse(userData) : null,
        isAuthenticated: !!token && !!userData,
      })
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    }
  }

  const testApiConnection = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const token = localStorage.getItem("auth_token")

      // Use our CORS proxy
      const response = await fetch("/api/auth/cors-proxy", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          url: "https://surfdata-il3yfd0qy-martins-projects-383d438b.vercel.app/api/surf-sessions",
          method: "GET",
          headers: {
            Authorization: token ? `Bearer ${token}` : "",
          },
        }),
      })

      const responseData = await response.json()

      // Log the full response structure to help debug
      console.log("Full API response:", JSON.stringify(responseData, null, 2))

      setApiResponse({
        status: response.status,
        data: responseData,
        // Add a processed version of the data to help debug
        processedData: processApiResponse(responseData),
      })
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setIsLoading(false)
    }
  }

  // Helper function to process the API response and extract sessions
  function processApiResponse(response: any): any {
    try {
      // Check for data.data structure
      if (response.data && response.data.data && Array.isArray(response.data.data)) {
        return {
          source: "data.data",
          count: response.data.data.length,
          sample: response.data.data.slice(0, 1),
        }
      }

      // Check for direct data array
      if (response.data && Array.isArray(response.data)) {
        return {
          source: "data",
          count: response.data.length,
          sample: response.data.slice(0, 1),
        }
      }

      // Check if the result itself is the array
      if (Array.isArray(response)) {
        return {
          source: "root",
          count: response.length,
          sample: response.slice(0, 1),
        }
      }

      return {
        source: "unknown",
        structure: Object.keys(response),
      }
    } catch (e) {
      return {
        error: String(e),
      }
    }
  }

  return (
    <Card className="mt-4">
      <CardHeader>
        <CardTitle>Auth Debug Information</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex gap-2">
            <Button onClick={checkAuth} variant="outline" size="sm">
              Check Auth
            </Button>
            <Button onClick={testApiConnection} disabled={isLoading} variant="outline" size="sm">
              {isLoading ? "Testing..." : "Test API Connection"}
            </Button>
            <Button onClick={() => setShowDebug(false)} variant="outline" size="sm">
              Hide Debug
            </Button>
          </div>

          {authData && (
            <div className="p-4 bg-muted rounded-md">
              <h3 className="text-sm font-medium mb-2">Auth Data:</h3>
              <pre className="text-xs overflow-auto max-h-40">{JSON.stringify(authData, null, 2)}</pre>
            </div>
          )}

          {error && (
            <div className="p-4 bg-destructive/10 text-destructive rounded-md">
              <p>Error: {error}</p>
            </div>
          )}

          {apiResponse && (
            <div className="p-4 bg-muted rounded-md overflow-auto max-h-96">
              <h3 className="text-sm font-medium mb-2">API Response:</h3>
              <div className="mb-4">
                <h4 className="text-xs font-medium">Processed Data:</h4>
                <pre className="text-xs">{JSON.stringify(apiResponse.processedData, null, 2)}</pre>
              </div>
              <h4 className="text-xs font-medium">Full Response:</h4>
              <pre className="text-xs">{JSON.stringify(apiResponse.data, null, 2)}</pre>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
