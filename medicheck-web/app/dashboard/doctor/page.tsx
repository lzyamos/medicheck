"use client";

import { useEffect } from "react";
import { getRole, getToken, clearAuth } from "@/lib/auth";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function DoctorDashboard() {
  const router = useRouter();

  useEffect(() => {
    const token = getToken();
    const role = getRole();

    if (!token || role !== "DOCTOR") {
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
      <h1>Doctor Dashboard</h1>

      <p>
        You are logged in as a <b>Doctor</b>.  
        Phase 1 access is limited to personal Notes and Reminders.
      </p>

      <nav style={{ display: "flex", gap: 16, marginTop: 16 }}>
        <Link href="/notes">Notes</Link>
        <Link href="/symptoms">Symptom Checker</Link>
        <Link href="/reminders">Reminders</Link>
        <Link href="/patient-records">Patient Records</Link>
        <Link href="/doctor-notes">Doctor Notes</Link>
        <Link href="/messages">Messages</Link>
      </nav>

      <section style={{ marginTop: 24 }}>
        <h2>Phase 1 Limitations</h2>
        <ul>
          <li>No patient records visible yet</li>
          <li>No symptom entry</li>
          <li>No consent-based access workflows</li>
          <li>No clinical insights or test recommendations</li>
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
