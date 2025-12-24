"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

const roles = ["PATIENT", "DOCTOR", "INSTITUTION"] as const;
type Role = (typeof roles)[number];

export default function Home() {
  const router = useRouter();

  const pick = (role: Role) => {
    localStorage.setItem("selected_role", role);
    router.push("/login");
  };

  return (
    <main style={{ padding: 32 }}>
      <h1 style={{ fontSize: 28, fontWeight: "bold" }}>
        Medicheck
      </h1>

      <p style={{ marginTop: 8 }}>
        Select your role to continue
      </p>

      <div style={{ display: "flex", gap: 12, marginTop: 16 }}>
        {roles.map((r) => (
          <button
            key={r}
            onClick={() => pick(r)}
            style={{
              padding: "10px 14px",
              cursor: "pointer",
              border: "1px solid #ccc",
              borderRadius: 6,
            }}
          >
            {r}
          </button>
        ))}
      </div>
    </main>
  );
}
