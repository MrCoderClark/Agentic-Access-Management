"use client";

import { useState } from "react";
import { Bot, Send, ChevronDown, ChevronRight, Shield } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface AgentStep {
  agent: string;
  action: string;
  detail: string;
}

interface RagSource {
  id: string;
  content: string;
  similarity: number;
}

interface AgentPolicyResult {
  approved: boolean;
  risk_score: number;
  reasoning: string;
  matched_policy_id: string | null;
  rag_sources: RagSource[];
  confidence: number;
}

interface AgentProvisioningResult {
  success: boolean;
  grant_id: string | null;
  ticket_id: string | null;
  message: string;
}

interface AgentResult {
  response: string;
  phase: string;
  steps: AgentStep[];
  intent: Record<string, unknown> | null;
  policy_result: AgentPolicyResult | null;
  provisioning_result: AgentProvisioningResult | null;
  error: string | null;
}

interface ScanResult {
  expired_revoked?: number;
  unused_grants?: number;
  policy_drift?: number;
  error?: string;
  details?: Record<string, unknown>;
}

const agentColors: Record<string, string> = {
  request_agent: "text-blue-400",
  policy_agent: "text-purple-400",
  provisioning_agent: "text-emerald-400",
  sentinel_agent: "text-yellow-400",
};

