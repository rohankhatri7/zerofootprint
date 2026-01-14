import { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

export default function AuthCallback() {
  const [params] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    const token = params.get("token");
    if (token) {
      localStorage.setItem("zf_token", token);
      navigate("/app", { replace: true });
    } else {
      navigate("/", { replace: true });
    }
  }, [params, navigate]);

  return (
    <div className="min-h-screen px-6 pt-20 text-center">
      <p className="text-lg">Signing you in.</p>
    </div>
  );
}
