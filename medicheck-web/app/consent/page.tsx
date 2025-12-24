"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { getRole, getToken } from "@/lib/auth";
import { useRouter } from "next/navigation";

export default function ConsentPage() {
  const router = useRouter();
  const [items, setItems] = useState<any[]>([]);
  const [granteeType, setGranteeType] = useState<"DOCTOR" | "INSTITUTION">("DOCTOR");
  const [granteeId, setGranteeId] = useState("");
  const [err, setErr] = useState("");

  const token = typeof window !== "undefined" ? getToken() : null;

  const load = async () => {
    if (!token) return;
    const res = await api<{ items: any[] }>("/consents", {}, token);
    setItems(res.items);
  };

  useEffect(() => {
    if (!token || getRole() !== "PATIENT") { router.push("/"); return; }
    load();
  }, []);

  const grant = async () => {
    setErr("");
    try {
      if (!token) return;
      await api("/consents/grant", {
        method: "POST",
        body: JSON.stringify({ grantee_type: granteeType, grantee_id: granteeId, scope_json: {} })
      }, token);
      setGranteeId("");
      await load();
    } catch (e: any) {
      setErr(e.message || "Failed to grant consent.");
    }
  };

  const revoke = async (consentId: string) => {
    setErr("");
    try {
      if (!token) return;
      await api("/consents/revoke", {
        method: "POST",
        body: JSON.stringify({ consent_id: consentId })
      }, token);
      await load();
    } catch (e: any) {
      setErr(e.message || "Failed to revoke consent.");
    }
  };

  return (
    <main style={{ maxWidth: 860, margin: "20px auto", padding: 16, fontFamily: "system-ui" }}>
      <h1>Sharing / Consent (Patient)</h1>

      <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
        <select value={granteeType} onChange={(e) => setGranteeType(e.target.value as any)}>
          <option value="DOCTOR">Doctor</option>
          <option value="INSTITUTION">Institution</option>
        </select>
        <input value={granteeId} onChange={(e) => setGranteeId(e.target.value)} placeholder="Grantee ID (UUID)" style={{ flex: 1 }} />
        <button onClick={grant} style={{ padding: "8px 12px" }}>Grant</button>
      </div>

      {err ? <p style={{ color: "crimson" }}>{err}</p> : null}

      <h2 style={{ marginTop: 16 }}>Your consents</h2>
      <ul>
        {items.map((c) => (
          <li key={c.id} style={{ padding: 10, border: "1px solid #ddd", marginBottom: 8 }}>
            <div>
              <b>{c.grantee_type}</b> — {c.grantee_id} — <b>{c.status}</b>
            </div>
            {c.status === "GRANTED" ? (
              <button onClick={() => revoke(c.id)} style={{ marginTop: 6 }}>Revoke</button>
            ) : null}
          </li>
        ))}
      </ul>
    </main>
  );
}
