import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import AppShell from "@/components/AppShell";
import { Button } from "@/components/ui/button";
import { apiFetch, getGmailConnectUrl } from "@/lib/api";
import { useRequireAuth } from "@/lib/auth";

interface ServiceAccount {
  id: number;
  service_name: string;
  domain: string;
  first_seen_at: string;
  last_seen_at: string;
  evidence_count: number;
}

export default function Dashboard() {
  useRequireAuth();
  const [services, setServices] = useState<ServiceAccount[]>([]);
  const [loading, setLoading] = useState(false);

  const loadServices = async () => {
    const data = await apiFetch("/services");
    setServices(data);
  };

  useEffect(() => {
    loadServices();
  }, []);

  const handleScan = async () => {
    setLoading(true);
    try {
      await apiFetch("/gmail/scan", { method: "POST" });
      await loadServices();
    } finally {
      setLoading(false);
    }
  };

  const handleConnectGmail = async () => {
    const data = await getGmailConnectUrl();
    window.location.href = data.auth_url;
  };

  return (
    <AppShell>
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-semibold">Dashboard</h2>
          <p className="mt-2 text-sm text-ink/70">
            Scan Gmail to discover accounts tied to your inbox.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" onClick={handleConnectGmail}>
            Connect Gmail
          </Button>
          <Button onClick={handleScan} disabled={loading}>
            {loading ? "Scanning" : "Scan Gmail"}
          </Button>
        </div>
      </div>

      <div className="mt-8 overflow-hidden rounded-3xl border border-ink/10 bg-sand/80">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-ink/5 text-xs uppercase tracking-wide text-ink/60">
            <tr>
              <th className="px-6 py-4">Service</th>
              <th className="px-6 py-4">Domain</th>
              <th className="px-6 py-4">First seen</th>
              <th className="px-6 py-4">Evidence</th>
              <th className="px-6 py-4"></th>
            </tr>
          </thead>
          <tbody>
            {services.map((service) => (
              <tr key={service.id} className="border-t border-ink/10">
                <td className="px-6 py-4 font-medium">{service.service_name}</td>
                <td className="px-6 py-4">{service.domain}</td>
                <td className="px-6 py-4">
                  {new Date(service.first_seen_at).toLocaleDateString()}
                </td>
                <td className="px-6 py-4">{service.evidence_count}</td>
                <td className="px-6 py-4">
                  <Link
                    to={`/app/services/${service.id}`}
                    className="text-sm font-semibold text-sea"
                  >
                    View
                  </Link>
                </td>
              </tr>
            ))}
            {services.length === 0 && (
              <tr>
                <td className="px-6 py-8 text-sm text-ink/60" colSpan={5}>
                  No services found yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </AppShell>
  );
}
