"use client"

import type React from "react"

import { useEffect, useState } from "react"
import { useAuth } from "@/lib/auth-context"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import Link from "next/link"

interface AuthCheckerProps {
  children: React.ReactNode
}

export function AuthChecker({ children }: AuthCheckerProps) {
  const { isAuthenticated, isLoading } = useAuth()
  const [isClient, setIsClient] = useState(false)

  // Use a simple useEffect to set isClient to true once mounted
  // This avoids the infinite loop issue
  useEffect(() => {
    setIsClient(true)
  }, [])

  // Show nothing during server-side rendering
  if (!isClient) {
    return null
  }

  // Show loading state
  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[200px]">
        <div className="animate-pulse">Loading...</div>
      </div>
    )
  }

  // If not authenticated, show login prompt
  if (!isAuthenticated) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Welcome to Surf Tracker</CardTitle>
          <CardDescription>
            Please log in to view your surf sessions or create a new account to get started.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex gap-4">
          <Link href="/login">
            <Button>Log In</Button>
          </Link>
          <Link href="/signup">
            <Button variant="outline">Sign Up</Button>
          </Link>
        </CardContent>
      </Card>
    )
  }

  // If authenticated, show children
  return <>{children}</>
}
