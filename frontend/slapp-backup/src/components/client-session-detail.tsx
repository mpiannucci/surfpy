"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { useParams, useRouter } from "next/navigation"
import { formatDate, formatTime } from "@/lib/utils"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { SwellDataDisplay } from "@/components/swell-data-display"
import { SwellComponentsVisualization } from "@/components/swell-components-visualization"
import { MeteorologicalDataDisplay } from "@/components/meteorological-data-display"
import { TideDataDisplay } from "@/components/tide-data-display"
import { ArrowLeft, Loader2, AlertCircle, User, Edit } from "lucide-react"
import { DeleteSessionButton } from "@/components/delete-session-button"
import { EditSessionModal } from "@/components/edit-session-modal"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { isSessionOwner } from "@/lib/api"
import { useToast } from "@/components/ui/use-toast"
import type { SurfSession } from "@/lib/types"

export function ClientSessionDetail() {
  const params = useParams()
  const router = useRouter()
  const { toast } = useToast()
  const [session, setSession] = useState<SurfSession | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [retryCount, setRetryCount] = useState(0)
  const [isOwner, setIsOwner] = useState(false)
  const [isEditModalOpen, setIsEditModalOpen] = useState(false)

  useEffect(() => {
    async function fetchSessionDetail() {
      if (!params.id) {
        setError("No session ID provided")
        setIsLoading(false)
        return
      }

      try {
        setIsLoading(true)
        setError(null)

        // Get auth token
        const token = localStorage.getItem("auth_token")
        if (!token) {
          setError("No authentication token found")
          setIsLoading(false)
          return
        }

        console.log("ClientSessionDetail - Fetching session ID:", params.id)

        // Use the correct API URL
        const apiUrl = `https://surfdata-hs9191va8-martins-projects-383d438b.vercel.app/api/surf-sessions/${params.id}`

        // Try with CORS proxy first
        try {
          console.log("ClientSessionDetail - Attempting fetch with CORS proxy")
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
                "Content-Type": "application/json",
              },
            }),
          })

          if (!proxyResponse.ok) {
            const errorData = await proxyResponse.json().catch(() => ({}))
            console.error("ClientSessionDetail - CORS proxy failed:", proxyResponse.status, errorData)
            throw new Error(`Proxy request failed: ${proxyResponse.status}`)
          }

          const proxyData = await proxyResponse.json()
          console.log("ClientSessionDetail - Proxy data received:", proxyData)
          processResponse(proxyData)
        } catch (proxyError) {
          console.error("ClientSessionDetail - CORS proxy error:", proxyError)

          // Try direct fetch as fallback
          try {
            console.log("ClientSessionDetail - Attempting direct fetch")
            const response = await fetch(apiUrl, {
              method: "GET",
              headers: {
                "Content-Type": "application/json",
                Accept: "application/json",
                Authorization: `Bearer ${token}`,
              },
              mode: "cors",
            })

            if (!response.ok) {
              throw new Error(`API request failed: ${response.status} ${response.statusText}`)
            }

            const text = await response.text()
            console.log("ClientSessionDetail - Direct fetch response text (first 200 chars):", text.substring(0, 200))
            const data = JSON.parse(text)
            console.log("ClientSessionDetail - Direct fetch data:", data)
            processResponse(data)
          } catch (directError) {
            console.error("ClientSessionDetail - Direct fetch failed:", directError)

            // Fall back to mock data after all attempts fail
            console.log("ClientSessionDetail - All API methods failed, using mock data")
            setMockData()
          }
        }
      } catch (e) {
        console.error("ClientSessionDetail - Error in fetchSessionDetail:", e)
        // Fall back to mock data
        setMockData()
      } finally {
        setIsLoading(false)
      }
    }

    // Helper function to set mock data when all fetch attempts fail
    function setMockData() {
      const mockSession: SurfSession = {
        id: Number(params.id) || 1,
        session_name: "Mock Session Detail",
        location: "rockaways",
        date: new Date().toISOString().split("T")[0],
        time: "10:00:00",
        end_time: "12:00:00",
        fun_rating: 8,
        session_notes:
          "This is mock data shown when the API is unreachable. The actual session details cannot be loaded at this time.",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        user_id: "mock-user-id",
        user_email: "mock@example.com",
        display_name: "Mock User",
        participants: [
          { user_id: "participant-1", display_name: "Jane Smith" },
          { user_id: "participant-2", display_name: "Bob Wilson" },
        ],
        raw_swell: {
          swells: [
            {
              height: 3.5,
              period: 12,
              direction: 270,
            },
          ],
        },
      }
      setSession(mockSession)
      // Check if the current user is the owner of this mock session
      setIsOwner(isSessionOwner(mockSession))
      setError("Using mock data because the API is currently unreachable.")
    }

    // Helper function to process the response and extract session data
    function processResponse(data: any) {
      console.log("ClientSessionDetail - Processing response:", data)

      // Extract session from the response
      let sessionData: SurfSession | null = null

      if (data) {
        if (typeof data === "object" && (data.id || data.session_name)) {
          // Direct session object
          sessionData = data
          console.log("ClientSessionDetail - Found direct session object")
        } else if (data.data && typeof data.data === "object" && (data.data.id || data.data.session_name)) {
          // { data: {...} } format
          sessionData = data.data
          console.log("ClientSessionDetail - Found session in data property")
        } else if (data.status === "success" && data.data && typeof data.data === "object") {
          // { status: "success", data: {...} } format
          sessionData = data.data
          console.log("ClientSessionDetail - Found session in success response")
        }
      }

      if (sessionData) {
        console.log("ClientSessionDetail - Session data extracted:", sessionData)

        // Ensure fun_rating is properly handled to prevent toString errors
        if (sessionData.fun_rating === null || sessionData.fun_rating === undefined) {
          sessionData.fun_rating = 7 // Default value
        }

        setSession(sessionData)
        // Check if the current user is the owner of this session
        setIsOwner(isSessionOwner(sessionData))
        setError(null)
        console.log("ClientSessionDetail - Session detail loaded:", sessionData.id)
      } else {
        console.log("ClientSessionDetail - Could not extract session data from response")
        setError("Could not extract session data from response")
        setMockData()
      }
    }

    fetchSessionDetail()
  }, [params.id, retryCount])

  // Function to retry fetching data
  const handleRetry = () => {
    setRetryCount((prev) => prev + 1)
  }

  // Helper function to format participants for display
  const formatParticipants = (participants: Array<{ user_id: string; display_name: string }> | undefined) => {
    if (!participants || participants.length === 0) {
      return "-"
    }
    return participants.map((p) => p.display_name).join(", ")
  }

  // Handle edit session button click
  const handleEditSession = () => {
    setIsEditModalOpen(true)
  }

  // Handle closing the edit modal
  const handleCloseEditModal = () => {
    setIsEditModalOpen(false)
  }

  // Handle successful session update
  const handleSessionUpdate = (updatedSession: SurfSession) => {
    console.log("ClientSessionDetail - Session updated:", updatedSession)

    // Ensure fun_rating is properly handled to prevent toString errors
    if (updatedSession.fun_rating === null || updatedSession.fun_rating === undefined) {
      updatedSession.fun_rating = 7 // Default value
    }

    setSession(updatedSession)
    setIsEditModalOpen(false)

    // Optionally refresh the session data from the server to ensure consistency
    setRetryCount((prev) => prev + 1)
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <span className="ml-2">Loading session details...</span>
      </div>
    )
  }

  if (error && !session) {
    return (
      <Alert variant="destructive" className="mb-6">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
        <div className="mt-4 flex gap-4">
          <Button variant="outline" onClick={() => router.back()}>
            Back
          </Button>
          <Button onClick={handleRetry}>Try Again</Button>
        </div>
      </Alert>
    )
  }

  if (!session) {
    return (
      <div className="rounded-lg border border-dashed p-8 text-center">
        <h3 className="text-lg font-medium">Session not found</h3>
        <p className="mt-1 text-sm text-muted-foreground">The requested session could not be found.</p>
        <div className="mt-4">
          <Link
            href="/sessions"
            className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
          >
            Back to Sessions
          </Link>
        </div>
      </div>
    )
  }

  // Extract swell buoy ID from the API response, handle null case
  const swellBuoyId = session.swell_buoy_id || "N/A"
  let swellData = null
  let swellComponents = null

  // Check if we have raw_swell with swell_components (renamed from raw_data)
  // Handle null values gracefully
  if (session.raw_swell && session.raw_swell !== null && typeof session.raw_swell === "object") {
    if ("swell_components" in session.raw_swell && session.raw_swell.swell_components !== null) {
      swellData = {
        date: session.date,
        swell_components: session.raw_swell.swell_components,
        buoy_id: swellBuoyId,
      }
      swellComponents = session.raw_swell.swell_components
    } else if (Array.isArray(session.raw_swell) && session.raw_swell.length > 0) {
      // Handle the case where raw_swell is an array (like the example provided)
      const firstEntry = session.raw_swell[0]
      if (
        firstEntry &&
        firstEntry !== null &&
        "swell_components" in firstEntry &&
        firstEntry.swell_components !== null
      ) {
        swellData = firstEntry
        swellComponents = firstEntry.swell_components
        if (!swellData.buoy_id) {
          swellData.buoy_id = swellBuoyId
        }
      }
    }
  }

  // Extract legacy swells data if available (for backward compatibility)
  // Handle null values gracefully
  const { raw_swell } = session
  const swells =
    raw_swell && raw_swell !== null && raw_swell.swells && raw_swell.swells !== null ? raw_swell.swells : []

  return (
    <div className="space-y-8">
      {error && (
        <Alert variant="warning" className="mb-6">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>API Connection Issue</AlertTitle>
          <AlertDescription className="flex flex-col gap-2">
            <p>{error}</p>
            <Button onClick={handleRetry} variant="outline" className="self-start mt-2 bg-transparent">
              Retry Connection
            </Button>
          </AlertDescription>
        </Alert>
      )}

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant="outline"
            size="sm"
            onClick={() => router.back()}
            className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background/20 border-border/30 h-10 w-10 p-0"
          >
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">{session.session_name || "Unnamed Session"}</h1>
            {session.display_name && (
              <div className="flex items-center gap-1 text-sm text-muted-foreground mt-1">
                <User className="h-3 w-3" />
                <span>Created by {session.display_name}</span>
              </div>
            )}
          </div>
        </div>
        {isOwner && (
          <div className="flex gap-2">
            <Button variant="default" size="sm" onClick={handleEditSession} className="flex items-center gap-2">
              <Edit className="h-4 w-4" />
              Edit Session
            </Button>
            <DeleteSessionButton sessionId={String(session.id)} />
          </div>
        )}
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card className="bg-background/10 border-border/30">
          <CardHeader>
            <CardTitle>Session Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <h3 className="text-sm font-medium text-muted-foreground">Date</h3>
                <p>{session.date ? formatDate(session.date) : "N/A"}</p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-muted-foreground">Location</h3>
                <p>{session.location || "N/A"}</p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-muted-foreground">Start Time</h3>
                <p>{session.time ? formatTime(session.time) : "N/A"}</p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-muted-foreground">End Time</h3>
                <p>{session.end_time ? formatTime(session.end_time) : "N/A"}</p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-muted-foreground">Rating</h3>
                <p className="font-medium">{session.fun_rating || 0}/10</p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-muted-foreground">Other Surfers</h3>
                <p>{formatParticipants(session.participants)}</p>
              </div>
            </div>

            {session.session_notes && (
              <div>
                <h3 className="text-sm font-medium text-muted-foreground">Notes</h3>
                <p className="mt-1 whitespace-pre-line">{session.session_notes}</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Display the swell data */}
        <SwellDataDisplay swellData={swellData} swells={swells} buoyId={swellBuoyId} />
      </div>

      {/* Display meteorological data if available - handle null gracefully */}
      {session.raw_met && session.raw_met !== null && <MeteorologicalDataDisplay metData={session.raw_met} />}

      {/* Display tide data if available - handle null gracefully */}
      {session.raw_tide && session.raw_tide !== null && <TideDataDisplay tideData={session.raw_tide} />}

      {/* Add the swell components visualization if available - handle null gracefully */}
      {swellComponents && swellComponents !== null && (
        <Card className="bg-background/10 border-border/30">
          <CardHeader>
            <CardTitle>Swell Components Visualization</CardTitle>
          </CardHeader>
          <CardContent>
            <SwellComponentsVisualization swellComponents={swellComponents} />
          </CardContent>
        </Card>
      )}

      {/* Edit Session Modal */}
      {session && (
        <EditSessionModal
          session={session}
          isOpen={isEditModalOpen}
          onClose={handleCloseEditModal}
          onUpdate={handleSessionUpdate}
        />
      )}
    </div>
  )
}
