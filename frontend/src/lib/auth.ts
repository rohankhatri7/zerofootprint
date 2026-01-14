import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export function useRequireAuth() {
  const navigate = useNavigate();
  useEffect(() => {
    const token = localStorage.getItem("zf_token");
    if (!token) {
      navigate("/", { replace: true });
    }
  }, [navigate]);
}
