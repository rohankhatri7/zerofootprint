import { Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";

export default function AppShell({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const navItems = [
    { label: "Dashboard", to: "/app" },
    { label: "Requests", to: "/app/requests" }
  ];

  return (
    <div className="min-h-screen px-6 pb-12 pt-8">
      <header className="mx-auto flex w-full max-w-6xl items-center justify-between gap-4">
        <Link to="/" className="text-xl font-semibold">
          ZeroFootprint
        </Link>
        <nav className="flex items-center gap-4">
          {navItems.map((item) => (
            <Link
              key={item.to}
              to={item.to}
              className={cn(
                "rounded-full px-4 py-2 text-sm font-medium",
                location.pathname === item.to ? "bg-ink text-sand" : "text-ink"
              )}
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </header>
      <main className="mx-auto mt-10 w-full max-w-6xl">{children}</main>
    </div>
  );
}
