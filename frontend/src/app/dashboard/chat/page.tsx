"use client";

import { useState, useRef, useEffect } from "react";
import { Bot, Send, User, BookOpen, Trash2, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface ChatSource {
  id: string;
  doc_type: string;
  content: string;
  similarity: number;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: ChatSource[];
}

const docTypeColors: Record<string, string> = {
  policy: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  runbook: "bg-purple-500/10 text-purple-400 border-purple-500/20",
  decision: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  system_doc: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20",
  compliance: "bg-red-500/10 text-red-400 border-red-500/20",
};

export default function DashboardChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  async function handleSend() {
    if (!input.trim() || sending) return;
    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setSending(true);

    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002";
      const res = await fetch(`${API_BASE}/api/v1/chat/message`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userMessage,
          session_id: sessionId,
          user_id: null,
        }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Chat failed" }));
        throw new Error(err.detail || "Chat failed");
      }

      const data = await res.json();
      setSessionId(data.session_id);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.response, sources: data.sources },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: err instanceof Error ? `Error: ${err.message}` : "Something went wrong." },
      ]);
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-6rem)]">
      {/* Header */}
      <div className="flex items-center justify-between pb-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Knowledge Chat</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Ask questions about policies, procedures, and compliance
          </p>
        </div>
        {messages.length > 0 && (
          <Button variant="ghost" size="sm" onClick={() => { setMessages([]); setSessionId(null); }}>
            <Trash2 className="h-4 w-4 mr-1" />
            Clear
          </Button>
        )}
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto space-y-4 pb-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <Sparkles className="h-10 w-10 text-muted-foreground mb-3" />
            <h2 className="text-lg font-medium">Ask the Knowledge Base</h2>
            <p className="text-sm text-muted-foreground mt-1 max-w-md">
              Get answers grounded in your organization&apos;s policies, runbooks, and compliance documentation.
            </p>
            <div className="mt-4 flex flex-wrap gap-2 justify-center max-w-lg">
              {[
                "What is the password policy?",
                "How are access reviews conducted?",
                "What systems require MFA?",
                "Explain the principle of least privilege",
              ].map((example) => (
                <button
                  key={example}
                  className="text-xs bg-muted/50 border border-border/60 rounded-md px-3 py-1.5 hover:bg-muted transition-colors"
                  onClick={() => setInput(example)}
                >
                  {example}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-3 ${msg.role === "user" ? "justify-end" : ""}`}>
            {msg.role === "assistant" && (
              <div className="h-7 w-7 rounded-full bg-primary/10 flex items-center justify-center shrink-0 mt-0.5">
                <Bot className="h-4 w-4 text-primary" />
              </div>
            )}
            <div className={`max-w-[75%] rounded-lg px-4 py-2.5 ${
              msg.role === "user"
                ? "bg-primary text-primary-foreground"
                : "bg-muted/50 border border-border/50"
            }`}>
              <p className="text-sm whitespace-pre-wrap leading-relaxed">{msg.content}</p>
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-2 pt-2 border-t border-border/30 flex flex-wrap gap-1">
                  {msg.sources.map((src, j) => (
                    <Badge key={j} variant="outline" className={`text-[10px] ${docTypeColors[src.doc_type] || ""}`}>
                      {src.doc_type.replace("_", " ")} {(src.similarity * 100).toFixed(0)}%
                    </Badge>
                  ))}
                </div>
              )}
            </div>
            {msg.role === "user" && (
              <div className="h-7 w-7 rounded-full bg-muted flex items-center justify-center shrink-0 mt-0.5">
                <User className="h-4 w-4 text-muted-foreground" />
              </div>
            )}
          </div>
        ))}

        {sending && (
          <div className="flex gap-3">
            <div className="h-7 w-7 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
              <Bot className="h-4 w-4 text-primary" />
            </div>
            <div className="bg-muted/50 border border-border/50 rounded-lg px-4 py-2.5">
              <div className="flex gap-1">
                <div className="h-2 w-2 rounded-full bg-muted-foreground/40 animate-bounce" style={{ animationDelay: "0ms" }} />
                <div className="h-2 w-2 rounded-full bg-muted-foreground/40 animate-bounce" style={{ animationDelay: "150ms" }} />
                <div className="h-2 w-2 rounded-full bg-muted-foreground/40 animate-bounce" style={{ animationDelay: "300ms" }} />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="border-t border-border pt-4">
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Ask about policies, access procedures, or compliance..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter") handleSend(); }}
            className="flex-1 px-4 py-2.5 text-sm bg-muted/50 border border-border/80 rounded-md placeholder:text-muted-foreground/70 focus:outline-none focus:ring-1 focus:ring-ring"
            disabled={sending}
          />
          <Button onClick={handleSend} disabled={sending || !input.trim()}>
            <Send className="h-4 w-4 mr-2" />
            {sending ? "..." : "Send"}
          </Button>
        </div>
      </div>
    </div>
  );
}
