"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { useRouter } from "next/navigation";

export default function RemindersPage() {
  const router = useRouter();
  const [items, setItems] = useState<any[]>([]);
  const [remindAt, setRemindAt] = useState("");
  const [type, setType] = useState("APPOINTMENT");
  const [err, setErr] = useState("");

  const token = typeof window !== "undefined" ? getToken() : null;

  const load = async () => {
    if (!token) return;
    const res = await api<{ items: any[] }>("/reminders", {}, token);
    setItems(res.items);
  };

  useEffect(() => {
    if (!token) { router.push("/"); return; }
    load();
  }, []);

  const create = async () => {
    setErr("");
    try {
      if (!token) return;
      await api(
        "/reminders",
        { method: "POST", body: JSON.stringify({ remind_at: remindAt, type, payload_json: {} }) },
        token
      );
      setRemindAt("");
      await load();
    } catch (e: any) {
      setErr(e.message || "Failed to create reminder.");
    }
  };

  return (
    <main style={{ maxWidth: 860, margin: "20px auto", padding: 16, fontFamily: "system-ui" }}>
      <h1>Reminders</h1>
      <div style={{ display: "grid", gap: 8, maxWidth: 420 }}>
        <input value={remindAt} onChange={(e) => setRemindAt(e.target.value)} placeholder="2025-12-17T20:00:00Z" />
        <input value={type} onChange={(e) => setType(e.target.value)} placeholder="Type" />
        <button onClick={create} style={{ padding: "8px 12px", width: 140 }}>Add</button>
      </div>
      {err ? <p style={{ color: "crimson" }}>{err}</p> : null}
      <ul style={{ marginTop: 16 }}>
        {items.map((r) => (
          <li key={r.id} style={{ padding: 10, border: "1px solid #ddd", marginBottom: 8 }}>
            <div><b>{r.type}</b> at {r.remind_at}</div>
            <small>Status: {r.status}</small>
          </li>
        ))}
      </ul>
    </main>
  );
}
