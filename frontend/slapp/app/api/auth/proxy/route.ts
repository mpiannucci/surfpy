import { type NextRequest, NextResponse } from "next/server"

// Update the API URL
const API_BASE_URL = "https://surfdata-hs9191va8-martins-projects-383d438b.vercel.app"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { endpoint, email, password } = body

    if (!endpoint || !email || !password) {
      return NextResponse.json({ message: "Missing required fields" }, { status: 400 })
    }

    // Determine the API endpoint based on the requested endpoint
    let apiEndpoint = ""
    if (endpoint === "login") {
      apiEndpoint = `${API_BASE_URL}/api/auth/login`
    } else if (endpoint === "signup") {
      apiEndpoint = `${API_BASE_URL}/api/auth/signup`
    } else {
      return NextResponse.json({ message: "Invalid endpoint" }, { status: 400 })
    }

    console.log(`Making request to: ${apiEndpoint}`)

    // Forward the request to the actual API
    const response = await fetch(apiEndpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({ email, password }),
    })

    // Check content type to determine how to handle the response
    const contentType = response.headers.get("content-type")

    if (contentType && contentType.includes("application/json")) {
      // Handle JSON response
      const responseData = await response.json()
      return NextResponse.json(responseData, { status: response.status })
    } else {
      // Handle non-JSON response (like HTML)
      const text = await response.text()
      console.error("Non-JSON response received:", text.substring(0, 200))

      return NextResponse.json(
        {
          message: "The API returned a non-JSON response",
          error: "API communication error",
          details: `Status: ${response.status}, Content-Type: ${contentType || "unknown"}`,
        },
        { status: 500 },
      )
    }
  } catch (error) {
    console.error("Auth proxy error:", error)
    return NextResponse.json(
      {
        message: "An error occurred while processing your request",
        error: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 },
    )
  }
}
