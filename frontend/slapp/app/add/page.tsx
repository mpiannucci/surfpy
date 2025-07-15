import { Suspense } from "react"
import { SessionForm } from "@/components/session-form"

export default function AddSessionPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-2xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight">Add Surf Session</h1>
          <p className="text-muted-foreground mt-2">Record the details of your latest surf session</p>
        </div>

        <Suspense fallback={<div>Loading...</div>}>
          <SessionForm />
        </Suspense>
      </div>
    </div>
  )
}
