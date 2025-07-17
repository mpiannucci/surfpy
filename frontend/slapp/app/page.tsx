import { AuthChecker } from "@/components/auth-checker"
import { DashboardNew } from "@/components/dashboard-new"

export const dynamic = "force-dynamic" // Disable caching for this page
export const revalidate = 0 // Revalidate on every request

export default async function Home() {
  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">Track and analyze your surf sessions</p>
      </div>

      <AuthChecker>
        <DashboardNew />
      </AuthChecker>
    </div>
  )
}
