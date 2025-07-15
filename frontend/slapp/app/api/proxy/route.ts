import { type NextRequest, NextResponse } from "next/server"

const FLASK_API_URL = "https://surfdata-hs9191va8-martins-projects-383d438b.vercel.app/api/surf-sessions"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { url, method = "POST", authToken, data } = body

    console.log("Proxy request:", { url, method, hasAuthToken: !!authToken })

    // Check if this is a forecast request
    const isForecastRequest = url.includes("/api/forecast/")

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    }

    // Add authorization header if token is provided
    if (authToken) {
      headers["Authorization"] = `Bearer ${authToken}`
    }

    const fetchOptions: RequestInit = {
      method: method,
      headers,
    }

    // Only add body for POST requests
    if (method === "POST" && data) {
      fetchOptions.body = JSON.stringify(data)
    }

    console.log("Making external API request to:", url)
    console.log("Request method:", method)
    console.log("Request headers:", headers)

    const response = await fetch(url, fetchOptions)

    console.log("External API response status:", response.status)

    if (!response.ok) {
      const errorText = await response.text()
      console.error("External API error:", errorText)
      return NextResponse.json(
        {
          error: `API request failed: ${response.status}`,
          details: errorText,
        },
        { status: response.status },
      )
    }

    const result = await response.json()
    console.log("External API success, returning data")

    return NextResponse.json(result)
  } catch (error) {
    console.error("Proxy error:", error)
    return NextResponse.json(
      {
        error: "Internal server error",
        details: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 },
    )
  }
}
