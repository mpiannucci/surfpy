"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useToast } from "@/components/ui/use-toast"
import { Loader2 } from "lucide-react"
import type { SurfSession } from "@/lib/types"

interface EditSessionModalProps {
  session: SurfSession
  isOpen: boolean
  onClose: () => void
  onUpdate: (updatedSession: SurfSession) => void
}

export function EditSessionModal({ session, isOpen, onClose, onUpdate }: EditSessionModalProps) {
  const { toast } = useToast()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Form state
  const [sessionName, setSessionName] = useState("")
  const [location, setLocation] = useState("")
  const [date, setDate] = useState("")
  const [startTime, setStartTime] = useState("")
  const [endTime, setEndTime] = useState("")
  const [funRating, setFunRating] = useState("7")
  const [sessionNotes, setSessionNotes] = useState("")

  // Pre-populate form when modal opens
  useEffect(() => {
    if (isOpen && session) {
      setSessionName(session.session_name || "")
      setLocation(session.location || "")
      setDate(session.date || "")
      setStartTime(session.time || "")
      setEndTime(session.end_time || "")
      // Fix the toString error by adding proper null checking and fallback
      const rating = session.fun_rating
      if (rating !== null && rating !== undefined) {
        setFunRating(String(rating))
      } else {
        setFunRating("7")
      }
      setSessionNotes(session.session_notes || "")
      setError(null)
    }
  }, [isOpen, session])

  // Check if end time is before start time
  const isEndTimeBeforeStartTime = startTime && endTime && endTime < startTime

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()

    if (isEndTimeBeforeStartTime) {
      setError("End time cannot be before start time")
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const token = localStorage.getItem("auth_token")
      if (!token) {
        throw new Error("No authentication token found")
      }

      const requestBody = {
        session_name: sessionName,
        location: location.toLowerCase(),
        date: date,
        time: startTime,
        end_time: endTime,
        fun_rating: Number.parseFloat(funRating) || 7,
        session_notes: sessionNotes,
      }

      console.log("EditSessionModal - Making update request for session:", session.id)
      console.log("EditSessionModal - Request body:", requestBody)

      // Use the same CORS proxy pattern as other successful API calls
      const response = await fetch("/api/auth/cors-proxy", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          url: `https://surfdata-dyoiv3qio-martins-projects-383d438b.vercel.app/api/surf-sessions/${session.id}`,
          method: "PUT",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          data: requestBody,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        console.error("EditSessionModal - Update failed:", response.status, errorData)
        throw new Error(errorData.message || `Update failed: ${response.status}`)
      }

      const data = await response.json()
      console.log("EditSessionModal - Update successful:", data)

      toast({
        title: "Session Updated",
        description: "Your session has been successfully updated.",
      })

      // Pass the updated session data back
      onUpdate(data.data || data)
      onClose()
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to update session"
      console.error("EditSessionModal - Error:", errorMessage)
      setError(errorMessage)
      toast({
        title: "Update Failed",
        description: errorMessage,
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Edit Session</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && <div className="p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md">{error}</div>}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="sessionName">Session Name</Label>
              <Input
                id="sessionName"
                value={sessionName}
                onChange={(e) => setSessionName(e.target.value)}
                placeholder="Enter session name"
                disabled={isLoading}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="location">Location</Label>
              <Select value={location} onValueChange={setLocation} disabled={true}>
                <SelectTrigger className="opacity-50">
                  <SelectValue placeholder="Select location" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="rockaways">Rockaways</SelectItem>
                  <SelectItem value="montauk">Montauk</SelectItem>
                  <SelectItem value="long-beach">Long Beach</SelectItem>
                  <SelectItem value="jones-beach">Jones Beach</SelectItem>
                  <SelectItem value="fire-island">Fire Island</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="date">Date</Label>
              <Input
                id="date"
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                disabled={isLoading}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="funRating">Fun Rating (1-10)</Label>
              <Input
                id="funRating"
                type="number"
                min="1"
                max="10"
                step="0.01"
                value={funRating}
                onChange={(e) => setFunRating(e.target.value)}
                disabled={isLoading}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="startTime">Start Time</Label>
              <Input
                id="startTime"
                type="time"
                value={startTime}
                onChange={(e) => setStartTime(e.target.value)}
                disabled={isLoading}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="endTime">End Time</Label>
              <Input
                id="endTime"
                type="time"
                value={endTime}
                onChange={(e) => setEndTime(e.target.value)}
                disabled={isLoading}
                className={isEndTimeBeforeStartTime ? "border-red-500" : ""}
                required
              />
              {isEndTimeBeforeStartTime && <p className="text-sm text-red-600">End time cannot be before start time</p>}
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="sessionNotes">Session Notes</Label>
            <Textarea
              id="sessionNotes"
              value={sessionNotes}
              onChange={(e) => setSessionNotes(e.target.value)}
              placeholder="Add any notes about your session..."
              rows={4}
              disabled={isLoading}
            />
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <Button type="button" variant="outline" onClick={onClose} disabled={isLoading}>
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading || isEndTimeBeforeStartTime}>
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                "Save Changes"
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
