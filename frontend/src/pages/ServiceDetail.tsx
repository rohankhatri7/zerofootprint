import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import AppShell from "@/components/AppShell";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle
} from "@/components/ui/dialog";
import { apiFetch } from "@/lib/api";
import { useRequireAuth } from "@/lib/auth";

interface ServiceAccount {
  id: number;
  service_name: string;
  domain: string;
  first_seen_at: string;
  last_seen_at: string;
  evidence_count: number;
}

interface Draft {
  to: string;
  subject: string;
  body: string;
}

export default function ServiceDetail() {
  useRequireAuth();
  const { id } = useParams();
  const navigate = useNavigate();
  const [service, setService] = useState<ServiceAccount | null>(null);
  const [draft, setDraft] = useState<Draft | null>(null);
  const [open, setOpen] = useState(false);
  const [confirm, setConfirm] = useState(false);
  const [sending, setSending] = useState(false);
  const [requestType, setRequestType] = useState<"unsubscribe" | "delete_close">("unsubscribe");

  useEffect(() => {
    const load = async () => {
      const data = await apiFetch(`/services/${id}`);
      setService(data);
    };
    load();
  }, [id]);

  const openDraft = async (type: "unsubscribe" | "delete_close") => {
    setRequestType(type);
    const data = await apiFetch("/requests/draft", {
      method: "POST",
      body: JSON.stringify({ service_account_id: Number(id), request_type: type })
    });
    setDraft(data);
    setConfirm(false);
    setOpen(true);
  };

  const handleSend = async () => {
    if (!draft) {
      return;
    }
    setSending(true);
    try {
      await apiFetch("/requests/send", {
        method: "POST",
        body: JSON.stringify({
          ...draft,
          service_account_id: Number(id),
          request_type: requestType,
          confirm
        })
      });
      setOpen(false);
      navigate("/app/requests");
    } finally {
      setSending(false);
    }
  };

  return (
    <AppShell>
      <div className="flex flex-wrap items-start justify-between gap-6">
        <div>
          <h2 className="text-3xl font-semibold">{service?.service_name}</h2>
          <p className="mt-2 text-sm text-ink/70">{service?.domain}</p>
          <div className="mt-4 flex flex-wrap gap-6 text-sm text-ink/70">
            <span>First seen {service ? new Date(service.first_seen_at).toLocaleDateString() : ""}</span>
            <span>Evidence {service?.evidence_count || 0}</span>
          </div>
        </div>
        <div className="flex flex-wrap gap-3">
          <Button variant="outline" onClick={() => openDraft("unsubscribe")}>Unsubscribe</Button>
          <Button onClick={() => openDraft("delete_close")}>Delete data plus close account</Button>
        </div>
      </div>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Review email draft</DialogTitle>
            <DialogDescription>
              Email will be sent from your Gmail account after confirmation.
            </DialogDescription>
          </DialogHeader>
          {draft && (
            <div className="grid gap-4">
              <label className="text-sm font-medium">To</label>
              <input
                className="rounded-xl border border-ink/10 bg-white px-3 py-2"
                value={draft.to}
                onChange={(e) => setDraft({ ...draft, to: e.target.value })}
              />
              <label className="text-sm font-medium">Subject</label>
              <input
                className="rounded-xl border border-ink/10 bg-white px-3 py-2"
                value={draft.subject}
                onChange={(e) => setDraft({ ...draft, subject: e.target.value })}
              />
              <label className="text-sm font-medium">Body</label>
              <textarea
                className="min-h-[160px] rounded-xl border border-ink/10 bg-white px-3 py-2"
                value={draft.body}
                onChange={(e) => setDraft({ ...draft, body: e.target.value })}
              />
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={confirm}
                  onChange={(e) => setConfirm(e.target.checked)}
                />
                I confirm this email should be sent.
              </label>
              <div className="flex flex-wrap justify-end gap-3">
                <Button variant="outline" onClick={() => setOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleSend} disabled={!confirm || sending}>
                  {sending ? "Sending" : "Send email"}
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </AppShell>
  );
}
