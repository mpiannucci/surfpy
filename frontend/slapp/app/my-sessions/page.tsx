import { ClientMySessions } from "@/components/client-my-sessions"

export default function MySessionsPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">My Sessions</h1>
        <p className="text-muted-foreground">View and manage your surf sessions</p>
      </div>
      <ClientMySessions />
    </div>
  )
}
