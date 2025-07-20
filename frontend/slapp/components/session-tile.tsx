"use client"

import Link from "next/link"
import { Card } from "@/components/ui/card"
import { Waves, TrendingUp, User, Calendar, Clock, ArrowUp, ArrowUpRight, ArrowRight, ArrowDownRight, ArrowDown, ArrowDownLeft, ArrowLeft, ArrowUpLeft, MapPin } from "lucide-react"
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

// Helper to get directional arrow icon based on degrees
const getDirectionArrow = (degrees: number | undefined) => {
  if (degrees === undefined || degrees === null) return null;
  if (degrees >= 337.5 || degrees < 22.5) return <ArrowUp className="h-3 w-3 inline-block ml-1" />; // N
  if (degrees >= 22.5 && degrees < 67.5) return <ArrowUpRight className="h-3 w-3 inline-block ml-1" />; // NE
  if (degrees >= 67.5 && degrees < 112.5) return <ArrowRight className="h-3 w-3 inline-block ml-1" />; // E
  if (degrees >= 112.5 && degrees < 157.5) return <ArrowDownRight className="h-3 w-3 inline-block ml-1" />; // SE
  if (degrees >= 157.5 && degrees < 202.5) return <ArrowDown className="h-3 w-3 inline-block ml-1" />; // S
  if (degrees >= 202.5 && degrees < 247.5) return <ArrowDownLeft className="h-3 w-3 inline-block ml-1" />; // SW
  if (degrees >= 247.5 && degrees < 292.5) return <ArrowLeft className="h-3 w-3 inline-block ml-1" />; // W
  if (degrees >= 292.5 && degrees < 337.5) return <ArrowUpLeft className="h-3 w-3 inline-block ml-1" />; // NW
  return null;
};

// Helper to get cardinal direction from degrees
const getCardinalDirection = (degrees: number | undefined) => {
  if (degrees === undefined || degrees === null) return "N/A";
  if (degrees >= 337.5 || degrees < 22.5) return "N";
  if (degrees >= 22.5 && degrees < 67.5) return "NE";
  if (degrees >= 67.5 && degrees < 112.5) return "E";
  if (degrees >= 112.5 && degrees < 157.5) return "SE";
  if (degrees >= 157.5 && degrees < 202.5) return "S";
  if (degrees >= 202.5 && degrees < 247.5) return "SW";
  if (degrees >= 247.5 && degrees < 292.5) return "W";
  if (degrees >= 292.5 && degrees < 337.5) return "NW";
  return "N/A";
};

export function SessionTile({ session }: SessionTileProps) {
  
  

  return (
    <Link href={`/sessions/${session.id}`} passHref>
      <Card className="h-full flex flex-col p-4 border rounded-lg hover:shadow-lg transition-shadow duration-200 cursor-pointer">
        {/* Header */}
        <div className="flex justify-between items-start mb-3">
          <div className="flex-1 overflow-hidden">
            <h3 className="text-xl font-bold truncate">{session.session_name}</h3>
            <div className="flex items-center text-base font-semibold text-foreground mt-1">
              <MapPin className="mr-1 h-4 w-4" /> {session.location}
            </div>
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
                      {swell.height?.toFixed(1) ?? 'N/A'}ft @ {swell.period?.toFixed(0) ?? 'N/A'}s from {getCardinalDirection(swell.direction)} ({swell.direction?.toFixed(0) ?? 'N/A'})° {getDirectionArrow((swell.direction + 180) % 360)}
                    </span>
                  </div>
                ))}
            </div>
          )}
          
        </div>

        {/* Session Notes */}
        {session.session_notes && (
          <div className="mb-4 flex-grow">
            <p className="text-sm text-muted-foreground line-clamp-4">
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
