"use client";

import { useState, useEffect } from "react";
import { Eye, Plus, CheckCircle, XCircle, AlertTriangle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface ReviewStats {
  total_active_grants: number;
  high_risk: number;
  medium_risk: number;
  low_risk: number;
  stale_grants: number;
  systems_covered: number;
  review_coverage: number;
}

interface ReviewItem {
  id: string;
  grant_id: string;
  user_id: string;
  system_id: string;
  permission: string;
  risk_score: number;
  granted_at: string | null;
  status: string;
  recommendation: string;
}

interface Campaign {
  campaign_id: string;
  name: string;
  scope: string;
  total_items: number;
  items: ReviewItem[];
  due_date: string;
}

const recommendationColors: Record<string, string> = {
  certify: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  revoke: "bg-red-500/10 text-red-400 border-red-500/20",
  review_with_justification: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20",
};

export default function ReviewsPage() {
  const [stats, setStats] = useState<ReviewStats | null>(null);
  const [campaign, setCampaign] = useState<Campaign | null>(null);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002";

  async function fetchStats() {
    try {
      const res = await fetch(`${API_BASE}/api/v1/reviews/stats`);
      if (res.ok) setStats(await res.json());
    } catch (err) {
      console.error("Failed to fetch review stats:", err);
    }
  }

  useEffect(() => { fetchStats(); }, []);

  async function handleCreateCampaign(scope: string) {
    setCreating(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/reviews/campaigns`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scope }),
      });
      if (res.ok) {
        const data = await res.json();
        setCampaign(data);
      }
    } catch (err) {
      console.error("Campaign creation failed:", err);
    } finally {
      setCreating(false);
    }
  }

  async function handleDecision(grantId: string, decision: string) {
    try {
      await fetch(`${API_BASE}/api/v1/reviews/decide`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          grant_id: grantId,
          decision,
          reviewer_id: "admin",
          reason: "Dashboard review",
        }),
      });
      // Remove from items list
      if (campaign) {
        setCampaign({
          ...campaign,
          items: campaign.items.filter((i) => i.grant_id !== grantId),
        });
      }
      fetchStats();
    } catch (err) {
      console.error("Decision failed:", err);
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Access Reviews</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Continuous access certification and review campaigns
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => handleCreateCampaign("high_risk")} disabled={creating}>
            <AlertTriangle className="h-4 w-4 mr-2 text-yellow-400" />
            Review High Risk
          </Button>
          <Button size="sm" onClick={() => handleCreateCampaign("all")} disabled={creating}>
            <Plus className="h-4 w-4 mr-2" />
            {creating ? "Creating..." : "New Campaign"}
          </Button>
        </div>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="rounded-lg border border-border bg-card p-3 text-center">
            <div className="text-2xl font-bold">{stats.total_active_grants}</div>
            <div className="text-xs text-muted-foreground">Active Grants</div>
          </div>
          <div className="rounded-lg border border-border bg-card p-3 text-center">
            <div className="text-2xl font-bold text-red-400">{stats.high_risk}</div>
            <div className="text-xs text-muted-foreground">High Risk</div>
          </div>
          <div className="rounded-lg border border-border bg-card p-3 text-center">
            <div className="text-2xl font-bold text-yellow-400">{stats.stale_grants}</div>
            <div className="text-xs text-muted-foreground">Stale ({">"}90 days)</div>
          </div>
          <div className="rounded-lg border border-border bg-card p-3 text-center">
            <div className="text-2xl font-bold text-blue-400">{stats.systems_covered}</div>
            <div className="text-xs text-muted-foreground">Systems</div>
          </div>
        </div>
      )}

      {/* Campaign Results */}
      {campaign && (
        <div className="rounded-lg border border-border bg-card p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-medium">{campaign.name}</h2>
              <p className="text-xs text-muted-foreground">
                {campaign.total_items} items · Due {new Date(campaign.due_date).toLocaleDateString()}
              </p>
            </div>
            <Badge variant="outline">{campaign.scope}</Badge>
          </div>

          {campaign.items.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-4">
              All items reviewed. Campaign complete.
            </p>
          ) : (
            <div className="space-y-2">
              {campaign.items.map((item) => (
                <div key={item.id} className="flex items-center gap-3 rounded-md border border-border/50 p-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-mono truncate">{item.permission}</span>
                      <Badge variant="outline" className={`text-[10px] ${recommendationColors[item.recommendation] || ""}`}>
                        {item.recommendation.replace(/_/g, " ")}
                      </Badge>
                    </div>
                    <div className="text-xs text-muted-foreground mt-0.5">
                      Grant: {item.grant_id.slice(0, 8)}... · Risk: {((item.risk_score || 0) * 100).toFixed(0)}%
                    </div>
                  </div>
                  <div className="flex gap-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-7 text-emerald-400 hover:text-emerald-300"
                      onClick={() => handleDecision(item.grant_id, "certify")}
                    >
                      <CheckCircle className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-7 text-red-400 hover:text-red-300"
                      onClick={() => handleDecision(item.grant_id, "revoke")}
                    >
                      <XCircle className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Empty state */}
      {!campaign && (
        <div className="rounded-lg border border-border bg-card p-12 text-center">
          <Eye className="h-10 w-10 text-muted-foreground mx-auto mb-3" />
          <h3 className="text-lg font-medium">No Active Campaign</h3>
          <p className="text-sm text-muted-foreground mt-1 max-w-md mx-auto">
            Start a review campaign to certify or revoke existing access grants.
            High-risk reviews focus on grants with elevated risk scores.
          </p>
        </div>
      )}
    </div>
  );
}
