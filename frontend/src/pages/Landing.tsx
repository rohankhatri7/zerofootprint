import { Button } from "@/components/ui/button";
import ShieldMark3D from "@/components/ShieldMark3D";
import { getAuthUrl } from "@/lib/api";
import { useState } from "react";

export default function Landing() {
  const [loading, setLoading] = useState(false);
  const handleSignIn = async () => {
    setLoading(true);
    try {
      const data = await getAuthUrl();
      window.location.href = data.auth_url;
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen px-6 pb-16 pt-10">
      <section className="mx-auto flex w-full max-w-5xl flex-col gap-10">
        <div className="rounded-[32px] bg-ink px-10 py-12 text-sand shadow-2xl">
          <p className="text-sm uppercase tracking-[0.3em] text-mint">ZEROFOOTPRINT</p>
          <h1 className="mt-4 text-5xl font-semibold leading-tight md:text-6xl">
            Your data, your terms.
          </h1>
          <div className="mt-8 flex justify-center">
            <ShieldMark3D size={140} intensity={1} className="text-sand" />
          </div>
        </div>
        <div className="grid gap-6 md:grid-cols-3">
          {[
            {
              title: "Discover",
              text: "Find services tied to your email with evidence counts."
            },
            {
              title: "Decide",
              text: "Choose unsubscribe or delete data plus close account."
            },
            {
              title: "Confirm",
              text: "Review every email before it is sent from Gmail."
            }
          ].map((item) => (
            <div key={item.title} className="rounded-3xl bg-sand/70 p-6 shadow-lg">
              <h3 className="text-lg font-semibold text-ink">{item.title}</h3>
              <p className="mt-3 text-sm text-ink/70">{item.text}</p>
            </div>
          ))}
        </div>
        <div className="flex justify-center">
          <Button
            onClick={handleSignIn}
            disabled={loading}
            size="lg"
            className="w-full max-w-[420px] text-base"
          >
            {loading ? "Connecting" : "Sign in with Gmail"}
          </Button>
        </div>
      </section>
    </div>
  );
}
