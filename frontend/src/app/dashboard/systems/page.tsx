"use client";

import { useState } from "react";
import { Server, Plus, Pencil, Trash2 } from "lucide-react";
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

interface System {
  id: string;
  name: string;
  display_name: string | null;
  system_type: string | null;
  connector_type: string | null;
  risk_level: string;
  owner_id: string | null;
  created_at: string;
}

interface SystemListResponse {
  data: System[];
  count: number;
}

const riskColors: Record<string, string> = {
  low: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  medium: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20",
  high: "bg-orange-500/10 text-orange-400 border-orange-500/20",
  critical: "bg-red-500/10 text-red-400 border-red-500/20",
};

export default function SystemsPage() {
  const [typeFilter, setTypeFilter] = useState<string | null>(null);
  const queryParams = typeFilter ? `?system_type=${typeFilter}` : "";
  const { data, loading, error } = useApi<SystemListResponse>(
    `/api/v1/systems${queryParams}`
  );

  const systems = data?.data ?? [];
  const types = ["saas", "infrastructure", "internal"];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Systems</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Managed applications and infrastructure
          </p>
        </div>
        <Button size="sm">
          <Plus className="h-4 w-4 mr-2" />
          Add System
        </Button>
      </div>

      {/* Filters */}
      <div className="flex gap-2">
        <Button
          variant={typeFilter === null ? "secondary" : "ghost"}
          size="sm"
          onClick={() => setTypeFilter(null)}
        >
          All
        </Button>
        {types.map((t) => (
          <Button
            key={t}
            variant={typeFilter === t ? "secondary" : "ghost"}
            size="sm"
            onClick={() => setTypeFilter(t)}
          >
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </Button>
        ))}
      </div>

      {/* Table */}
      {loading ? (
        <div className="text-sm text-muted-foreground py-8 text-center">
          Loading systems...
        </div>
      ) : error ? (
        <div className="text-sm text-destructive py-8 text-center">{error}</div>
      ) : systems.length === 0 ? (
        <div className="rounded-lg border border-border bg-card p-12 text-center">
          <Server className="h-10 w-10 text-muted-foreground mx-auto mb-3" />
          <h3 className="text-lg font-medium">No systems yet</h3>
          <p className="text-sm text-muted-foreground mt-1">
            Add your first system to start managing access.
          </p>
        </div>
      ) : (
        <div className="rounded-lg border border-border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Connector</TableHead>
                <TableHead>Risk Level</TableHead>
                <TableHead>Added</TableHead>
                <TableHead className="w-[80px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {systems.map((system) => (
                <TableRow key={system.id}>
                  <TableCell className="font-medium">
                    {system.display_name || system.name}
                  </TableCell>
                  <TableCell className="text-muted-foreground">
                    {system.system_type || "—"}
                  </TableCell>
                  <TableCell className="text-muted-foreground">
                    {system.connector_type || "—"}
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant="outline"
                      className={riskColors[system.risk_level] || ""}
                    >
                      {system.risk_level}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-muted-foreground text-xs">
                    {new Date(system.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-1">
                      <Button variant="ghost" size="icon" className="h-7 w-7">
                        <Pencil className="h-3.5 w-3.5" />
                      </Button>
                      <Button variant="ghost" size="icon" className="h-7 w-7 text-destructive">
                        <Trash2 className="h-3.5 w-3.5" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      {/* Count */}
      {data && (
        <p className="text-xs text-muted-foreground">
          {data.count} system{data.count !== 1 ? "s" : ""} total
        </p>
      )}
    </div>
  );
}
