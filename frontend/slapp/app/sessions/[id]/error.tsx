"use client"

import { useEffect } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { AlertCircle } from "lucide-react"

export default function ErrorPage({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Safe error logging
    console.error("Session page error:", error?.message || "Unknown error")
  }, [error])

  const isNetworkError =
    error?.message?.includes("fetch failed") ||
    error?.message?.includes("Failed to fetch") ||
    error?.message?.includes("network") ||
    error?.message?.includes("CORS")

  return (
    <div className="flex h-[50vh] items-center justify-center">
      <Card className="max-w-md">
        <CardHeader>
          <div className="flex items-center gap-2 text-destructive">
            <AlertCircle className="h-5 w-5" />
            <CardTitle>Error Loading Session</CardTitle>
          </div>
          <CardDescription>
            {isNetworkError
              ? "There was a network error connecting to the API. Please check your connection and try again."
              : error?.message || "Something went wrong while loading the session."}
          </CardDescription>
          {error?.digest && (
            <CardDescription className="mt-2 text-xs text-muted-foreground">Error ID: {error.digest}</CardDescription>
          )}
        </CardHeader>
        <CardContent className="flex gap-4">
          <Button variant="outline" onClick={() => reset()}>
            Try again
          </Button>
          <Link href="/sessions">
            <Button>Back to Sessions</Button>
          </Link>
        </CardContent>
      </Card>
    </div>
  )
}
