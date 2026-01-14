import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function GmailCallback() {
  const navigate = useNavigate();

  useEffect(() => {
    const timer = setTimeout(() => {
      navigate("/app", { replace: true });
    }, 1200);
    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <div className="min-h-screen px-6 pt-20 text-center">
      <p className="text-lg">Gmail connected. Returning to dashboard.</p>
    </div>
  );
}
