"use client";

import { useEffect } from "react";
import { getRole, getToken, clearAuth } from "@/lib/auth";
import { useRouter } from "next/navigation";

export default function Dashboard() {
  const router = useRouter();

  useEffect(() => {
    const token = getToken();
    const role = getRole();
    if (!token || !role) {
      router.push("/");
      return;
    }
    if (role === "PATIENT") router.push("/dashboard/patient");
    if (role === "DOCTOR") router.push("/dashboard/doctor");
    if (role === "INSTITUTION") router.push("/dashboard/institution");
  }, [router]);

  return (
    <main style={{ padding: 16 }}>
      <p>Routing to your dashboard...</p>
      <button onClick={() => { clearAuth(); router.push("/"); }}>Logout</button>
    </main>
  );
}
