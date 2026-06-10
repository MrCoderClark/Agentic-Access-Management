"use client";

import { useState, useEffect } from "react";
import { BarChart3, Shield, TrendingUp, Users, Server, AlertTriangle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface Overview {
  total_users: number;
  total_systems: number;
  active_grants: number;
  total_grants: number;
  active_policies: number;
  avg_risk_score: number;
}

interface RiskDistribution {
  distribution: Record<string, number>;
  total: number;
}

interface SecurityPosture {
  overall_score: number;
  factors: Record<string, number>;
  grade: string;
  total_active_grants: number;
}

interface HeatmapItem {
  system_id: string;
  name: string;
  environment: string;
  grant_count: number;
  avg_risk: number;
  max_risk: number;
  permissions: string[];
}

const riskColors: Record<string, string> = {
  critical: "bg-red-500",
  high: "bg-orange-500",
  medium: "bg-yellow-500",
  low: "bg-blue-500",
  minimal: "bg-emerald-500",
};

const gradeColors: Record<string, string> = {
  A: "text-emerald-400",
  B: "text-blue-400",
  C: "text-yellow-400",
  D: "text-orange-400",
  F: "text-red-400",
};

export default function AnalyticsPage() {
  const [overview, setOverview] = useState<Overview | null>(null);
  const [riskDist, setRiskDist] = useState<RiskDistribution | null>(null);
  const [posture, setPosture] = useState<SecurityPosture | null>(null);
  const [heatmap, setHeatmap] = useState<HeatmapItem[]>([]);
  const [loading, setLoading] = useState(true);

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002";

  async function fetchAll() {
    setLoading(true);
    try {
      const [ov, rd, sp, hm] = await Promise.all([
        fetch(`${API_BASE}/api/v1/analytics/overview`).then((r) => r.json()),
        fetch(`${API_BASE}/api/v1/analytics/risk-distribution`).then((r) => r.json()),
        fetch(`${API_BASE}/api/v1/analytics/security-posture`).then((r) => r.json()),
        fetch(`${API_BASE}/api/v1/analytics/risk-heatmap`).then((r) => r.json()),
      ]);
      setOverview(ov);
      setRiskDist(rd);
      setPosture(sp);
      setHeatmap(hm);
    } catch (err) {
      console.error("Analytics fetch failed:", err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { fetchAll(); }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Analytics & Security Posture</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Risk metrics, grant trends, and security posture overview
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={fetchAll} disabled={loading}>
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      {/* Overview Cards */}
      {overview && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          <StatCard icon={Users} label="Users" value={overview.total_users} />
          <StatCard icon={Server} label="Systems" value={overview.total_systems} />
          <StatCard icon={Shield} label="Active Grants" value={overview.active_grants} />
          <StatCard icon={BarChart3} label="Total Grants" value={overview.total_grants} />
          <StatCard icon={Shield} label="Policies" value={overview.active_policies} />
          <StatCard
            icon={AlertTriangle}
            label="Avg Risk"
            value={overview.avg_risk_score.toFixed(2)}
            highlight={overview.avg_risk_score >= 0.6}
          />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Security Posture */}
        {posture && (
          <div className="rounded-lg border border-border bg-card p-5">
            <h2 className="text-sm font-medium mb-4 flex items-center gap-2">
              <Shield className="h-4 w-4 text-primary" />
              Security Posture
            </h2>
            <div className="flex items-center gap-6 mb-4">
              <div className="text-center">
                <div className={`text-4xl font-bold ${gradeColors[posture.grade] || "text-foreground"}`}>
                  {posture.grade}
                </div>
                <div className="text-xs text-muted-foreground">Grade</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">{posture.overall_score.toFixed(0)}</div>
                <div className="text-xs text-muted-foreground">Score / 100</div>
              </div>
            </div>
            <div className="space-y-2">
              {Object.entries(posture.factors).map(([key, value]) => (
                <div key={key} className="flex items-center gap-2">
                  <span className="text-xs text-muted-foreground w-36 capitalize">
                    {key.replace(/_/g, " ")}
                  </span>
                  <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${value >= 70 ? "bg-emerald-500" : value >= 40 ? "bg-yellow-500" : "bg-red-500"}`}
                      style={{ width: `${value}%` }}
                    />
                  </div>
                  <span className="text-xs font-mono w-8 text-right">{value}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Risk Distribution */}
        {riskDist && (
          <div className="rounded-lg border border-border bg-card p-5">
            <h2 className="text-sm font-medium mb-4 flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-yellow-400" />
              Risk Distribution
            </h2>
            <div className="space-y-3">
              {Object.entries(riskDist.distribution).map(([level, count]) => (
                <div key={level} className="flex items-center gap-3">
                  <div className={`h-3 w-3 rounded-full ${riskColors[level] || "bg-muted"}`} />
                  <span className="text-sm capitalize w-20">{level}</span>
                  <div className="flex-1 h-3 bg-muted rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${riskColors[level] || "bg-muted-foreground"}`}
                      style={{ width: riskDist.total ? `${(count / riskDist.total) * 100}%` : "0%" }}
                    />
                  </div>
                  <span className="text-sm font-mono w-8 text-right">{count}</span>
                </div>
              ))}
            </div>
            <div className="mt-3 pt-3 border-t border-border text-xs text-muted-foreground text-center">
              {riskDist.total} active grants total
            </div>
          </div>
        )}
      </div>

      {/* Risk Heatmap */}
      {heatmap.length > 0 && (
        <div className="rounded-lg border border-border bg-card p-5">
          <h2 className="text-sm font-medium mb-4 flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-orange-400" />
            System Risk Heatmap
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {heatmap.map((item) => (
              <div
                key={item.system_id}
                className="rounded-md border border-border/50 p-3 space-y-1"
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium truncate">{item.name}</span>
                  <Badge variant="outline" className="text-[10px]">
                    {item.environment}
                  </Badge>
                </div>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <span>{item.grant_count} grants</span>
                  <span>·</span>
                  <span>avg {(item.avg_risk * 100).toFixed(0)}%</span>
                  <span>·</span>
                  <span>max {(item.max_risk * 100).toFixed(0)}%</span>
                </div>
                {/* Risk bar */}
                <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${
                      item.avg_risk >= 0.7 ? "bg-red-500" : item.avg_risk >= 0.4 ? "bg-yellow-500" : "bg-emerald-500"
                    }`}
                    style={{ width: `${item.avg_risk * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty state */}
      {!loading && !overview && (
        <div className="rounded-lg border border-border bg-card p-12 text-center">
          <BarChart3 className="h-10 w-10 text-muted-foreground mx-auto mb-3" />
          <h3 className="text-lg font-medium">No Data Yet</h3>
          <p className="text-sm text-muted-foreground mt-1">
            Analytics will populate as access grants and policies are created.
          </p>
        </div>
      )}
    </div>
  );
}

function StatCard({
  icon: Icon,
  label,
  value,
  highlight = false,
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: string | number;
  highlight?: boolean;
}) {
  return (
    <div className="rounded-lg border border-border bg-card p-3 text-center">
      <Icon className={`h-4 w-4 mx-auto mb-1 ${highlight ? "text-red-400" : "text-muted-foreground"}`} />
      <div className={`text-lg font-bold ${highlight ? "text-red-400" : ""}`}>{value}</div>
      <div className="text-[10px] text-muted-foreground">{label}</div>
    </div>
  );
}
