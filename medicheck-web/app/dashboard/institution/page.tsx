"use client";

import { useEffect } from "react";
import { getRole, getToken, clearAuth } from "@/lib/auth";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function InstitutionDashboard() {
  const router = useRouter();

  useEffect(() => {
    const token = getToken();
    const role = getRole();

    if (!token || role !== "INSTITUTION") {
      router.push("/");
      return;
    }
  }, [router]);

  const logout = () => {
    clearAuth();
    router.push("/");
  };

  return (
    <main
      style={{
        maxWidth: 960,
        margin: "20px auto",
        padding: 16,
        fontFamily: "system-ui",
      }}
    >
      <h1>Institution Dashboard</h1>

      <p>
        You are logged in as an <b>Institution</b>.  
        Phase 1 provides foundational access only.
      </p>

      <nav style={{ display: "flex", gap: 16, marginTop: 16 }}>
        <Link href="/notes">Notes</Link>
        <Link href="/reminders">Reminders</Link>
      </nav>

      <section style={{ marginTop: 24 }}>
        <h2>Phase 1 Capabilities</h2>
        <ul>
          <li>Institution-level Notes</li>
          <li>Administrative Reminders</li>
          <li>Authentication and audit logging</li>
        </ul>

        <h2 style={{ marginTop: 16 }}>Upcoming (Phase 2+)</h2>
        <ul>
          <li>Doctor affiliation management</li>
          <li>Patient enrollment (consent-gated)</li>
          <li>Audit and compliance dashboards</li>
          <li>Diagnostic workflow support</li>
        </ul>
      </section>

      <button
        onClick={logout}
        style={{
          marginTop: 32,
          padding: "8px 14px",
          cursor: "pointer",
        }}
      >
        Logout
      </button>
    </main>
  );
}
