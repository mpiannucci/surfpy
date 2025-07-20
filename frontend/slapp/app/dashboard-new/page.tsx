import { AuthChecker } from "@/components/auth-checker"
import { DashboardNew } from "@/components/dashboard-new"

export const dynamic = "force-dynamic"
export const revalidate = 0

export default function DashboardNewPage() {
  return (
    <div className="space-y-8">
      

      <AuthChecker>
        <DashboardNew />
      </AuthChecker>
    </div>
  )
}