import { type NextRequest, NextResponse } from "next/server"

// Update the Flask API URL
const FLASK_API_URL = "https://surfdata-hs9191va8-martins-projects-383d438b.vercel.app"

export async function POST(request: NextRequest) {
  try {
    // Get the request body
    const body = await request.json()

    console.log("Proxying request to Flask API:", body)

    // Forward the request to the Flask API
    const response = await fetch(FLASK_API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify(body),
    })

    // Check content type to handle different response types
    const contentType = response.headers.get("content-type")
    console.log("Response content type:", contentType)

    if (contentType && contentType.includes("application/json")) {
      // Handle JSON response
      const data = await response.json()
      return NextResponse.json(data, { status: response.status })
    } else {
      // Handle non-JSON response (like HTML)
      const text = await response.text()
      console.log("Non-JSON response received:", text.substring(0, 200) + "...")

      // Return a more helpful error
      return NextResponse.json(
        {
          error: "The API returned a non-JSON response",
          details: "The API might be returning an HTML error page or is not configured correctly.",
        },
        { status: 500 },
      )
    }
  } catch (error) {
    console.error("Error in API route:", error)

    // Return a 500 error
    return NextResponse.json(
      {
        error: "Failed to communicate with the Flask API",
        details: error instanceof Error ? error.message : String(error),
      },
      { status: 500 },
    )
  }
}
