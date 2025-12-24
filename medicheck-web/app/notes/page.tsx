"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { useRouter } from "next/navigation";

export default function NotesPage() {
  const router = useRouter();
  const [items, setItems] = useState<any[]>([]);
  const [text, setText] = useState("");
  const [err, setErr] = useState("");

  const token = typeof window !== "undefined" ? getToken() : null;

  const load = async () => {
    if (!token) return;
    const res = await api<{ items: any[] }>("/notes", {}, token);
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
      await api("/notes", { method: "POST", body: JSON.stringify({ text }) }, token);
      setText("");
      await load();
    } catch (e: any) {
      setErr(e.message || "Failed to create note.");
    }
  };

  return (
    <main style={{ maxWidth: 860, margin: "20px auto", padding: 16, fontFamily: "system-ui" }}>
      <h1>Notes</h1>
      <div style={{ display: "flex", gap: 8 }}>
        <input style={{ flex: 1 }} value={text} onChange={(e) => setText(e.target.value)} placeholder="Write a note..." />
        <button onClick={create} style={{ padding: "8px 12px" }}>Add</button>
      </div>
      {err ? <p style={{ color: "crimson" }}>{err}</p> : null}
      <ul style={{ marginTop: 16 }}>
        {items.map((n) => (
          <li key={n.id} style={{ padding: 10, border: "1px solid #ddd", marginBottom: 8 }}>
            <div>{n.text}</div>
            <small>{n.created_at}</small>
          </li>
        ))}
      </ul>
    </main>
  );
}
