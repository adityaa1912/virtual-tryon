import { useEffect, useState } from "react";
import axios from "axios";

type Status = "checking" | "online" | "offline";

const styles: Record<Status, string> = {
  checking: "bg-slate-100 text-slate-500",
  online: "bg-emerald-100 text-emerald-700",
  offline: "bg-rose-100 text-rose-700",
};

export default function HealthBadge() {
  const [status, setStatus] = useState<Status>("checking");

  useEffect(() => {
    axios
      .get("/health")
      .then((response) =>
        setStatus(response.data?.status === "running" ? "online" : "offline")
      )
      .catch(() => setStatus("offline"));
  }, []);

  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-medium ${styles[status]}`}
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      Backend: {status}
    </span>
  );
}
