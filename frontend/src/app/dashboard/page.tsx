import { KeyRound, CheckCircle, Clock, Gauge } from "lucide-react";

function MetricCard({
  label,
  value,
  change,
  icon: Icon,
}: {
  label: string;
  value: string;
  change: string;
  icon: React.ComponentType<{ className?: string }>;
}) {
  return (
    <div className="rounded-lg border border-border bg-card p-5 transition-colors hover:border-[var(--border-strong,#2E3148)]">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium uppercase tracking-widest text-muted-foreground">
          {label}
        </span>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </div>
      <div className="mt-3">
        <span className="font-mono text-3xl font-semibold tracking-tight">
          {value}
        </span>
      </div>
      <p className="mt-1 text-xs text-muted-foreground">{change}</p>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      {/* Page title */}
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">
          Access Overview
        </h1>
        <p className="text-sm text-muted-foreground mt-1">
          Organization access health at a glance
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          label="Open Requests"
          value="12"
          change="+3 today"
          icon={KeyRound}
        />
        <MetricCard
          label="Auto-Approved"
          value="73%"
          change="▲ +5% this week"
          icon={CheckCircle}
        />
        <MetricCard
          label="Avg Decision"
          value="4.2s"
          change="▼ -1.1s from last week"
          icon={Clock}
        />
        <MetricCard
          label="Posture Score"
          value="87"
          change="▲ +2 from last week"
          icon={Gauge}
        />
      </div>

      {/* Placeholder sections */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-lg border border-border bg-card p-5">
          <h2 className="text-lg font-medium">Recent Agent Decisions</h2>
          <p className="mt-2 text-sm text-muted-foreground">
            Agent activity will appear here once connected.
          </p>
        </div>
        <div className="rounded-lg border border-border bg-card p-5">
          <h2 className="text-lg font-medium">Risk Distribution</h2>
          <p className="mt-2 text-sm text-muted-foreground">
            Risk breakdown charts will render here.
          </p>
        </div>
      </div>

      <div className="rounded-lg border border-border bg-card p-5">
        <h2 className="text-lg font-medium">Pending Approvals (0)</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          No pending approvals. Requests requiring review will appear here.
        </p>
      </div>
    </div>
  );
}
