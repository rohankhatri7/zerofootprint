import { Routes, Route, Navigate } from "react-router-dom";
import Landing from "@/pages/Landing";
import Dashboard from "@/pages/Dashboard";
import ServiceDetail from "@/pages/ServiceDetail";
import Requests from "@/pages/Requests";
import AuthCallback from "@/pages/AuthCallback";
import GmailCallback from "@/pages/GmailCallback";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/auth/callback" element={<AuthCallback />} />
      <Route path="/gmail/callback" element={<GmailCallback />} />
      <Route path="/app" element={<Dashboard />} />
      <Route path="/app/services/:id" element={<ServiceDetail />} />
      <Route path="/app/requests" element={<Requests />} />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}
