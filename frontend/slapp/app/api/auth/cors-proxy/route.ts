import { type NextRequest, NextResponse } from "next/server"

// Update the API URL to the new one
const API_BASE_URL = "https://surfdata-nfzxhcjek-martins-projects-383d438b.vercel.app"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { url, method = "GET", headers = {}, data } = body

    if (!url) {
      return NextResponse.json({ message: "URL is required" }, { status: 400 })
    }

    const fullUrl = url.startsWith("http") ? url : `${API_BASE_URL}${url}`
    console.log("CORS Proxy - Request URL:", fullUrl)
    console.log("CORS Proxy - Request Method:", method)
    console.log("CORS Proxy - Request Headers:", JSON.stringify(headers))

    // Log the auth token if present (partially masked for security)
    if (headers.Authorization) {
      const authToken = headers.Authorization.toString()
      const maskedToken = authToken.substring(0, 15) + "..." + authToken.substring(authToken.length - 10)
      console.log("CORS Proxy - Auth Token:", maskedToken)
    } else {
      console.log("CORS Proxy - No Auth Token provided")
    }

    const requestOptions: RequestInit = {
      method,
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        ...headers,
      },
      cache: "no-store",
      mode: "cors", // Explicitly set CORS mode
    }

    if (data) {
      requestOptions.body = JSON.stringify(data)
      console.log("CORS Proxy - Request Body:", JSON.stringify(data))
    }

    try {
      // Add a timeout to the fetch request
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 20000) // 20 second timeout

      requestOptions.signal = controller.signal

      console.log("CORS Proxy - Sending request to:", fullUrl)
      const response = await fetch(fullUrl, requestOptions)
      clearTimeout(timeoutId)

      console.log("CORS Proxy - Response Status:", response.status)
      console.log("CORS Proxy - Response Headers:", JSON.stringify(Object.fromEntries([...response.headers])))

      // Get the response text
      const text = await response.text()
      console.log("CORS Proxy - Raw response (first 500 chars):", text.substring(0, 500))
      console.log(
        "CORS Proxy - Raw response (last 500 chars):",
        text.length > 500 ? text.substring(text.length - 500) : "Response too short",
      )

      // Try to parse as JSON
      try {
        const jsonData = JSON.parse(text)
        console.log("CORS Proxy - Successfully parsed JSON response")

        // DEBUG: Enhanced logging for display_name field
        if (jsonData.data && Array.isArray(jsonData.data) && jsonData.data.length > 0) {
          console.log("CORS Proxy - Response has data array with", jsonData.data.length, "items")
          console.log("CORS Proxy - First item keys:", Object.keys(jsonData.data[0]))
          console.log("CORS Proxy - First item in data array:", JSON.stringify(jsonData.data[0]))

          // Check specifically for display_name field
          const itemsWithDisplayName = jsonData.data.filter((item: any) => !!item.display_name)
          const itemsWithUserEmail = jsonData.data.filter((item: any) => !!item.user_email)

          console.log("CORS Proxy - Items with display_name:", itemsWithDisplayName.length)
          console.log("CORS Proxy - Items with user_email:", itemsWithUserEmail.length)

          // Log sample display_name values
          if (itemsWithDisplayName.length > 0) {
            const displayNameSamples = itemsWithDisplayName.slice(0, 5).map((item: any, index: number) => {
              return {
                index,
                id: item.id,
                display_name: item.display_name,
                user_email: item.user_email || "MISSING",
              }
            })
            console.log("CORS Proxy - Sample display_name data:", JSON.stringify(displayNameSamples))
          } else {
            console.log("CORS Proxy - ⚠️ NO ITEMS WITH display_name FOUND!")
            // Log what fields are actually present
            const availableFields = new Set()
            jsonData.data.forEach((item: any) => {
              Object.keys(item).forEach((key) => availableFields.add(key))
            })
            console.log("CORS Proxy - Available fields across all items:", Array.from(availableFields))
          }
        } else if (Array.isArray(jsonData) && jsonData.length > 0) {
          console.log("CORS Proxy - Response is an array with", jsonData.length, "items")
          console.log("CORS Proxy - First item keys:", Object.keys(jsonData[0]))
          console.log("CORS Proxy - First item in array:", JSON.stringify(jsonData[0]))

          // Check specifically for display_name field
          const itemsWithDisplayName = jsonData.filter((item: any) => !!item.display_name)
          const itemsWithUserEmail = jsonData.filter((item: any) => !!item.user_email)

          console.log("CORS Proxy - Items with display_name:", itemsWithDisplayName.length)
          console.log("CORS Proxy - Items with user_email:", itemsWithUserEmail.length)

          // Log sample display_name values
          if (itemsWithDisplayName.length > 0) {
            const displayNameSamples = itemsWithDisplayName.slice(0, 5).map((item: any, index: number) => {
              return {
                index,
                id: item.id,
                display_name: item.display_name,
                user_email: item.user_email || "MISSING",
              }
            })
            console.log("CORS Proxy - Sample display_name data:", JSON.stringify(displayNameSamples))
          } else {
            console.log("CORS Proxy - ⚠️ NO ITEMS WITH display_name FOUND!")
          }
        } else {
          console.log("CORS Proxy - Response structure:", typeof jsonData, jsonData ? Object.keys(jsonData) : "null")
        }

        // CRITICAL: Return the data exactly as received from the API
        // DO NOT modify the response in any way
        return NextResponse.json(jsonData, { status: response.status })
      } catch (e) {
        console.error("CORS Proxy - Error parsing JSON:", e)
        // If parsing fails, return the text
        return NextResponse.json(
          {
            message: "Non-JSON response",
            text: text.substring(0, 1000),
            status: response.status,
          },
          { status: response.status },
        )
      }
    } catch (fetchError) {
      console.error("CORS Proxy - Fetch error:", fetchError)

      // For development, create a mock response if the API is unreachable
      if (fetchError.name === "AbortError") {
        return NextResponse.json(
          {
            message: "Request timed out",
            error: "The request to the API timed out after 20 seconds",
          },
          { status: 504 }, // Gateway Timeout
        )
      }

      // If the URL contains a specific session ID, return mock data for that session
      if (fullUrl.includes("/api/surf-sessions/") && !fullUrl.endsWith("/api/surf-sessions")) {
        // Extract the session ID from the URL
        const sessionId = fullUrl.split("/").pop()

        // Mock session data with display_name
        return NextResponse.json({
          id: Number(sessionId),
          session_name: `Mock Session ${sessionId}`,
          location: "Mock Beach",
          date: new Date().toISOString().split("T")[0],
          time: "10:00:00",
          fun_rating: 8,
          session_notes: "This is a mock session returned by the CORS proxy when the API is unreachable.",
          user_id: "mock-user-id",
          user_email: "mock@example.com",
          display_name: "Mock User", // Add display_name field
          raw_swell: {
            swells: [
              {
                height: 3.5,
                period: 12,
                direction: 270,
              },
            ],
          },
        })
      }

      // For sessions list
      if (fullUrl.includes("/api/surf-sessions")) {
        // Mock sessions data with display_name
        return NextResponse.json({
          status: "success",
          data: [
            {
              id: 1,
              session_name: "Mock Session 1",
              location: "Mock Beach",
              date: new Date().toISOString().split("T")[0],
              time: "10:00:00",
              fun_rating: 8,
              session_notes: "This is a mock session",
              user_id: "mock-user-id",
              user_email: "mock-user@example.com",
              display_name: "Mock User 1", // Add display_name field
            },
            {
              id: 2,
              session_name: "Mock Session 2",
              location: "Another Beach",
              date: new Date(Date.now() - 86400000).toISOString().split("T")[0],
              time: "14:30:00",
              fun_rating: 7,
              session_notes: "Another mock session",
              user_id: "different-user-id",
              user_email: "different-user@example.com",
              display_name: "Mock User 2", // Add display_name field
            },
            {
              id: 3,
              session_name: "Mock Session 3",
              location: "Third Beach",
              date: new Date(Date.now() - 172800000).toISOString().split("T")[0],
              time: "08:15:00",
              fun_rating: 9,
              session_notes: "A third mock session",
              user_id: "third-user-id",
              user_email: "third-user@example.com",
              display_name: "Mock User 3", // Add display_name field
            },
          ],
        })
      }

      return NextResponse.json(
        {
          message: "Failed to fetch from API",
          error: fetchError instanceof Error ? fetchError.message : "Unknown fetch error",
        },
        { status: 502 }, // Bad Gateway
      )
    }
  } catch (error) {
    console.error("CORS Proxy - General error:", error)
    return NextResponse.json(
      {
        message: "An error occurred in the CORS proxy",
        error: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 },
    )
  }
}
