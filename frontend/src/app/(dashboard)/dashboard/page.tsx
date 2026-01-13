/**
 * Dashboard Page - Main Dashboard View
 * Overview of user's activity and quick stats
 */

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome to your Auto Bidder dashboard
        </p>
      </div>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-lg border bg-card p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium text-muted-foreground">Total Projects</p>
            <span className="text-2xl">💼</span>
          </div>
          <p className="mt-2 text-3xl font-bold">0</p>
          <p className="mt-1 text-xs text-muted-foreground">+0 from last week</p>
        </div>

        <div className="rounded-lg border bg-card p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium text-muted-foreground">Proposals Generated</p>
            <span className="text-2xl">📝</span>
          </div>
          <p className="mt-2 text-3xl font-bold">0</p>
          <p className="mt-1 text-xs text-muted-foreground">0 / 10 this month</p>
        </div>

        <div className="rounded-lg border bg-card p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium text-muted-foreground">Win Rate</p>
            <span className="text-2xl">📈</span>
          </div>
          <p className="mt-2 text-3xl font-bold">0%</p>
          <p className="mt-1 text-xs text-muted-foreground">No data yet</p>
        </div>

        <div className="rounded-lg border bg-card p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium text-muted-foreground">Time Saved</p>
            <span className="text-2xl">⏱️</span>
          </div>
          <p className="mt-2 text-3xl font-bold">0h</p>
          <p className="mt-1 text-xs text-muted-foreground">This month</p>
        </div>
      </div>

      <div className="rounded-lg border bg-card p-6 shadow-sm">
        <h2 className="text-lg font-semibold">Quick Start</h2>
        <div className="mt-4 space-y-3">
          <div className="flex items-center gap-4 rounded-lg border p-4">
            <span className="text-2xl">1️⃣</span>
            <div>
              <p className="font-medium">Upload Knowledge Base Documents</p>
              <p className="text-sm text-muted-foreground">
                Add your portfolio, case studies, and team profiles
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4 rounded-lg border p-4">
            <span className="text-2xl">2️⃣</span>
            <div>
              <p className="font-medium">Configure Keywords</p>
              <p className="text-sm text-muted-foreground">
                Set up keywords to filter relevant job postings
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4 rounded-lg border p-4">
            <span className="text-2xl">3️⃣</span>
            <div>
              <p className="font-medium">Generate Your First Proposal</p>
              <p className="text-sm text-muted-foreground">
                Find a project and let AI create a customized proposal
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
