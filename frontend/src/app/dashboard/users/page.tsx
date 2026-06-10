"use client";

import { useState } from "react";
import { Users, Plus } from "lucide-react";
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

interface User {
  id: string;
  email: string;
  full_name: string;
  department: string | null;
  title: string | null;
  status: string;
  risk_score: number;
  groups: string[];
  created_at: string;
}

interface UserListResponse {
  data: User[];
  count: number;
}

const statusColors: Record<string, string> = {
  active: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  suspended: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20",
  offboarded: "bg-red-500/10 text-red-400 border-red-500/20",
};

export default function UsersPage() {
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  const queryParams = statusFilter ? `?status=${statusFilter}` : "";
  const { data, loading, error } = useApi<UserListResponse>(
    `/api/v1/users${queryParams}`
  );

  const users = data?.data ?? [];
  const statuses = ["active", "suspended", "offboarded"];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Users</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Manage organization members and roles
          </p>
        </div>
        <Button size="sm">
          <Plus className="h-4 w-4 mr-2" />
          Add User
        </Button>
      </div>

      {/* Filters */}
      <div className="flex gap-2">
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
            {s.charAt(0).toUpperCase() + s.slice(1)}
          </Button>
        ))}
      </div>

      {/* Table */}
      {loading ? (
        <div className="text-sm text-muted-foreground py-8 text-center">
          Loading users...
        </div>
      ) : error ? (
        <div className="text-sm text-destructive py-8 text-center">{error}</div>
      ) : users.length === 0 ? (
        <div className="rounded-lg border border-border bg-card p-12 text-center">
          <Users className="h-10 w-10 text-muted-foreground mx-auto mb-3" />
          <h3 className="text-lg font-medium">No users yet</h3>
          <p className="text-sm text-muted-foreground mt-1">
            Add users from your identity provider or manually.
          </p>
        </div>
      ) : (
        <div className="rounded-lg border border-border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Department</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Risk</TableHead>
                <TableHead>Joined</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {users.map((user) => (
                <TableRow key={user.id}>
                  <TableCell className="font-medium">{user.full_name}</TableCell>
                  <TableCell className="text-muted-foreground">{user.email}</TableCell>
                  <TableCell className="text-muted-foreground">
                    {user.department || "—"}
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className={statusColors[user.status] || ""}>
                      {user.status}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <span
                      className={`font-mono text-xs ${
                        user.risk_score > 0.7
                          ? "text-red-400"
                          : user.risk_score > 0.4
                          ? "text-yellow-400"
                          : "text-emerald-400"
                      }`}
                    >
                      {user.risk_score.toFixed(1)}
                    </span>
                  </TableCell>
                  <TableCell className="text-muted-foreground text-xs">
                    {new Date(user.created_at).toLocaleDateString()}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      {data && (
        <p className="text-xs text-muted-foreground">
          {data.count} user{data.count !== 1 ? "s" : ""} total
        </p>
      )}
    </div>
  );
}
