import { AuthChecker } from "@/components/auth-checker"
import { RefreshSessionsButton } from "@/components/refresh-sessions-button"
import { ComparisonTable } from "@/components/comparison-table"

export const dynamic = "force-dynamic" // Disable caching for this page
export const revalidate = 0 // Revalidate on every request

export default async function ComparisonPage() {
  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <div className="flex flex-col gap-2">
          <h1 className="text-3xl font-bold tracking-tight">Swell Comparison</h1>
          <p className="text-muted-foreground">Compare swell data across your surf sessions</p>
        </div>
        <RefreshSessionsButton />
      </div>

      <AuthChecker>
        <ComparisonTable />
      </AuthChecker>
    </div>
  )
}
