"use client";

import { ShieldCheck, Plus, Pencil, Power } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useApi } from "@/lib/use-api";

interface Policy {
  id: string;
  name: string;
  description: string | null;
  system_id: string | null;
  auto_approve: boolean;
  is_active: boolean;
  max_duration_hours: number | null;
  risk_threshold: number | null;
  created_at: string;
  updated_at: string;
}

interface PolicyListResponse {
  data: Policy[];
  count: number;
}

export default function PoliciesPage() {
  const { data, loading, error } = useApi<PolicyListResponse>("/api/v1/policies");

  const policies = data?.data ?? [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Policies</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Access policies and approval rules
          </p>
        </div>
        <Button size="sm">
          <Plus className="h-4 w-4 mr-2" />
          Create Policy
        </Button>
      </div>

      {/* Table */}
      {loading ? (
        <div className="text-sm text-muted-foreground py-8 text-center">
          Loading policies...
        </div>
      ) : error ? (
        <div className="text-sm text-destructive py-8 text-center">{error}</div>
      ) : policies.length === 0 ? (
        <div className="rounded-lg border border-border bg-card p-12 text-center">
          <ShieldCheck className="h-10 w-10 text-muted-foreground mx-auto mb-3" />
          <h3 className="text-lg font-medium">No policies yet</h3>
          <p className="text-sm text-muted-foreground mt-1">
            Create your first policy to define access rules.
          </p>
        </div>
      ) : (
        <div className="rounded-lg border border-border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Auto-Approve</TableHead>
                <TableHead>Max Duration</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="w-[80px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {policies.map((policy) => (
                <TableRow key={policy.id}>
                  <TableCell className="font-medium">{policy.name}</TableCell>
                  <TableCell className="text-muted-foreground max-w-[200px] truncate">
                    {policy.description || "—"}
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant="outline"
                      className={
                        policy.auto_approve
                          ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                          : "bg-muted text-muted-foreground"
                      }
                    >
                      {policy.auto_approve ? "Yes" : "Manual"}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-muted-foreground">
                    {policy.max_duration_hours ? `${policy.max_duration_hours}h` : "Unlimited"}
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant="outline"
                      className={
                        policy.is_active
                          ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                          : "bg-red-500/10 text-red-400 border-red-500/20"
                      }
                    >
                      {policy.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-1">
                      <Button variant="ghost" size="icon" className="h-7 w-7">
                        <Pencil className="h-3.5 w-3.5" />
                      </Button>
                      <Button variant="ghost" size="icon" className="h-7 w-7">
                        <Power className="h-3.5 w-3.5" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      {data && (
        <p className="text-xs text-muted-foreground">
          {data.count} polic{data.count !== 1 ? "ies" : "y"} total
        </p>
      )}
    </div>
  );
}
