"use client"

import Link from "next/link"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { formatDate, formatTime } from "@/lib/utils"
import { SurfSession } from "@/lib/types" // Assuming types are defined here
import { Waves, Wind, Thermometer, Star, Calendar, Clock, BookOpen, User } from "lucide-react"

interface LocationSessionsTableProps {
  sessions: SurfSession[]
}

// Helper to get the primary swell component
const getPrimarySwell = (swellData: any) => {
  if (!swellData || !swellData.length || !swellData[0].swell_components) {
    return null
  }
  // Assuming the first swell component is the primary one
  return swellData[0].swell_components.swell_1 || null
}

export function LocationSessionsTable({ sessions }: LocationSessionsTableProps) {
  if (sessions.length === 0) {
    return (
      <div className="text-center text-muted-foreground py-8">
        <p>No sessions found for this location.</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {sessions.map((session) => {
        const primarySwell = getPrimarySwell(session.raw_swell)

        return (
          <Card key={session.id} className="bg-background/20 border-border/30">
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="text-xl font-bold">{session.session_name}</CardTitle>
                  <div className="flex items-center gap-4 text-sm text-muted-foreground mt-1">
                    <div className="flex items-center gap-1">
                      <Calendar className="h-4 w-4" />
                      <span>{formatDate(session.date)}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Clock className="h-4 w-4" />
                      <span>{formatTime(session.time)}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <User className="h-4 w-4" />
                      <span>{session.display_name}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="secondary" className="flex items-center gap-1 text-lg">
                    <Star className="h-4 w-4 text-yellow-400" />
                    <span>{session.fun_rating}/10</span>
                  </Badge>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {primarySwell && (
                <div className="p-3 rounded-lg bg-muted/50">
                  <h4 className="font-semibold mb-2 text-base">Conditions</h4>
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-sm">
                    <div className="flex items-center gap-2">
                      <Waves className="h-5 w-5 text-primary" />
                      <div>
                        <p className="font-bold">{primarySwell.height.toFixed(1)} ft</p>
                        <p className="text-muted-foreground">Swell</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <p className="text-3xl font-light text-muted-foreground">/</p>
                      <div>
                        <p className="font-bold">{primarySwell.period.toFixed(1)} s</p>
                        <p className="text-muted-foreground">Period</p>
                      </div>
                    </div>
                     <div className="flex items-center gap-2">
                      <p className="text-3xl font-light text-muted-foreground">/</p>
                      <div>
                        <p className="font-bold">{primarySwell.direction.toFixed(0)}°</p>
                        <p className="text-muted-foreground">Direction</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {session.session_notes && (
                <div>
                  <h4 className="font-semibold mb-1 flex items-center gap-2"><BookOpen className="h-4 w-4"/>Notes</h4>
                  <p className="text-muted-foreground whitespace-pre-line text-sm">{session.session_notes}</p>
                </div>
              )}

              <div className="flex justify-end">
                <Link href={`/sessions/${session.id}`} passHref>
                  <Button variant="outline" size="sm">View Full Details</Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
