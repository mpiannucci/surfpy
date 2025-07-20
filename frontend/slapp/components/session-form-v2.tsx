 
"use client"

import type React from "react"
import { useState, useEffect, useCallback } from "react"
import { useRouter } from "next/navigation"
import { addSurfSession } from "@/app/actions"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { useToast } from "@/components/ui/use-toast"
import { getAuthToken } from "@/lib/auth"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { X, Search, Loader2 } from "lucide-react"
import { debounce } from "lodash"

// Define the types for the data we'll be fetching
interface SurfSpot {
  name: string
  slug: string
}

interface User {
  user_id: string
  display_name: string
  email: string
}

const API_BASE_URL = "https://surfdata-3jbxpd53s-martins-projects-383d438b.vercel.app"

export function SessionFormV2() {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [surfSpots, setSurfSpots] = useState<SurfSpot[]>([])
  const [location, setLocation] = useState<string>("")
  const [currentDate, setCurrentDate] = useState("")
  const [startTime, setStartTime] = useState("")
  const [endTime, setEndTime] = useState("")
  const { toast } = useToast()
  const router = useRouter()

  const [searchQuery, setSearchQuery] = useState("")
  const [searchResults, setSearchResults] = useState<User[]>([])
  const [selectedUsers, setSelectedUsers] = useState<User[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const [showDropdown, setShowDropdown] = useState(false)

  // Set default date and time on component mount
  useEffect(() => {
    const now = new Date()
    const formattedDate = now.toISOString().split("T")[0]
    setCurrentDate(formattedDate)

    const hours = now.getHours().toString().padStart(2, "0")
    const minutes = now.getMinutes().toString().padStart(2, "0")
    const timeString = `${hours}:${minutes}`
    setStartTime(timeString)

    const endDate = new Date(now.getTime() + 2 * 60 * 60 * 1000) // Add 2 hours
    const endHours = endDate.getHours().toString().padStart(2, "0")
    const endMinutes = endDate.getMinutes().toString().padStart(2, "0")
    const endTimeString = `${endHours}:${endMinutes}`
    setEndTime(endTimeString)
  }, [])

  // Fetch surf spots on component mount
  useEffect(() => {
    const fetchSurfSpots = async () => {
      try {
        const authToken = getAuthToken()
        const response = await fetch("/api/auth/cors-proxy", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            url: `${API_BASE_URL}/api/surf-spots`,
            method: "GET",
            headers: {
              Authorization: `Bearer ${authToken}`,
            },
          }),
        })
        const data = await response.json()
        if (data.status === "success") {
          setSurfSpots(data.data)
        } else {
          toast({
            title: "Error",
            description: "Failed to load surf spots.",
            variant: "destructive",
          })
        }
      } catch (error) {
        console.error("Error fetching surf spots:", error)
        toast({
          title: "Error",
          description: "Failed to load surf spots.",
          variant: "destructive",
        })
      }
    }
    fetchSurfSpots()
  }, [toast])

  const debouncedSearch = useCallback(
    debounce(async (query: string) => {
      if (query.length < 2) {
        setSearchResults([])
        setShowDropdown(false)
        return
      }

      setIsSearching(true)
      try {
        const authToken = getAuthToken()
        const response = await fetch("/api/auth/cors-proxy", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            url: `${API_BASE_URL}/api/users/search?q=${encodeURIComponent(query)}`,
            method: "GET",
            headers: {
              Authorization: `Bearer ${authToken}`,
            },
          }),
        })
        const data = await response.json()
        if (data.status === "success") {
          const filteredResults = data.data.filter(
            (user: any) => !selectedUsers.some((selected) => selected.user_id === user.user_id)
          )
          setSearchResults(filteredResults)
          setShowDropdown(filteredResults.length > 0)
        } else {
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
    }, 300),
    [selectedUsers]
  )

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value
    setSearchQuery(query)
    debouncedSearch(query)
  }

  const selectUser = (user: User) => {
    setSelectedUsers((prev) => [...prev, user])
    setSearchQuery("")
    setSearchResults([])
    setShowDropdown(false)
  }

  const removeUser = (userId: string) => {
    setSelectedUsers((prev) => prev.filter((user) => user.user_id !== userId))
  }

  const isEndTimeBeforeStartTime = startTime && endTime && endTime < startTime

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setIsSubmitting(true)

    try {
      const formData = new FormData(event.currentTarget)
      const sessionData = {
        session_name: formData.get("session_name") as string,
        location: location,
        date: formData.get("date") as string,
        time: `${formData.get("time")}:00`,
        end_time: `${formData.get("end_time")}:00`,
        fun_rating: parseFloat(formData.get("fun_rating") as string),
        session_notes: formData.get("session_notes") as string,
        tagged_users: selectedUsers.map((user) => user.user_id),
      }

      const authToken = getAuthToken()
      const response = await fetch("/api/auth/cors-proxy", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          url: `${API_BASE_URL}/api/surf-sessions`,
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${authToken}`,
          },
          data: sessionData,
        }),
      })

      if (response.ok) {
        toast({
          title: "Success!",
          description: "Your surf session has been added.",
        })
        router.push("/sessions-v2")
      } else {
        const errorData = await response.json()
        toast({
          title: "Error",
          description: errorData.message || "Failed to add surf session. Please try again.",
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

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-4">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="session_name">Session Name</Label>
            <Input id="session_name" name="session_name" required placeholder="Epic Dawn Session" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="location">Location</Label>
            <Select value={location} onValueChange={setLocation} name="location">
              <SelectTrigger>
                <SelectValue placeholder="Select a location" />
              </SelectTrigger>
              <SelectContent>
                {surfSpots.map((spot) => (
                  <SelectItem key={spot.slug} value={spot.slug}>
                    {spot.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
          <div className="space-y-2">
            <Label htmlFor="date">Date</Label>
            <Input id="date" name="date" type="date" required value={currentDate} onChange={(e) => setCurrentDate(e.target.value)} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="time">Start Time</Label>
            <Input
              id="time"
              name="time"
              type="time"
              required
              value={startTime}
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
              value={endTime}
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
              step="0.25"
              required
            />
          </div>
        </div>

        {isEndTimeBeforeStartTime && <div className="text-sm text-red-600">End time cannot be before start time</div>}

        <div className="space-y-2">
          <Label htmlFor="session_notes">Notes</Label>
          <Textarea
            id="session_notes"
            name="session_notes"
            placeholder="Share details about the session..."
            className="min-h-32"
            rows={4}
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
                placeholder="Search for surf buddies..."
                className="pl-10"
                onFocus={() => searchQuery.length >= 2 && setShowDropdown(true)}
                onBlur={() => setTimeout(() => setShowDropdown(false), 200)}
              />
              {isSearching && (
                <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                  <Loader2 className="animate-spin h-4 w-4" />
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
          {isSubmitting ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Saving...</> : "Save Session"}
        </Button>
      </div>
    </form>
  )
}
