"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Loader2 } from "lucide-react"

export function ApiTester() {
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState<string | null>(null)
  const [rawResponse, setRawResponse] = useState<string | null>(null)

  const testApi = async () => {
    try {
      setIsLoading(true)
      setResults(null)
      setRawResponse(null)

      const token = localStorage.getItem("auth_token")
      if (!token) {
        setResults("No auth token found. Please log in first.")
        return
      }

      const apiUrl = "https://surfdata-hs9191va8-martins-projects-383d438b.vercel.app/api/surf-sessions"
      let resultsText = "API Test Results:\n\n"

      // Try proxy fetch
      try {
        resultsText += "Testing via CORS Proxy...\n"
        console.log("API Tester - Attempting fetch via proxy")

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
              Accept: "application/json",
            },
          }),
        })

        if (!proxyResponse.ok) {
          resultsText += `Proxy request failed: ${proxyResponse.status} ${proxyResponse.statusText}\n`
        } else {
          const text = await proxyResponse.text()
          setRawResponse(text)
          resultsText += `Proxy response received (${text.length} chars)\n`

          try {
            const data = JSON.parse(text)

            // Check for user_email fields
            let hasUserEmail = false
            let emailSamples = []

            if (data.data && Array.isArray(data.data) && data.data.length > 0) {
              hasUserEmail = data.data.some((item: any) => !!item.user_email)
              emailSamples = data.data
                .slice(0, 5)
                .map((item: any, i: number) => `Session ${i} (ID: ${item.id}): ${item.user_email || "MISSING"}`)

              resultsText += `Response format: { data: [...] } with ${data.data.length} items\n`
            } else if (Array.isArray(data) && data.length > 0) {
              hasUserEmail = data.some((item: any) => !!item.user_email)
              emailSamples = data
                .slice(0, 5)
                .map((item: any, i: number) => `Session ${i} (ID: ${item.id}): ${item.user_email || "MISSING"}`)

              resultsText += `Response format: Direct array with ${data.length} items\n`
            } else {
              resultsText += `Response format: Unknown structure\n`
            }

            resultsText += `Contains user_email fields: ${hasUserEmail ? "YES" : "NO"}\n`
            resultsText += "Sample user_email values:\n"
            resultsText += emailSamples.join("\n") + "\n\n"
          } catch (e) {
            resultsText += `Error parsing JSON: ${e}\n`
            resultsText += `Raw response: ${text.substring(0, 200)}...\n`
          }
        }
      } catch (e) {
        console.error("API Tester - Proxy fetch failed:", e)
        resultsText += `Proxy fetch error: ${e}\n`
      }

      setResults(resultsText)
    } catch (e) {
      console.error("API Tester - Error:", e)
      setResults(`Error during API test: ${e}`)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>API Tester</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <Button onClick={testApi} disabled={isLoading} className="w-full">
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Testing API...
              </>
            ) : (
              "Test API Connection"
            )}
          </Button>

          {results && (
            <div className="mt-4">
              <h3 className="text-sm font-medium mb-2">Test Results:</h3>
              <div className="bg-black text-green-400 p-3 rounded-md text-xs overflow-auto max-h-60 whitespace-pre-wrap">
                {results}
              </div>
            </div>
          )}

          {rawResponse && (
            <div className="mt-4">
              <h3 className="text-sm font-medium mb-2">Raw API Response:</h3>
              <div className="bg-gray-100 dark:bg-gray-800 p-3 rounded-md text-xs overflow-auto max-h-60">
                <pre>{rawResponse}</pre>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
