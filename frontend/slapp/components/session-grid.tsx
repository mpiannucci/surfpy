"use client"

import { SessionTile } from "./session-tile"
import type { SurfSession } from "@/app/sessions-v2/page"

interface SessionGridProps {
  sessions: SurfSession[]
  currentUserId: string | undefined
  onUpdate: (updatedSession: SurfSession) => void
}

export function SessionGrid({ sessions, currentUserId, onUpdate }: SessionGridProps) {
  if (sessions.length === 0) {
    return (
      <div className="text-center py-16">
        <h2 className="text-xl font-semibold">No Sessions Found</h2>
        <p className="text-muted-foreground mt-2">Try adjusting your filters to find what you're looking for.</p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {sessions.map((session) => (
        <SessionTile key={session.id} session={session} currentUserId={currentUserId} onUpdate={onUpdate} />
      ))}
    </div>
  )
}
