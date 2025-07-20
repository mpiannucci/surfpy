"use client"

import Link from "next/link"
import { Card } from "@/components/ui/card"
import { Waves, TrendingUp, User, Calendar, Clock } from "lucide-react"
import type { SurfSession } from "@/app/sessions-v2/page"

interface SessionTileProps {
  session: SurfSession
}

// Helper to format time from HH:MM:SS to H:MM AM/PM
const formatTime = (timeStr: string) => {
  if (!timeStr) return "N/A"
  const [hours, minutes] = timeStr.split(":")
  const date = new Date()
  date.setHours(parseInt(hours, 10))
  date.setMinutes(parseInt(minutes, 10))
  return date.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" })
}

export function SessionTile({ session }: SessionTileProps) {
  const primarySwell = session.raw_swell?.[0]?.swell_components?.swell_1
  const tideLevel = session.raw_tide?.water_level

  return (
    <Link href={`/sessions/${session.id}`} passHref>
      <Card className="h-full flex flex-col p-4 border rounded-lg hover:shadow-lg transition-shadow duration-200 cursor-pointer">
        {/* Header */}
        <div className="flex justify-between items-start mb-3">
          <div className="flex-1">
            <h3 className="text-xl font-bold truncate">{session.session_name}</h3>
            <p className="text-sm text-muted-foreground">{session.location}</p>
          </div>
          <div className="ml-4 text-4xl font-extrabold text-primary">
            {session.fun_rating}
          </div>
        </div>

        {/* Core Conditions */}
        <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
          <div className="flex items-center gap-2 p-2 bg-muted/50 rounded-md">
            <Waves className="h-5 w-5 text-primary" />
            <div>
              <p className="font-bold">
                {primarySwell?.height ? `${primarySwell.height.toFixed(1)}ft` : "N/A"}
                <span className="font-normal text-muted-foreground"> @ </span>
                {primarySwell?.period ? `${primarySwell.period.toFixed(0)}s` : "N/A"}
              </p>
              <p className="text-xs text-muted-foreground">
                {primarySwell?.direction ? `${primarySwell.direction.toFixed(0)}°` : ""}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2 p-2 bg-muted/50 rounded-md">
            <TrendingUp className="h-5 w-5 text-primary" />
            <div>
              <p className="font-bold">
                {tideLevel !== undefined ? `${tideLevel.toFixed(1)}ft` : "N/A"}
              </p>
              <p className="text-xs text-muted-foreground">Tide Level</p>
            </div>
          </div>
        </div>

        {/* Session Notes */}
        {session.session_notes && (
          <div className="mb-4 flex-grow">
            <p className="text-sm text-muted-foreground line-clamp-2">
              {session.session_notes}
            </p>
          </div>
        )}

        {/* Footer */}
        <div className="flex justify-between items-center text-xs text-muted-foreground border-t pt-3 mt-auto">
           <div className="flex items-center gap-1">
             <User className="h-3 w-3" />
             <span>{session.display_name}</span>
           </div>
           <div className="flex items-center gap-1">
             <Calendar className="h-3 w-3" />
             <span>{new Date(session.date).toLocaleDateString("en-US", { month: 'short', day: 'numeric' })}</span>
             <Clock className="h-3 w-3 ml-2" />
             <span>{formatTime(session.time)}</span>
           </div>
        </div>
      </Card>
    </Link>
  )
}
