"use client";

import { useState } from "react";
import { BookOpen, Upload, Trash2, Search, FileText, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useApi, apiMutate } from "@/lib/use-api";

interface Document {
  id: string;
  content: string;
  doc_type: string;
  source_id: string | null;
  metadata: Record<string, unknown>;
  chunk_index: number;
  token_count: number | null;
  created_at: string;
}

interface DocumentListResponse {
  data: Document[];
  count: number;
}

interface SearchResult {
  id: string;
  content: string;
  metadata: Record<string, unknown>;
  doc_type: string;
  source_id: string | null;
  chunk_index: number;
  similarity: number;
}

interface SearchResponse {
  results: SearchResult[];
  query: string;
  count: number;
}

const docTypeColors: Record<string, string> = {
  policy: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  runbook: "bg-purple-500/10 text-purple-400 border-purple-500/20",
  decision: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  system_doc: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20",
  compliance: "bg-red-500/10 text-red-400 border-red-500/20",
};

const DOC_TYPES = ["policy", "runbook", "decision", "system_doc", "compliance"];

export default function KnowledgePage() {
  const [typeFilter, setTypeFilter] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadDocType, setUploadDocType] = useState("policy");
  const [showIngestModal, setShowIngestModal] = useState(false);
  const [manualContent, setManualContent] = useState("");

  // Search state
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<SearchResult[] | null>(null);
  const [searching, setSearching] = useState(false);

  const queryParams = typeFilter ? `?doc_type=${typeFilter}` : "";
  const { data, loading, error, refetch } = useApi<DocumentListResponse>(
    `/api/v1/documents${queryParams}`
  );

  const documents = data?.data ?? [];

  async function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadError(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("doc_type", uploadDocType);
    formData.append("metadata", JSON.stringify({ uploaded_by: "ui" }));

    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002";
      const res = await fetch(`${API_BASE}/api/v1/documents/ingest/file`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Upload failed" }));
        throw new Error(err.detail || "Upload failed");
      }
      await refetch();
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  }

  async function handleManualIngest() {
    if (!manualContent.trim()) return;
    setUploading(true);
    setUploadError(null);
    try {
      await apiMutate("/api/v1/documents/ingest", "POST", {
        content: manualContent,
        doc_type: uploadDocType,
        metadata: { uploaded_by: "ui", source: "manual_paste" },
      });
      setManualContent("");
      setShowIngestModal(false);
      await refetch();
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : "Ingestion failed");
    } finally {
      setUploading(false);
    }
  }

  async function handleSearch() {
    if (!searchQuery.trim()) {
      setSearchResults(null);
      return;
    }
    setSearching(true);
    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002";
      const res = await fetch(`${API_BASE}/api/v1/documents/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: searchQuery,
          match_count: 10,
          doc_type: typeFilter,
          similarity_threshold: 0.3,
        }),
      });
      if (!res.ok) throw new Error("Search failed");
      const data: SearchResponse = await res.json();
      setSearchResults(data.results);
    } catch {
      setSearchResults([]);
    } finally {
      setSearching(false);
    }
  }

  function clearSearch() {
    setSearchQuery("");
    setSearchResults(null);
  }

  const [deleteTargetId, setDeleteTargetId] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);

  async function confirmDelete() {
    if (!deleteTargetId) return;
    setDeleting(true);
    try {
      await apiMutate(`/api/v1/documents/${deleteTargetId}`, "DELETE");
      await refetch();
    } catch {
      // Silent fail
    } finally {
      setDeleting(false);
      setDeleteTargetId(null);
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Knowledge Base</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Documents powering RAG-based policy decisions
          </p>
        </div>
        <div className="flex gap-2">
          <Button size="sm" variant="outline" onClick={() => setShowIngestModal(true)}>
            <FileText className="h-4 w-4 mr-2" />
            Paste Text
          </Button>
          <label>
            <input
              type="file"
              accept=".txt,.md"
              className="hidden"
              onChange={handleFileUpload}
              disabled={uploading}
            />
            <Button size="sm" asChild disabled={uploading}>
              <span>
                <Upload className="h-4 w-4 mr-2" />
                {uploading ? "Uploading..." : "Upload File"}
              </span>
            </Button>
          </label>
        </div>
      </div>

      {uploadError && (
        <div className="text-sm text-destructive bg-destructive/10 border border-destructive/20 rounded-md px-3 py-2">
          {uploadError}
        </div>
      )}

      {/* Upload doc type selector */}
      <div className="flex items-center gap-3">
        <span className="text-xs text-muted-foreground">Upload as:</span>
        {DOC_TYPES.map((t) => (
          <Button
            key={t}
            variant={uploadDocType === t ? "default" : "outline"}
            size="sm"
            className="h-6 text-xs px-2"
            onClick={() => setUploadDocType(t)}
          >
            {t.replace("_", " ")}
          </Button>
        ))}
      </div>

      {/* Search bar */}
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Semantic search across documents..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter") handleSearch(); }}
            className="w-full pl-10 pr-8 py-2 text-sm bg-muted/50 border border-border/80 rounded-md placeholder:text-muted-foreground/70 focus:outline-none focus:ring-1 focus:ring-ring focus:border-ring"
          />
          {searchQuery && (
            <button
              type="button"
              onClick={clearSearch}
              className="absolute right-3 top-1/2 -translate-y-1/2"
            >
              <X className="h-4 w-4 text-muted-foreground hover:text-foreground" />
            </button>
          )}
        </div>
        <Button size="sm" disabled={searching} onClick={() => handleSearch()}>
          {searching ? "Searching..." : "Search"}
        </Button>
      </div>

      {/* Filter buttons */}
      <div className="flex gap-2 flex-wrap">
        <Button
          variant={typeFilter === null ? "secondary" : "ghost"}
          size="sm"
          onClick={() => { setTypeFilter(null); clearSearch(); }}
        >
          All
        </Button>
        {DOC_TYPES.map((t) => (
          <Button
            key={t}
            variant={typeFilter === t ? "secondary" : "ghost"}
            size="sm"
            onClick={() => { setTypeFilter(t); clearSearch(); }}
          >
            {t.replace("_", " ").replace(/\b\w/g, (c) => c.toUpperCase())}
          </Button>
        ))}
      </div>

      {/* Search Results */}
      {searchResults !== null ? (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-medium">
              {searchResults.length} result{searchResults.length !== 1 ? "s" : ""} for &quot;{searchQuery}&quot;
            </h2>
            <Button variant="ghost" size="sm" onClick={clearSearch}>
              Clear results
            </Button>
          </div>
          {searchResults.length === 0 ? (
            <div className="rounded-lg border border-border bg-card p-8 text-center">
              <Search className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
              <p className="text-sm text-muted-foreground">No matching documents found.</p>
            </div>
          ) : (
            <div className="space-y-2">
              {searchResults.map((result) => (
                <div
                  key={`${result.id}-${result.chunk_index}`}
                  className="rounded-lg border border-border bg-card p-4 space-y-2"
                >
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className={docTypeColors[result.doc_type] || ""}>
                      {result.doc_type.replace("_", " ")}
                    </Badge>
                    <span className="text-xs text-muted-foreground font-mono">
                      {(result.similarity * 100).toFixed(1)}% match
                    </span>
                    <span className="text-xs text-muted-foreground">
                      chunk #{result.chunk_index}
                    </span>
                  </div>
                  <p className="text-sm leading-relaxed">{result.content}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      ) : (
        /* Document list table */
        <>
          {loading ? (
            <div className="text-sm text-muted-foreground py-8 text-center">
              Loading documents...
            </div>
          ) : error ? (
            <div className="text-sm text-destructive py-8 text-center">{error}</div>
          ) : documents.length === 0 ? (
            <div className="rounded-lg border border-border bg-card p-12 text-center">
              <BookOpen className="h-10 w-10 text-muted-foreground mx-auto mb-3" />
              <h3 className="text-lg font-medium">No documents yet</h3>
              <p className="text-sm text-muted-foreground mt-1">
                Upload policies, runbooks, or compliance docs to power AI decisions.
              </p>
            </div>
          ) : (
            <div className="rounded-lg border border-border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Content Preview</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Tokens</TableHead>
                    <TableHead>Added</TableHead>
                    <TableHead className="w-[60px]"></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {documents.map((doc) => (
                    <TableRow key={doc.id}>
                      <TableCell className="font-medium max-w-[300px] truncate">
                        {(doc.metadata as Record<string, string>)?.filename || doc.content.slice(0, 80)}
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className={docTypeColors[doc.doc_type] || ""}>
                          {doc.doc_type.replace("_", " ")}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-muted-foreground text-xs font-mono">
                        {doc.token_count ?? "—"}
                      </TableCell>
                      <TableCell className="text-muted-foreground text-xs">
                        {new Date(doc.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7 text-destructive"
                          onClick={() => setDeleteTargetId(doc.id)}
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}

          {data && (
            <p className="text-xs text-muted-foreground">
              {data.count} document{data.count !== 1 ? "s" : ""} indexed
            </p>
          )}
        </>
      )}

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={!!deleteTargetId} onOpenChange={(open) => { if (!open && !deleting) setDeleteTargetId(null); }}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Document</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete this document and all its chunks from the knowledge base. This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={deleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={confirmDelete} disabled={deleting} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
              {deleting ? "Deleting..." : "Delete"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Manual Ingest Modal */}
      {showIngestModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
          <div className="bg-card border border-border rounded-lg p-6 w-full max-w-lg space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">Paste Document Content</h2>
              <button onClick={() => setShowIngestModal(false)}>
                <X className="h-5 w-5 text-muted-foreground hover:text-foreground" />
              </button>
            </div>
            <div className="space-y-2">
              <label className="text-sm text-muted-foreground">Document type</label>
              <div className="flex gap-2 flex-wrap">
                {DOC_TYPES.map((t) => (
                  <Button
                    key={t}
                    variant={uploadDocType === t ? "default" : "outline"}
                    size="sm"
                    className="h-7 text-xs"
                    onClick={() => setUploadDocType(t)}
                  >
                    {t.replace("_", " ")}
                  </Button>
                ))}
              </div>
            </div>
            <textarea
              placeholder="Paste policy text, runbook content, or compliance documentation..."
              value={manualContent}
              onChange={(e) => setManualContent(e.target.value)}
              className="w-full h-48 p-3 text-sm bg-background border border-border rounded-md resize-none focus:outline-none focus:ring-1 focus:ring-ring"
            />
            <div className="flex justify-end gap-2">
              <Button variant="ghost" size="sm" onClick={() => setShowIngestModal(false)}>
                Cancel
              </Button>
              <Button
                size="sm"
                onClick={handleManualIngest}
                disabled={uploading || !manualContent.trim()}
              >
                {uploading ? "Ingesting..." : "Ingest Document"}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
