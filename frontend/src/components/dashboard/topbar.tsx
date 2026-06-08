"use client";

import { usePathname } from "next/navigation";
import { Search, Bell } from "lucide-react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

const routeLabels: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/dashboard/requests": "Access Requests",
  "/dashboard/policies": "Policies",
  "/dashboard/systems": "Systems",
  "/dashboard/knowledge": "Knowledge Base",
  "/dashboard/reviews": "Access Reviews",
  "/dashboard/agents": "Agent Observatory",
  "/dashboard/audit": "Audit Log",
  "/dashboard/analytics": "Analytics",
  "/dashboard/settings": "Settings",
};

function getBreadcrumb(pathname: string): string[] {
  const parts = pathname.split("/").filter(Boolean);
  const crumbs: string[] = [];

  let currentPath = "";
  for (const part of parts) {
    currentPath += `/${part}`;
    const label = routeLabels[currentPath];
    if (label) crumbs.push(label);
  }

  return crumbs.length > 0 ? crumbs : ["Dashboard"];
}

export function Topbar() {
  const pathname = usePathname();
  const breadcrumb = getBreadcrumb(pathname);

  return (
    <header className="sticky top-0 z-30 flex h-14 items-center justify-between border-b border-border bg-background px-8">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 text-sm">
        {breadcrumb.map((crumb, idx) => (
          <span key={idx} className="flex items-center gap-2">
            {idx > 0 && (
              <span className="text-muted-foreground">/</span>
            )}
            <span
              className={
                idx === breadcrumb.length - 1
                  ? "text-foreground font-medium"
                  : "text-muted-foreground"
              }
            >
              {crumb}
            </span>
          </span>
        ))}
      </nav>

      {/* Right actions */}
      <div className="flex items-center gap-2">
        {/* Search */}
        <Button variant="ghost" size="icon" className="text-muted-foreground">
          <Search className="h-4 w-4" />
          <span className="sr-only">Search</span>
        </Button>

        {/* Notifications */}
        <Button variant="ghost" size="icon" className="relative text-muted-foreground">
          <Bell className="h-4 w-4" />
          <Badge className="absolute -top-1 -right-1 h-4 w-4 rounded-full p-0 flex items-center justify-center text-[10px]">
            3
          </Badge>
          <span className="sr-only">Notifications</span>
        </Button>

        {/* User avatar */}
        <Avatar className="h-8 w-8 cursor-pointer">
          <AvatarFallback className="bg-primary text-primary-foreground text-xs font-medium">
            AG
          </AvatarFallback>
        </Avatar>
      </div>
    </header>
  );
}
