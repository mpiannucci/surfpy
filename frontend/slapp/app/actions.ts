"use server"

import { revalidatePath } from "next/cache"
import { supabase } from "@/lib/supabase"

// Update the API URL
const API_URL = "https://surfdata-hs9191va8-martins-projects-383d438b.vercel.app/api/surf-sessions"

// The correct table name
const TABLE_NAME = "surf_sessions_duplicate"

export async function addSurfSession(formData: FormData) {
  try {
    // Extract values from form
    const session_name = formData.get("session_name") as string
    const location = formData.get("location") as string
    const fun_rating = Number(formData.get("fun_rating") as string)
    const date = formData.get("date") as string
    const time = formData.get("time") as string
    const end_time = formData.get("end_time") as string
    const session_notes = (formData.get("session_notes") as string) || ""
    const authToken = formData.get("auth_token") as string
    const taggedUsersJson = formData.get("tagged_users") as string

    // Parse tagged users
    let tagged_users: string[] = []
    if (taggedUsersJson) {
      try {
        tagged_users = JSON.parse(taggedUsersJson)
      } catch (e) {
        console.error("Error parsing tagged users:", e)
        tagged_users = []
      }
    }

    // Validate required fields
    if (!session_name || !location || !date || !time || !end_time || isNaN(fun_rating)) {
      return {
        success: false,
        error: "Please fill in all required fields",
      }
    }

    // Validate fun_rating range
    if (fun_rating < 1 || fun_rating > 10) {
      return {
        success: false,
        error: "Fun rating must be between 1 and 10",
      }
    }

    // Ensure time has seconds
    const timeWithSeconds = time.includes(":") ? (time.split(":").length === 2 ? `${time}:00` : time) : `${time}:00:00`
    const endTimeWithSeconds = end_time.includes(":")
      ? end_time.split(":").length === 2
        ? `${end_time}:00`
        : end_time
      : `${end_time}:00:00`

    // Create request body with exact structure as specified
    const requestBody = {
      session_name,
      location,
      fun_rating,
      date,
      time: timeWithSeconds,
      end_time: endTimeWithSeconds,
      session_notes,
      ...(tagged_users.length > 0 && { tagged_users }), // Only include if there are tagged users
    }

    console.log("Server action: Submitting to API:", requestBody)

    try {
      // Try to send data to the Flask API with auth token
      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${authToken}`,
        },
        body: JSON.stringify(requestBody),
      })

      console.log("Server action: API Response Status:", response.status)

      // Get the response text
      const responseText = await response.text()
      console.log("Server action: API Response Text:", responseText)

      // Check if the response is OK
      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`)
      }

      // Try to parse the response as JSON
      let data
      try {
        if (responseText.trim()) {
          data = JSON.parse(responseText)
        } else {
          data = { message: "Session added successfully (empty response)" }
        }
      } catch (e) {
        console.warn("Server action: Could not parse response as JSON:", e)
        // If we can't parse as JSON, assume success if the status was OK
        data = { message: "Session added successfully (non-JSON response)" }
      }

      // Revalidate the sessions page
      revalidatePath("/sessions")

      return {
        success: true,
        data,
      }
    } catch (apiError) {
      console.error("Server action: API error, falling back to Supabase:", apiError)

      // Fall back to Supabase if the API fails
      try {
        // Ensure time has seconds
        const timeWithSeconds = time.includes(":")
          ? time.split(":").length === 2
            ? `${time}:00`
            : time
          : `${time}:00:00`

        // Ensure end_time has seconds
        const endTimeWithSeconds = end_time.includes(":")
          ? end_time.split(":").length === 2
            ? `${end_time}:00`
            : end_time
          : `${end_time}:00:00`

        // Get user ID from auth token
        let userId = null
        try {
          // In a server action, we can't access localStorage directly
          // So we'll extract user ID from the auth token if possible
          if (authToken) {
            // This is a simplified approach - in a real app, you'd decode the JWT
            // For now, we'll use a placeholder user ID
            userId = "auth-user-id"
          }
        } catch (e) {
          console.error("Error extracting user ID from token:", e)
        }

        // Create the session data object
        const newSessionData = {
          session_name,
          location,
          fun_rating,
          date,
          time: timeWithSeconds,
          end_time: endTimeWithSeconds,
          session_notes,
          user_id: userId, // Add user ID if available
          ...(tagged_users.length > 0 && { tagged_users }), // Include tagged users in Supabase fallback
          raw_swell: {
            // Updated from raw_data to raw_swell
            swells: [],
            conditions: {
              tide: { height: 0, type: "unknown" },
              wind: { speed: 0, direction: 0 },
              temperature: { water: 0, air: 0 },
            },
          },
        }

        // Add a timestamp to make the session name unique
        const timestamp = new Date().getTime()
        newSessionData.session_name = `${newSessionData.session_name} (${timestamp})`

        console.log("Inserting into Supabase with data:", newSessionData)

        const { data, error } = await supabase.from(TABLE_NAME).insert(newSessionData).select()

        if (error) {
          throw new Error(`Supabase error: ${error.message}`)
        }

        if (!data || data.length === 0) {
          throw new Error("No data returned after creating session")
        }

        // Revalidate the sessions page
        revalidatePath("/sessions")

        return {
          success: true,
          data: data[0],
          source: "supabase",
        }
      } catch (supabaseError) {
        console.error("Server action: Supabase fallback also failed:", supabaseError)
        throw supabaseError
      }
    }
  } catch (error) {
    console.error("Server action: Error in addSurfSession:", error)
    return {
      success: false,
      error: error instanceof Error ? error.message : "Failed to add surf session",
      debug: String(error),
    }
  }
}
