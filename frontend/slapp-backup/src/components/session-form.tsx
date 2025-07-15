"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { addSurfSession } from "@/app/actions"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { useToast } from "@/components/ui/use-toast"
import { getAuthToken } from "@/lib/auth"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { X, Search } from "lucide-react"

// Define the supported locations
const SUPPORTED_LOCATIONS = ["Lido", "Rockaways", "Belmar", "Manasquan"]

export function SessionForm() {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [location, setLocation] = useState<string>(SUPPORTED_LOCATIONS[0])
  const [currentDate, setCurrentDate] = useState("")
  const [currentTime, setCurrentTime] = useState("")
  const [startTime, setStartTime] = useState("")
  const [endTime, setEndTime] = useState("")
  const { toast } = useToast()
  const router = useRouter()

  const [searchQuery, setSearchQuery] = useState("")
  const [searchResults, setSearchResults] = useState<Array<{ user_id: string; display_name: string; email: string }>>(
    [],
  )
  const [selectedUsers, setSelectedUsers] = useState<Array<{ user_id: string; display_name: string; email: string }>>(
    [],
  )
  const [isSearching, setIsSearching] = useState(false)
  const [showDropdown, setShowDropdown] = useState(false)

  // Set default date and time on component mount
  useEffect(() => {
    const now = new Date()

    // Format date as YYYY-MM-DD for the date input
    const formattedDate = now.toISOString().split("T")[0]
    setCurrentDate(formattedDate)

    // Format time as HH:MM for the time input
    const hours = now.getHours().toString().padStart(2, "0")
    const minutes = now.getMinutes().toString().padStart(2, "0")
    const timeString = `${hours}:${minutes}`
    setCurrentTime(timeString)
    setStartTime(timeString)

    // Set end time to 2 hours after start time
    const endDate = new Date(now.getTime() + 2 * 60 * 60 * 1000) // Add 2 hours
    const endHours = endDate.getHours().toString().padStart(2, "0")
    const endMinutes = endDate.getMinutes().toString().padStart(2, "0")
    const endTimeString = `${endHours}:${endMinutes}`
    setEndTime(endTimeString)
  }, [])

  // Check if end time is before start time
  const isEndTimeBeforeStartTime = startTime && endTime && endTime < startTime

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setIsSubmitting(true)

    try {
      const formData = new FormData(event.currentTarget)

      // Add the selected location to the form data
      formData.set("location", location)

      // Add tagged users to form data
      if (selectedUsers.length > 0) {
        formData.set("tagged_users", JSON.stringify(selectedUsers.map((user) => user.user_id)))
      }

      // Add auth token to form data
      const authToken = getAuthToken()
      if (authToken) {
        formData.append("auth_token", authToken)
      }

      const result = await addSurfSession(formData)

      if (result.success) {
        toast({
          title: "Success!",
          description: "Your surf session has been added.",
        })
        router.push("/sessions")
      } else {
        toast({
          title: "Error",
          description: result.error || "Failed to add surf session. Please try again.",
          variant: "destructive",
        })
      }
    } catch (error) {
      console.error("Error submitting form:", error)
      toast({
        title: "Error",
        description: "An unexpected error occurred. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const searchUsers = async (query: string) => {
    if (query.length < 2) {
      setSearchResults([])
      setShowDropdown(false)
      return
    }

    setIsSearching(true)
    try {
      const authToken = getAuthToken()

      // Use the CORS proxy for the user search request
      const proxyResponse = await fetch("/api/auth/cors-proxy", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          url: `https://surfdata-hg88fz7nn-martins-projects-383d438b.vercel.app/api/users/search?q=${encodeURIComponent(query)}`,
          method: "GET",
          headers: {
            Authorization: `Bearer ${authToken}`,
            "Content-Type": "application/json",
          },
        }),
      })

      if (proxyResponse.ok) {
        const data = await proxyResponse.json()
        if (data.status === "success") {
          // Filter out already selected users
          const filteredResults = data.data.filter(
            (user: any) => !selectedUsers.some((selected) => selected.user_id === user.user_id),
          )
          setSearchResults(filteredResults)
          setShowDropdown(filteredResults.length > 0)
        } else {
          console.error("User search failed:", data)
          setSearchResults([])
          setShowDropdown(false)
        }
      } else {
        console.error("Proxy request failed:", proxyResponse.status)
        setSearchResults([])
        setShowDropdown(false)
      }
    } catch (error) {
      console.error("Error searching users:", error)
      setSearchResults([])
      setShowDropdown(false)
    } finally {
      setIsSearching(false)
    }
  }

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value
    setSearchQuery(query)
    searchUsers(query)
  }

  const selectUser = (user: { user_id: string; display_name: string; email: string }) => {
    setSelectedUsers((prev) => [...prev, user])
    setSearchQuery("")
    setSearchResults([])
    setShowDropdown(false)
  }

  const removeUser = (userId: string) => {
    setSelectedUsers((prev) => prev.filter((user) => user.user_id !== userId))
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-4">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="session_name">Session Name</Label>
            <Input id="session_name" name="session_name" required />
          </div>
          <div className="space-y-2">
            <Label htmlFor="location">Location</Label>
            <Select value={location} onValueChange={setLocation} name="location">
              <SelectTrigger>
                <SelectValue placeholder="Select a location" />
              </SelectTrigger>
              <SelectContent>
                {SUPPORTED_LOCATIONS.map((loc) => (
                  <SelectItem key={loc} value={loc}>
                    {loc}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
          <div className="space-y-2">
            <Label htmlFor="date">Date</Label>
            <Input id="date" name="date" type="date" required defaultValue={currentDate} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="time">Start Time</Label>
            <Input
              id="time"
              name="time"
              type="time"
              required
              defaultValue={currentTime}
              onChange={(e) => setStartTime(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="end_time">End Time</Label>
            <Input
              id="end_time"
              name="end_time"
              type="time"
              required
              defaultValue={endTime}
              onChange={(e) => setEndTime(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="fun_rating">Fun Rating (1-10)</Label>
            <Input
              id="fun_rating"
              name="fun_rating"
              type="number"
              min="1"
              max="10"
              step="0.01"
              required
              defaultValue="7"
            />
          </div>
        </div>

        {isEndTimeBeforeStartTime && <div className="text-sm text-red-600">End time cannot be before start time</div>}

        <div className="space-y-2">
          <Label htmlFor="session_notes">Notes</Label>
          <Textarea
            id="session_notes"
            name="session_notes"
            placeholder="How was your session? Any notable conditions or experiences?"
            className="min-h-32"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="tag_buddies">Tag Surf Buddies</Label>
          <div className="relative">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                id="tag_buddies"
                value={searchQuery}
                onChange={handleSearchChange}
                placeholder="Search for friends to tag..."
                className="pl-10"
                onFocus={() => searchQuery.length >= 2 && setShowDropdown(true)}
                onBlur={() => setTimeout(() => setShowDropdown(false), 200)}
              />
              {isSearching && (
                <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-900"></div>
                </div>
              )}
            </div>

            {showDropdown && searchResults.length > 0 && (
              <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto">
                {searchResults.map((user) => (
                  <div
                    key={user.user_id}
                    className="px-4 py-2 hover:bg-gray-100 cursor-pointer"
                    onClick={() => selectUser(user)}
                  >
                    <div className="font-medium">{user.display_name}</div>
                    <div className="text-sm text-gray-500">{user.email}</div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {selectedUsers.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-2">
              {selectedUsers.map((user) => (
                <div
                  key={user.user_id}
                  className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                >
                  <span>{user.display_name}</span>
                  <button
                    type="button"
                    onClick={() => removeUser(user.user_id)}
                    className="hover:bg-blue-200 rounded-full p-0.5"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="flex justify-end gap-4">
        <Button type="button" variant="outline" onClick={() => router.back()} disabled={isSubmitting}>
          Cancel
        </Button>
        <Button type="submit" disabled={isSubmitting || isEndTimeBeforeStartTime}>
          {isSubmitting ? "Saving..." : "Save Session"}
        </Button>
      </div>
    </form>
  )
}
