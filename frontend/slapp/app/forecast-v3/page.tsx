"use client"

import { useState, useEffect } from "react"
import { ForecastDashboardV2 } from "@/components/forecast-dashboard-v2"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { MapPin, Waves } from "lucide-react"

interface Spot {
  name: string;
  slug: string | null;
}

interface RegionData {
  region: string | null;
  spots: Spot[];
}

export default function ForecastV3Page() {
  const [selectedLocation, setSelectedLocation] = useState<string | null>(null)
  const [regionsData, setRegionsData] = useState<RegionData[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchSurfSpots = async () => {
      try {
        setLoading(true)
        const response = await fetch("https://surfdata-martins-projects-383d438b.vercel.app/api/surf-spots-by-region")
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        const result = await response.json()
        // Filter out regions where region is null
        const filteredData = result.data.filter((item: RegionData) => item.region !== null)
        setRegionsData(filteredData)
      } catch (e: any) {
        setError(e.message)
      } finally {
        setLoading(false)
      }
    }

    fetchSurfSpots()
  }, [])

  if (selectedLocation) {
    return <ForecastDashboardV2 location={selectedLocation} onBack={() => setSelectedLocation(null)} />
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <p className="text-lg font-semibold">Getting surf spots...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8 text-center text-red-500">
        <p>Error loading surf spots: {error}</p>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Surf Forecast</h1>
          <p className="text-muted-foreground">Select a location to view the new forecast dashboard</p>
        </div>

        {regionsData.map((regionData) => (
          <div key={regionData.region} className="mb-8">
            <h2 className="text-2xl font-bold mb-4">{regionData.region}</h2>
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {regionData.spots.map((spot) => (
                <Card
                  key={spot.name}
                  className={`transition-all hover:shadow-lg hover:scale-105 ${spot.slug ? "cursor-pointer" : "opacity-50 cursor-not-allowed"}`}
                  onClick={() => spot.slug && setSelectedLocation(spot.slug)}
                >
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <MapPin className="h-5 w-5" />
                      {spot.name}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <Button className="w-full bg-transparent" variant="outline" disabled={!spot.slug}>
                      <Waves className="h-4 w-4 mr-2" />
                      View Forecast
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
