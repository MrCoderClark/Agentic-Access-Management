import { ShieldCheck } from "lucide-react";

export default function Home() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center space-y-6">
        <div className="flex items-center justify-center gap-3">
          <ShieldCheck className="h-10 w-10 text-primary" />
          <h1 className="text-4xl font-semibold tracking-tight">AgentGuard</h1>
        </div>
        <p className="text-muted-foreground max-w-md mx-auto">
          AI-native Access Governance & ITSM Platform
        </p>
        <div className="flex gap-3 justify-center font-mono text-xs text-muted-foreground">
          <span className="px-2 py-1 rounded bg-card border border-border">Next.js 16</span>
          <span className="px-2 py-1 rounded bg-card border border-border">FastAPI</span>
          <span className="px-2 py-1 rounded bg-card border border-border">Supabase</span>
          <span className="px-2 py-1 rounded bg-card border border-border">LangGraph</span>
        </div>
      </div>
    </div>
  );
}
