"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  KeyRound,
  ShieldCheck,
  Server,
  BookOpen,
  Users,
  Eye,
  Bot,
  MessageSquare,
  ScrollText,
  BarChart3,
  Settings,
} from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

const navGroups = [
  {
    items: [
      { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
      { label: "Requests", href: "/dashboard/requests", icon: KeyRound },
      { label: "Policies", href: "/dashboard/policies", icon: ShieldCheck },
      { label: "Systems", href: "/dashboard/systems", icon: Server },
      { label: "Knowledge", href: "/dashboard/knowledge", icon: BookOpen },
      { label: "Users", href: "/dashboard/users", icon: Users },
    ],
  },
  {
    items: [
      { label: "Reviews", href: "/dashboard/reviews", icon: Eye },
      { label: "Agents", href: "/dashboard/agents", icon: Bot },
      { label: "Chat", href: "/dashboard/chat", icon: MessageSquare },
      { label: "Audit", href: "/dashboard/audit", icon: ScrollText },
      { label: "Analytics", href: "/dashboard/analytics", icon: BarChart3 },
    ],
  },
];

const bottomNav = [
  { label: "Settings", href: "/dashboard/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <TooltipProvider delayDuration={0}>
      <aside className="group/sidebar fixed left-0 top-0 z-40 flex h-full w-16 flex-col border-r border-border bg-background transition-all duration-200 ease-out hover:w-[220px]">
        {/* Logo */}
        <div className="flex h-14 items-center px-4">
          <Link href="/dashboard" className="flex items-center gap-3">
            <ShieldCheck className="h-8 w-8 shrink-0 text-primary" />
            <span className="text-lg font-semibold tracking-tight opacity-0 transition-opacity duration-200 delay-50 group-hover/sidebar:opacity-100 whitespace-nowrap overflow-hidden">
              AgentGuard
            </span>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex flex-1 flex-col gap-1 px-2 pt-4">
          {navGroups.map((group, groupIdx) => (
            <div key={groupIdx}>
              {groupIdx > 0 && (
                <div className="my-3 border-t border-border" />
              )}
              <div className="flex flex-col gap-1">
                {group.items.map((item) => {
                  const isActive =
                    pathname === item.href ||
                    (item.href !== "/dashboard" &&
                      pathname.startsWith(item.href));

                  return (
                    <Tooltip key={item.href}>
                      <TooltipTrigger asChild>
                        <Link
                          href={item.href}
                          className={cn(
                            "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                            isActive
                              ? "border-l-[3px] border-primary bg-muted text-primary"
                              : "text-muted-foreground hover:bg-muted hover:text-foreground"
                          )}
                        >
                          <item.icon className="h-5 w-5 shrink-0" />
                          <span className="opacity-0 transition-opacity duration-200 delay-50 group-hover/sidebar:opacity-100 whitespace-nowrap overflow-hidden">
                            {item.label}
                          </span>
                        </Link>
                      </TooltipTrigger>
                      <TooltipContent
                        side="right"
                        className="group-hover/sidebar:hidden"
                      >
                        {item.label}
                      </TooltipContent>
                    </Tooltip>
                  );
                })}
              </div>
            </div>
          ))}

          {/* Bottom nav */}
          <div className="mt-auto pb-4">
            <div className="border-t border-border pt-3">
              {bottomNav.map((item) => {
                const isActive = pathname.startsWith(item.href);
                return (
                  <Tooltip key={item.href}>
                    <TooltipTrigger asChild>
                      <Link
                        href={item.href}
                        className={cn(
                          "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                          isActive
                            ? "border-l-[3px] border-primary bg-muted text-primary"
                            : "text-muted-foreground hover:bg-muted hover:text-foreground"
                        )}
                      >
                        <item.icon className="h-5 w-5 shrink-0" />
                        <span className="opacity-0 transition-opacity duration-200 delay-50 group-hover/sidebar:opacity-100 whitespace-nowrap overflow-hidden">
                          {item.label}
                        </span>
                      </Link>
                    </TooltipTrigger>
                    <TooltipContent
                      side="right"
                      className="group-hover/sidebar:hidden"
                    >
                      {item.label}
                    </TooltipContent>
                  </Tooltip>
                );
              })}
            </div>
          </div>
        </nav>
      </aside>
    </TooltipProvider>
  );
}
