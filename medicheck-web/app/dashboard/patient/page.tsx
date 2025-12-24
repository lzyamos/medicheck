"use client";
import Link from "next/link";
import { useEffect } from "react";
import { getRole, getToken } from "@/lib/auth";
import { useRouter } from "next/navigation";

export default function PatientDashboard() {
  const router = useRouter();
  useEffect(() => {
    if (!getToken() || getRole() !== "PATIENT") router.push("/");
  }, [router]);

  return (
    <main style={{ maxWidth: 860, margin: "20px auto", padding: 16, fontFamily: "system-ui" }}>
      <h1>Patient Dashboard</h1>
      <p>Phase 1: Notes, Reminders, Consent.</p>
      <nav style={{ display: "flex", gap: 12 }}>
        <Link href="/notes">Notes</Link>
        <Link href="/reminders">Reminders</Link>
        <Link href="/symptoms">Symptom Checker</Link>
        <Link href="/patient-records">My Records</Link>
        <Link href="/consent">Sharing / Consent</Link>
        <Link href="/messages">Messages</Link>
      </nav>
    </main>
  );
}
