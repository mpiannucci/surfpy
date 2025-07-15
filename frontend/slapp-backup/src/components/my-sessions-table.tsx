"use client"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import type React from "react"

import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import { useRouter } from "next/navigation"
import { useState } from "react"
import { Edit } from "lucide-react"
import { EditSessionModal } from "./edit-session-modal"
import { DeleteSessionButton } from "./delete-session-button"
import type { SurfSession } from "@/lib/types"

interface MySessionsTableProps {
  sessions: SurfSession[]
  onSessionsChange?: () => void
}

export function MySessionsTable({ sessions, onSessionsChange }: MySessionsTableProps) {
  const router = useRouter()
  const [editingSession, setEditingSession] = useState<SurfSession | null>(null)
  const [isEditModalOpen, setIsEditModalOpen] = useState(false)

  const handleView = (id: number) => {
    router.push(`/sessions/${id}`)
  }

  const handleEdit = (session: SurfSession, event: React.MouseEvent) => {
    event.stopPropagation() // Prevent row click
    setEditingSession(session)
    setIsEditModalOpen(true)
  }

  const handleEditClose = () => {
    setIsEditModalOpen(false)
    setEditingSession(null)
  }

  const handleEditUpdate = (updatedSession: SurfSession) => {
    if (onSessionsChange) {
      onSessionsChange()
    }
  }

  const formatParticipants = (participants: Array<{ user_id: string; display_name: string }> | undefined) => {
    if (!participants || participants.length === 0) {
      return "Solo session"
    }

    if (participants.length <= 2) {
      return participants.map((p) => p.display_name).join(", ")
    }

    // Show first 2 names + count for the rest
    const firstTwo = participants
      .slice(0, 2)
      .map((p) => p.display_name)
      .join(", ")
    const remaining = participants.length - 2
    return `${firstTwo} + ${remaining} other${remaining > 1 ? "s" : ""}`
  }

  const formatTime = (time: string) => {
    if (!time) return ""

    try {
      // Parse the time string (assuming HH:MM:SS format)
      const [hours, minutes] = time.split(":")
      const hour = Number.parseInt(hours, 10)
      const minute = Number.parseInt(minutes, 10)

      // Convert to 12-hour format
      const ampm = hour >= 12 ? "PM" : "AM"
      const hour12 = hour % 12 || 12

      return `${hour12}:${minute.toString().padStart(2, "0")} ${ampm}`
    } catch (error) {
      return time // Return original if parsing fails
    }
  }

  if (sessions.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-muted-foreground">No surf sessions found.</p>
        <Button onClick={() => router.push("/add")} className="mt-4">
          Add Your First Session
        </Button>
      </div>
    )
  }

  return (
    <>
      {/* Desktop Table View - Hidden on mobile */}
      <div className="hidden md:block rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[150px]">Session Name</TableHead>
              <TableHead className="w-[120px]">Location</TableHead>
              <TableHead className="w-[100px]">Date</TableHead>
              <TableHead className="w-[90px]">Start Time</TableHead>
              <TableHead className="w-[90px]">End Time</TableHead>
              <TableHead className="w-[120px]">Other Surfers</TableHead>
              <TableHead className="w-[80px]">Rating</TableHead>
              <TableHead className="w-[100px]">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {sessions.map((session) => (
              <TableRow
                key={session.id}
                className="cursor-pointer hover:bg-muted/50"
                onClick={() => handleView(session.id)}
              >
                <TableCell className="font-medium w-[150px]">
                  <div className="break-words">{session.session_name}</div>
                </TableCell>
                <TableCell className="w-[120px]">{session.location}</TableCell>
                <TableCell className="w-[100px]">{new Date(session.date).toLocaleDateString()}</TableCell>
                <TableCell className="w-[90px]">{formatTime(session.time)}</TableCell>
                <TableCell className="w-[90px]">{formatTime(session.end_time || "")}</TableCell>
                <TableCell className="w-[120px]">
                  <div className="text-sm text-muted-foreground break-words">
                    {formatParticipants(session.participants)}
                  </div>
                </TableCell>
                <TableCell className="w-[80px]">
                  <Badge variant="secondary">{session.fun_rating}/10</Badge>
                </TableCell>
                <TableCell className="w-[100px]">
                  <div className="flex gap-2" onClick={(e) => e.stopPropagation()}>
                    <Button variant="outline" size="sm" onClick={(e) => handleEdit(session, e)}>
                      <Edit className="h-3 w-3" />
                    </Button>
                    <DeleteSessionButton sessionId={session.id.toString()} iconOnly={true} />
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {/* Mobile Tile View - Hidden on desktop */}
      <div className="md:hidden space-y-4">
        {sessions.map((session) => (
          <Card
            key={session.id}
            className="cursor-pointer hover:shadow-md transition-shadow"
            onClick={() => handleView(session.id)}
          >
            <CardContent className="p-4">
              <div className="flex justify-between items-start mb-2">
                <h3 className="font-semibold text-lg truncate pr-2">{session.session_name}</h3>
                <Badge variant="secondary" className="shrink-0">
                  {session.fun_rating}/10
                </Badge>
              </div>

              <div className="space-y-2 text-sm mb-3">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Location:</span>
                  <span className="font-medium">{session.location}</span>
                </div>

                <div className="flex justify-between">
                  <span className="text-muted-foreground">Date:</span>
                  <span>{new Date(session.date).toLocaleDateString()}</span>
                </div>

                <div className="flex justify-between">
                  <span className="text-muted-foreground">Start Time:</span>
                  <span>{formatTime(session.time)}</span>
                </div>

                <div className="flex justify-between">
                  <span className="text-muted-foreground">End Time:</span>
                  <span>{formatTime(session.end_time || "")}</span>
                </div>

                <div className="flex justify-between">
                  <span className="text-muted-foreground">Other Surfers:</span>
                  <span className="text-right max-w-[60%] truncate">{formatParticipants(session.participants)}</span>
                </div>
              </div>

              <div className="flex gap-2 pt-2 border-t" onClick={(e) => e.stopPropagation()}>
                <Button variant="outline" size="sm" onClick={(e) => handleEdit(session, e)} className="flex-1">
                  <Edit className="h-3 w-3 mr-1" />
                  Edit
                </Button>
                <DeleteSessionButton sessionId={session.id.toString()} iconOnly={true} />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Edit Modal */}
      {editingSession && (
        <EditSessionModal
          session={editingSession}
          isOpen={isEditModalOpen}
          onClose={handleEditClose}
          onUpdate={handleEditUpdate}
        />
      )}
    </>
  )
}
