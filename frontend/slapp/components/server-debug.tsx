"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface ServerDebugProps {
  rawResponse: any
  processedSessions: any[]
  fetchPath: string
}

export function ServerDebug({ rawResponse, processedSessions, fetchPath }: ServerDebugProps) {
  const [showDebug, setShowDebug] = useState(false)

  // Only show in production if forced
  if (process.env.NODE_ENV !== "development" && !showDebug) {
    return (
      <Button variant="outline" size="sm" onClick={() => setShowDebug(true)}>
        Show Server Debug
      </Button>
    )
  }

  return (
    <Card className="mt-4">
      <CardHeader>
        <CardTitle className="flex justify-between">
          <span>Server-Side Debug Information</span>
          <Button variant="outline" size="sm" onClick={() => setShowDebug(false)}>
            Hide
          </Button>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <h3 className="text-sm font-medium mb-2">Fetch Path:</h3>
            <div className="p-2 bg-muted rounded-md">
              <code className="text-xs">{fetchPath}</code>
            </div>
          </div>

          <div>
            <h3 className="text-sm font-medium mb-2">Processed Sessions:</h3>
            <div className="p-2 bg-muted rounded-md">
              <pre className="text-xs overflow-auto max-h-40">
                {JSON.stringify(
                  {
                    count: processedSessions.length,
                    sample: processedSessions.slice(0, 1),
                  },
                  null,
                  2,
                )}
              </pre>
            </div>
          </div>

          <div>
            <h3 className="text-sm font-medium mb-2">Raw API Response:</h3>
            <div className="p-2 bg-muted rounded-md">
              <pre className="text-xs overflow-auto max-h-40">{JSON.stringify(rawResponse, null, 2)}</pre>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
