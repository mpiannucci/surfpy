"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export function ClientFetchButton() {
  const [isLoading, setIsLoading] = useState(false)
  const [response, setResponse] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [showResults, setShowResults] = useState(false)

  const fetchSessions = async () => {
    setIsLoading(true)
    setError(null)
    setResponse(null)

    try {
      // Get auth token
      const token = localStorage.getItem("auth_token")

      // API URL
      const apiUrl = "https://surfdata-il3yfd0qy-martins-projects-383d438b.vercel.app/api/surf-sessions"

      // Make the request
      const response = await fetch(apiUrl, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
          Authorization: token ? `Bearer ${token}` : "",
        },
        cache: "no-store",
      })

      // Get the response text
      const text = await response.text()

      try {
        // Try to parse as JSON
        const data = JSON.parse(text)
        setResponse({
          status: response.status,
          headers: Object.fromEntries([...response.headers.entries()]),
          data,
        })
      } catch (e) {
        // If parsing fails, show the raw text
        setResponse({
          status: response.status,
          headers: Object.fromEntries([...response.headers.entries()]),
          text: text.substring(0, 1000),
        })
      }

      setShowResults(true)
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="mt-4">
      <Button variant="outline" onClick={fetchSessions} disabled={isLoading}>
        {isLoading ? "Fetching..." : "Fetch Sessions Directly"}
      </Button>

      {showResults && (
        <Card className="mt-4">
          <CardHeader>
            <CardTitle className="flex justify-between">
              <span>Direct API Fetch Results</span>
              <Button variant="outline" size="sm" onClick={() => setShowResults(false)}>
                Hide
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {error ? (
              <div className="p-4 bg-destructive/10 text-destructive rounded-md">
                <p>Error: {error}</p>
              </div>
            ) : response ? (
              <div className="space-y-4">
                <div>
                  <h3 className="text-sm font-medium mb-2">Status: {response.status}</h3>
                </div>

                <div>
                  <h3 className="text-sm font-medium mb-2">Headers:</h3>
                  <pre className="text-xs bg-muted p-2 rounded-md overflow-auto max-h-40">
                    {JSON.stringify(response.headers, null, 2)}
                  </pre>
                </div>

                <div>
                  <h3 className="text-sm font-medium mb-2">Response:</h3>
                  <pre className="text-xs bg-muted p-2 rounded-md overflow-auto max-h-96">
                    {response.data ? JSON.stringify(response.data, null, 2) : response.text}
                  </pre>
                </div>

                {response.data && response.data.data && Array.isArray(response.data.data) && (
                  <div>
                    <h3 className="text-sm font-medium mb-2">Sessions Count: {response.data.data.length}</h3>
                  </div>
                )}
              </div>
            ) : (
              <p>No response data</p>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
