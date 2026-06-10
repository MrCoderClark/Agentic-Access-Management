"use client";

import { useState } from "react";
import { KeyRound, Plus } from "lucide-react";
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

interface Ticket {
  id: string;
  requester_id: string;
  ticket_type: string;
  subject: string;
  status: string;
  priority: string;
  created_at: string;
  updated_at: string;
}

interface TicketListResponse {
  data: Ticket[];
  count: number;
}

const statusColors: Record<string, string> = {
  open: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  in_progress: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20",
  waiting_approval: "bg-purple-500/10 text-purple-400 border-purple-500/20",
  resolved: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  closed: "bg-muted text-muted-foreground border-border",
};

const priorityColors: Record<string, string> = {
  low: "text-muted-foreground",
  medium: "text-yellow-400",
  high: "text-orange-400",
  critical: "text-red-400",
};

export default function RequestsPage() {
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  const queryParams = new URLSearchParams();
  queryParams.set("ticket_type", "access_request");
  if (statusFilter) queryParams.set("status", statusFilter);

  const { data, loading, error } = useApi<TicketListResponse>(
    `/api/v1/tickets?${queryParams.toString()}`
  );

  const tickets = data?.data ?? [];
  const statuses = ["open", "in_progress", "waiting_approval", "resolved", "closed"];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Access Requests</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Review and manage access requests
          </p>
        </div>
        <Button size="sm">
          <Plus className="h-4 w-4 mr-2" />
          New Request
        </Button>
      </div>

      {/* Filters */}
      <div className="flex gap-2 flex-wrap">
        <Button
          variant={statusFilter === null ? "secondary" : "ghost"}
          size="sm"
          onClick={() => setStatusFilter(null)}
        >
          All
        </Button>
        {statuses.map((s) => (
          <Button
            key={s}
            variant={statusFilter === s ? "secondary" : "ghost"}
            size="sm"
            onClick={() => setStatusFilter(s)}
          >
            {s.replace("_", " ").replace(/\b\w/g, (c) => c.toUpperCase())}
          </Button>
        ))}
      </div>

      {/* Table */}
      {loading ? (
        <div className="text-sm text-muted-foreground py-8 text-center">
          Loading requests...
        </div>
      ) : error ? (
        <div className="text-sm text-destructive py-8 text-center">{error}</div>
      ) : tickets.length === 0 ? (
        <div className="rounded-lg border border-border bg-card p-12 text-center">
          <KeyRound className="h-10 w-10 text-muted-foreground mx-auto mb-3" />
          <h3 className="text-lg font-medium">No access requests</h3>
          <p className="text-sm text-muted-foreground mt-1">
            Access requests will appear here when submitted.
          </p>
        </div>
      ) : (
        <div className="rounded-lg border border-border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Subject</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Priority</TableHead>
                <TableHead>Created</TableHead>
                <TableHead>Updated</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {tickets.map((ticket) => (
                <TableRow key={ticket.id} className="cursor-pointer hover:bg-muted/50">
                  <TableCell className="font-medium max-w-[300px] truncate">
                    {ticket.subject}
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className={statusColors[ticket.status] || ""}>
                      {ticket.status.replace("_", " ")}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <span className={`text-xs font-medium ${priorityColors[ticket.priority] || ""}`}>
                      {ticket.priority}
                    </span>
                  </TableCell>
                  <TableCell className="text-muted-foreground text-xs">
                    {new Date(ticket.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell className="text-muted-foreground text-xs">
                    {new Date(ticket.updated_at).toLocaleDateString()}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      {data && (
        <p className="text-xs text-muted-foreground">
          {data.count} request{data.count !== 1 ? "s" : ""} total
        </p>
      )}
    </div>
  );
}
