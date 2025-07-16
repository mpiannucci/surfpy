"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { MapPin, Waves } from "lucide-react"
import { NewForecastDashboard } from "@/components/new-forecast-dashboard"

const locations = [
  {
    id: "lido-beach",
    name: "Lido Beach",
    description: "Long Island, New York",
    image: "/placeholder.svg?height=200&width=300",
  },
]

export default function ForecastPage() {
  const [selectedLocation, setSelectedLocation] = useState<string | null>(null)

  if (selectedLocation) {
    return <NewForecastDashboard location={selectedLocation} onBack={() => setSelectedLocation(null)} />
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Surf Forecast</h1>
          <p className="text-muted-foreground">Select a location to view detailed wave forecasts</p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {locations.map((location) => (
            <Card
              key={location.id}
              className="cursor-pointer transition-all hover:shadow-lg hover:scale-105"
              onClick={() => setSelectedLocation(location.id)}
            >
              <div className="aspect-video relative overflow-hidden rounded-t-lg">
                <img
                  src={location.image || "/placeholder.svg"}
                  alt={location.name}
                  className="object-cover w-full h-full"
                />
              </div>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MapPin className="h-5 w-5" />
                  {location.name}
                </CardTitle>
                <CardDescription>{location.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <Button className="w-full bg-transparent" variant="outline">
                  <Waves className="h-4 w-4 mr-2" />
                  View Forecast
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        <Card className="bg-muted/50">
          <CardHeader>
            <CardTitle>Coming Soon</CardTitle>
            <CardDescription>More surf spots will be added in future updates</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              We're working on adding more locations to provide comprehensive surf forecasts for your favorite spots.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
