import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { apiFetch } from "@/lib/api";
import { useRequireAuth } from "@/lib/auth";

interface RequestItem {
  id: number;
  service_account_id: number;
  request_type: string;
  status: string;
  created_at: string;
}

const statusVariant = (status: string) => {
  if (status === "completed") return "success";
  if (status === "needs_info") return "warning";
  if (status === "failed") return "warning";
  return "muted";
};

export default function Requests() {
  useRequireAuth();
  const [requests, setRequests] = useState<RequestItem[]>([]);
  const [loading, setLoading] = useState(false);

  const loadRequests = async () => {
    const data = await apiFetch("/requests");
    setRequests(data);
  };

  useEffect(() => {
    loadRequests();
  }, []);

  const handleSync = async () => {
    setLoading(true);
    try {
      await apiFetch("/requests/sync", { method: "POST" });
      await loadRequests();
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppShell>
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-semibold">Requests</h2>
          <p className="mt-2 text-sm text-ink/70">Track responses and sync status updates.</p>
        </div>
        <Button onClick={handleSync} disabled={loading}>
          {loading ? "Syncing" : "Sync status"}
        </Button>
      </div>

      <div className="mt-8 grid gap-4">
        {requests.map((req) => (
          <div key={req.id} className="rounded-3xl border border-ink/10 bg-sand/80 p-6">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <div className="text-sm text-ink/60">Request #{req.id}</div>
                <div className="mt-1 text-lg font-semibold">{req.request_type}</div>
                <div className="mt-2 text-xs text-ink/60">
                  {new Date(req.created_at).toLocaleString()}
                </div>
              </div>
              <Badge variant={statusVariant(req.status)}>{req.status}</Badge>
            </div>
          </div>
        ))}
        {requests.length === 0 && (
          <div className="rounded-3xl border border-dashed border-ink/20 p-8 text-center text-sm text-ink/60">
            No requests yet.
          </div>
        )}
      </div>
    </AppShell>
  );
}
