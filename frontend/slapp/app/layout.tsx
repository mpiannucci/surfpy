import type React from "react"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { ThemeProvider } from "@/components/theme-provider"
import { Navbar } from "@/components/navbar"
import { AuthProvider } from "@/lib/auth-context"
import { ProtectedRoute } from "@/components/protected-route"
import { Toaster } from "@/components/ui/toaster"
import { BottomNav } from "@/components/bottom-nav"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Surf Session Tracker",
  description: "Track and analyze your surf sessions",
    generator: 'v0.dev'
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthProvider>
          <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
            <ProtectedRoute>
              <div className="min-h-screen flex flex-col">
                <Navbar />
                <main className="flex-1 container mx-auto py-6 px-4 pb-20 md:pb-6">{children}</main>
                <footer className="border-t py-4 hidden md:block">
                  <div className="container mx-auto text-center text-sm text-muted-foreground">
                    © {new Date().getFullYear()} Surf Session Tracker
                  </div>
                </footer>
                <BottomNav />
              </div>
            </ProtectedRoute>
          </ThemeProvider>
          <Toaster />
        </AuthProvider>
      </body>
    </html>
  )
}
