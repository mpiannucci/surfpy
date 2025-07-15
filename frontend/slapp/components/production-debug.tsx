"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export function ProductionDebug() {
  const [showDebug, setShowDebug] = useState(false)
  const [apiResponse, setApiResponse] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [networkInfo, setNetworkInfo] = useState<any>(null)

  // Get network information
  useEffect(() => {
    if (showDebug) {
      setNetworkInfo({
        userAgent: navigator.userAgent,
        online: navigator.onLine,
        hostname: window.location.hostname,
        protocol: window.location.protocol,
        cookies: document.cookie ? "Present" : "None",
        localStorage: typeof localStorage !== "undefined" ? "Available" : "Unavailable",
      })
    }
  }, [showDebug])

  const testApiConnection = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const token = localStorage.getItem("auth_token")
      const userData = JSON.parse(localStorage.getItem("user_data") || "{}")

      // API URL
      const apiUrl = "https://surfdata-il3yfd0qy-martins-projects-383d438b.vercel.app/api/surf-sessions"

      // Try direct fetch first
      try {
        console.log("Testing direct API connection")
        const directResponse = await fetch(apiUrl, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            Authorization: token ? `Bearer ${token}` : "",
          },
        })

        const directText = await directResponse.text()
        let directData
        try {
          directData = JSON.parse(directText)
        } catch (e) {
          directData = { text: directText }
        }

        setApiResponse({
          direct: {
            status: directResponse.status,
            statusText: directResponse.statusText,
            headers: Object.fromEntries([...directResponse.headers.entries()]),
            data: directData,
          },
          auth: {
            token: token ? "Present (hidden)" : "Missing",
            user: userData,
          },
        })
      } catch (directError) {
        console.error("Direct API test failed:", directError)

        // Try with proxy
        try {
          console.log("Testing proxy API connection")
          const proxyResponse = await fetch("/api/auth/cors-proxy", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              url: apiUrl,
              method: "GET",
              headers: {
                Authorization: token ? `Bearer ${token}` : "",
              },
            }),
          })

          const proxyData = await proxyResponse.json()

          setApiResponse({
            direct: {
              error: directError.message,
            },
            proxy: {
              status: proxyResponse.status,
              statusText: proxyResponse.statusText,
              data: proxyData,
            },
            auth: {
              token: token ? "Present (hidden)" : "Missing",
              user: userData,
            },
          })
        } catch (proxyError) {
          console.error("Proxy API test failed:", proxyError)
          setError(`Direct: ${directError.message}, Proxy: ${proxyError.message}`)
        }
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="mt-8">
      <Button variant="outline" onClick={() => setShowDebug(!showDebug)}>
        {showDebug ? "Hide" : "Show"} Production Debug
      </Button>

      {showDebug && (
        <Card className="mt-4">
          <CardHeader>
            <CardTitle>Production Debug Information</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {networkInfo && (
                <div className="p-4 bg-muted rounded-md">
                  <h3 className="text-sm font-medium mb-2">Network Information:</h3>
                  <pre className="text-xs overflow-auto max-h-40">{JSON.stringify(networkInfo, null, 2)}</pre>
                </div>
              )}

              <div>
                <p className="text-sm text-muted-foreground">
                  Auth Token: {localStorage.getItem("auth_token") ? "Present (hidden)" : "Missing"}
                </p>
                <p className="text-sm text-muted-foreground">
                  User Data: {localStorage.getItem("user_data") || "None"}
                </p>
              </div>

              <Button onClick={testApiConnection} disabled={isLoading}>
                {isLoading ? "Testing..." : "Test API Connection"}
              </Button>

              {error && (
                <div className="p-4 bg-destructive/10 text-destructive rounded-md">
                  <p>Error: {error}</p>
                </div>
              )}

              {apiResponse && (
                <div className="p-4 bg-muted rounded-md overflow-auto max-h-96">
                  <pre className="text-xs">{JSON.stringify(apiResponse, null, 2)}</pre>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
