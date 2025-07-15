"use client"

import type React from "react"

import { useEffect, useState } from "react"
import { useRouter, usePathname } from "next/navigation"
import { useAuth } from "@/lib/auth-context"
import { AuthChecker } from "@/components/auth-checker"

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth()
  const router = useRouter()
  const pathname = usePathname()
  const [redirecting, setRedirecting] = useState(false)

  useEffect(() => {
    // Skip protection for login and signup pages
    if (pathname === "/login" || pathname === "/signup") {
      return
    }

    // If not loading and not authenticated, redirect to login
    if (!isLoading && !isAuthenticated && !redirecting) {
      setRedirecting(true)
      router.push("/login")
    }
  }, [isAuthenticated, isLoading, router, pathname, redirecting])

  // Skip protection for login and signup pages
  if (pathname === "/login" || pathname === "/signup") {
    return <>{children}</>
  }

  // For protected pages, use AuthChecker
  return <AuthChecker>{children}</AuthChecker>
}
