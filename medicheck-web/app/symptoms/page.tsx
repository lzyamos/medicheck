"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { getToken, getRole } from "@/lib/auth";
import { useRouter } from "next/navigation";

export default function SymptomsPage() {
  const router = useRouter();
  const token = getToken();
  const role = getRole();

  if (!token || (role !== "PATIENT" && role !== "DOCTOR")) {
    router.push("/");
    return null;
  }

  const [symptom, setSymptom] = useState("");
  const [severity, setSeverity] = useState(5);
  const [days, setDays] = useState(1);
  const [result, setResult] = useState<any>(null);

  const submit = async () => {
    const res = await api<any>(
      "/symptoms",
      {
        method: "POST",
        body: JSON.stringify({
          symptoms: [{ symptom, severity, duration_days: days }],
        }),
      },
      token!
    );
    setResult(res);
  };

  return (
    <main style={{ maxWidth: 720, margin: "20px auto", padding: 16 }}>
      <h1>Symptom Checker</h1>

      <input placeholder="Symptom" value={symptom} onChange={(e) => setSymptom(e.target.value)} />
      <input type="number" min={1} max={10} value={severity} onChange={(e) => setSeverity(+e.target.value)} />
      <input type="number" min={0} value={days} onChange={(e) => setDays(+e.target.value)} />

      <button onClick={submit} style={{ marginTop: 12 }}>Analyze</button>

      {result && (
        <section style={{ marginTop: 20 }}>
          <h2>Urgency: {result.urgency}</h2>

          <h3>Possible Condition Insights</h3>
          <pre>{JSON.stringify(result.insights, null, 2)}</pre>

          <h3>Recommended Tests</h3>
          <pre>{JSON.stringify(result.recommended_tests, null, 2)}</pre>

          <p style={{ marginTop: 12, fontStyle: "italic" }}>
            {result.safety_statement}
          </p>
        </section>
      )}
    </main>
  );
}