export default function AgentsPage() {
  const [message, setMessage] = useState("");
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<AgentResult | null>(null);
  const [history, setHistory] = useState<{ input: string; result: AgentResult }[]>([]);
  const [showSteps, setShowSteps] = useState(true);

  // Sentinel state
  const [scanning, setScanning] = useState(false);
  const [scanResult, setScanResult] = useState<ScanResult | null>(null);

  async function handleSubmit() {
    if (!message.trim() || running) return;
    setRunning(true);
    setResult(null);

    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002";
      const res = await fetch(`${API_BASE}/api/v1/agents/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, user_id: null }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Agent failed" }));
        throw new Error(err.detail || "Agent failed");
      }

      const data: AgentResult = await res.json();
      setResult(data);
      setHistory((prev) => [...prev, { input: message, result: data }]);
      setMessage("");
    } catch (err) {
      setResult({
        response: err instanceof Error ? err.message : "Agent pipeline failed",
        phase: "error",
        steps: [],
        intent: null,
        policy_result: null,
        provisioning_result: null,
        error: err instanceof Error ? err.message : "Unknown error",
      });
    } finally {
      setRunning(false);
    }
  }

  async function handleSentinelScan() {
    setScanning(true);
    setScanResult(null);
    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002";
      const res = await fetch(`${API_BASE}/api/v1/agents/sentinel/scan`, { method: "POST" });
      if (!res.ok) throw new Error("Scan failed");
      const data = await res.json();
      setScanResult(data);
    } catch {
      setScanResult({ error: "Sentinel scan failed" });
    } finally {
      setScanning(false);
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">AI Agents</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Natural language access requests processed by the agent pipeline
          </p>
        </div>
        <Button
          size="sm"
          variant="outline"
          onClick={handleSentinelScan}
          disabled={scanning}
        >
          <Shield className="h-4 w-4 mr-2" />
          {scanning ? "Scanning..." : "Run Sentinel Scan"}
        </Button>
      </div>

      {/* Sentinel Results */}
      {scanResult && (
        <div className="rounded-lg border border-border bg-card p-4 space-y-2">
          <h3 className="text-sm font-medium flex items-center gap-2">
            <Shield className="h-4 w-4 text-yellow-400" />
            Sentinel Scan Results
          </h3>
          {scanResult.error ? (
            <p className="text-sm text-destructive">{String(scanResult.error)}</p>
          ) : (
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div className="text-center">
                <div className="text-2xl font-bold text-red-400">{String(scanResult.expired_revoked || 0)}</div>
                <div className="text-xs text-muted-foreground">Expired (Revoked)</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-400">{String(scanResult.unused_grants || 0)}</div>
                <div className="text-xs text-muted-foreground">Unused Grants</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-400">{String(scanResult.policy_drift || 0)}</div>
                <div className="text-xs text-muted-foreground">Policy Drift</div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Chat Input */}
      <div className="rounded-lg border border-border bg-card p-4">
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="e.g. I need admin access to GitHub for the deployment..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter") handleSubmit(); }}
            className="flex-1 px-3 py-2 text-sm bg-muted/50 border border-border/80 rounded-md placeholder:text-muted-foreground/70 focus:outline-none focus:ring-1 focus:ring-ring"
            disabled={running}
          />
          <Button onClick={handleSubmit} disabled={running || !message.trim()}>
            <Send className="h-4 w-4 mr-2" />
            {running ? "Processing..." : "Send"}
          </Button>
        </div>
      </div>

      {/* Current Result */}
      {result && (
        <div className="rounded-lg border border-border bg-card p-5 space-y-4">
          {/* Response */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Bot className="h-5 w-5 text-primary" />
              <span className="text-sm font-medium">Agent Response</span>
              <Badge variant="outline" className="text-xs">
                {result.phase}
              </Badge>
            </div>
            <p className="text-sm whitespace-pre-wrap leading-relaxed pl-7">
              {result.response}
            </p>
          </div>

          {/* Reasoning Steps */}
          {result.steps.length > 0 && (
            <div className="border-t border-border pt-3">
              <button
                className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
                onClick={() => setShowSteps(!showSteps)}
              >
                {showSteps ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
                Reasoning chain ({result.steps.length} steps)
              </button>
              {showSteps && (
                <div className="mt-2 space-y-1 pl-4 border-l-2 border-border">
                  {result.steps.map((step, i) => (
                    <div key={i} className="text-xs flex gap-2">
                      <span className={`font-mono ${agentColors[step.agent] || "text-muted-foreground"}`}>
                        {step.agent}
                      </span>
                      <span className="text-muted-foreground">→</span>
                      <span className="font-medium">{step.action}</span>
                      {step.detail && (
                        <span className="text-muted-foreground truncate max-w-[300px]">
                          {step.detail}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* RAG Sources */}
          {result.policy_result?.rag_sources && result.policy_result.rag_sources.length > 0 && (
            <div className="border-t border-border pt-3">
              <h4 className="text-xs text-muted-foreground mb-2">RAG Sources Used</h4>
              <div className="space-y-1">
                {result.policy_result.rag_sources.map((src, i) => (
                  <div key={i} className="text-xs bg-muted/30 rounded px-2 py-1">
                    <span className="text-muted-foreground font-mono">
                      {(src.similarity * 100).toFixed(0)}%
                    </span>{" "}
                    {src.content.slice(0, 120)}...
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* History */}
      {history.length > 1 && (
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-muted-foreground">Previous Requests</h3>
          {history.slice(0, -1).reverse().map((item, i) => (
            <div key={i} className="rounded-lg border border-border/50 bg-card/50 p-3 space-y-1">
              <p className="text-xs text-muted-foreground">{item.input}</p>
              <p className="text-sm">{item.result.response.slice(0, 150)}</p>
            </div>
          ))}
        </div>
      )}

      {/* Empty state */}
      {!result && history.length === 0 && (
        <div className="rounded-lg border border-border bg-card p-12 text-center">
          <Bot className="h-10 w-10 text-muted-foreground mx-auto mb-3" />
          <h3 className="text-lg font-medium">Agent Pipeline</h3>
          <p className="text-sm text-muted-foreground mt-1 max-w-md mx-auto">
            Type an access request in natural language. The agent pipeline will parse your intent,
            evaluate policies, and provision access automatically if approved.
          </p>
          <div className="mt-4 flex flex-wrap gap-2 justify-center">
            {[
              "I need read access to the production database",
              "Can I get admin on GitHub for 4 hours?",
              "Request editor access to Confluence for onboarding docs",
            ].map((example) => (
              <button
                key={example}
                className="text-xs bg-muted/50 border border-border/60 rounded-md px-3 py-1.5 hover:bg-muted transition-colors"
                onClick={() => setMessage(example)}
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
