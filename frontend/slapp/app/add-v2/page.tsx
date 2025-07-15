import { Suspense } from "react"
import { SessionFormV2 } from "@/components/session-form-v2"

export default function AddNewSessionPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-2xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight">Add New Surf Session</h1>
          <p className="text-muted-foreground mt-2">Record the details of your latest surf session (v2)</p>
        </div>

        <Suspense fallback={<div>Loading...</div>}>
          <SessionFormV2 />
        </Suspense>
      </div>
    </div>
  )
}
