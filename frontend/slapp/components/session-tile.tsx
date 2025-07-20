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
          {session.raw_swell?.[0]?.swell_components && (
            <div className="col-span-2">
              <p className="font-bold text-sm mb-1">Swell Components:</p>
              {Object.entries(session.raw_swell[0].swell_components)
                .filter(([, swell]) => swell !== undefined)
                .map(([key, swell]) => (
                  <div key={key} className="flex items-center gap-2 text-xs mb-1">
                    <Waves className="h-4 w-4 text-blue-500" />
                    <span>
                      {swell.height?.toFixed(1) ?? 'N/A'}ft @ {swell.period?.toFixed(0) ?? 'N/A'}s from {swell.direction?.toFixed(0) ?? 'N/A'}°
                    </span>
                  </div>
                ))}
            </div>
          )}
          
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
