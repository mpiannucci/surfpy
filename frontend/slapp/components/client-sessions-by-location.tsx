"use client"

import { useState, useEffect } from "react"
import { LocationSessionsTable } from "./location-sessions-table"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Card } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { AlertCircle, ListFilter } from "lucide-react"
import type { SurfSession } from "@/lib/types"

// --- Helper Functions and Data Definitions ---

const getCardinalDirection = (angle: number): string => {
  const directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
  return directions[Math.round(angle / 45) % 8];
}

const heightRanges = [
  { label: "0-2 ft", min: 0, max: 2 },
  { label: "2-4 ft", min: 2, max: 4 },
  { label: "4-6 ft", min: 4, max: 6 },
  { label: "6+ ft", min: 6, max: Infinity },
]

const periodRanges = [
  { label: "0-5 s", min: 0, max: 5 },
  { label: "5-8 s", min: 5, max: 8 },
  { label: "8-12 s", min: 8, max: 12 },
  { label: "12+ s", min: 12, max: Infinity },
]

const directionRanges = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];

interface FilterToggleGroupProps {
  label: string;
  options: readonly string[];
  selected: string[];
  onToggle: (option: string) => void;
}

const FilterToggleGroup: React.FC<FilterToggleGroupProps> = ({ label, options, selected, onToggle }) => (
  <div className="space-y-2">
    <Label>{label}</Label>
    <div className="flex flex-wrap gap-2">
      {options.map(option => (
        <Button
          key={option}
          variant={selected.includes(option) ? "secondary" : "outline"}
          size="sm"
          onClick={() => onToggle(option)}
        >
          {option}
        </Button>
      ))}
    </div>
  </div>
);


// --- Main Component ---

interface ClientSessionsByLocationProps {
  location: string
}

export function ClientSessionsByLocation({ location }: ClientSessionsByLocationProps) {
  const [masterSessionList, setMasterSessionList] = useState<SurfSession[]>([])
  const [displayedSessions, setDisplayedSessions] = useState<SurfSession[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // New filter states
  const [selectedHeights, setSelectedHeights] = useState<string[]>([])
  const [selectedPeriods, setSelectedPeriods] = useState<string[]>([])
  const [selectedDirections, setSelectedDirections] = useState<string[]>([])

  useEffect(() => {
    const fetchSessionsByLocation = async () => {
      if (!location) return
      setIsLoading(true)
      setError(null)
      try {
        const token = localStorage.getItem("auth_token")
        if (!token) throw new Error("Authentication token not found.")

        const response = await fetch("/api/auth/cors-proxy", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            url: `https://surfdata-4kuzgt1ku-martins-projects-383d438b.vercel.app/api/surf-sessions/location/${location}`,
            method: "GET",
            headers: { Authorization: `Bearer ${token}` },
          }),
        })

        if (!response.ok) {
          if (response.status === 404) {
            setMasterSessionList([])
          } else {
            throw new Error(`Failed to fetch sessions: ${response.statusText}`)
          }
        } else {
          const result = await response.json()
          if (result.status === 'success') {
            setMasterSessionList(result.data || [])
          } else if (result.message === 'No sessions found for location') {
            setMasterSessionList([])
          } else {
            throw new Error(result.message || 'Invalid data format from API')
          }
        }
      } catch (err: any) {
        setError(err.message)
      } finally {
        setIsLoading(false)
      }
    }
    fetchSessionsByLocation()
  }, [location])

  useEffect(() => {
    let filtered = [...masterSessionList]

    // Helper function to check if a value is within any of the selected ranges
    const isInRange = (value: number, selectedRanges: string[], rangeDefs: { label: string, min: number, max: number }[]) => {
      if (selectedRanges.length === 0) return true;
      return selectedRanges.some(label => {
        const range = rangeDefs.find(r => r.label === label);
        return range && value >= range.min && value < range.max;
      });
    };

    // Apply filters
    filtered = filtered.filter(session => {
      // Ensure swell data exists, otherwise exclude from filtered results
      const primarySwell = session.raw_swell?.[0]?.swell_components?.swell_1;
      if (!primarySwell) {
        return false;
      }

      const heightMatch = isInRange(primarySwell.height, selectedHeights, heightRanges);
      const periodMatch = isInRange(primarySwell.period, selectedPeriods, periodRanges);
      
      const directionMatch = selectedDirections.length === 0 || selectedDirections.includes(getCardinalDirection(primarySwell.direction));

      return heightMatch && periodMatch && directionMatch;
    });
    
    // Default sort by newest first
    filtered.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());

    setDisplayedSessions(filtered)
  }, [masterSessionList, selectedHeights, selectedPeriods, selectedDirections])

  const handleToggle = (setter: React.Dispatch<React.SetStateAction<string[]>>, option: string) => {
    setter(prev => 
      prev.includes(option) ? prev.filter(item => item !== option) : [...prev, option]
    );
  };

  if (isLoading) {
    return <Skeleton className="h-48 w-full" />
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    )
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold tracking-tight">Logged Sessions at this Spot</h2>
      <Card className="p-4 bg-background/20 border-border/30">
        <div className="space-y-4">
          <div className="font-semibold flex items-center gap-2">
            <ListFilter className="h-5 w-5" />
            Filter by Swell Conditions
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <FilterToggleGroup
              label="Swell Height"
              options={heightRanges.map(r => r.label)}
              selected={selectedHeights}
              onToggle={(option) => handleToggle(setSelectedHeights, option)}
            />
            <FilterToggleGroup
              label="Swell Period"
              options={periodRanges.map(r => r.label)}
              selected={selectedPeriods}
              onToggle={(option) => handleToggle(setSelectedPeriods, option)}
            />
            <FilterToggleGroup
              label="Swell Direction"
              options={directionRanges}
              selected={selectedDirections}
              onToggle={(option) => handleToggle(setSelectedDirections, option)}
            />
          </div>
        </div>
      </Card>

      <LocationSessionsTable sessions={displayedSessions} />
    </div>
  )
}
