"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { getToken, getRole } from "@/lib/auth";
import { useRouter } from "next/navigation";

export default function PatientRecordsPage() {
  const router = useRouter();
  const token = getToken();
  const role = getRole();

  const [data, setData] = useState<any>(null);
  const [patientId, setPatientId] = useState("");

  if (!token) {
    router.push("/");
    return null;
  }

  const load = async () => {
    const res = await api(`/patients/${patientId}/records`, {}, token);
    setData(res);
  };

  return (
    <main style={{ maxWidth: 900, margin: "20px auto", padding: 16 }}>
      <h1>Patient Records</h1>

      {role === "PATIENT" && (
        <p>You may view your records. Doctors require your consent.</p>
      )}

      <input
        placeholder="Patient ID"
        value={patientId}
        onChange={(e) => setPatientId(e.target.value)}
        style={{ width: "100%" }}
      />

      <button onClick={load} style={{ marginTop: 12 }}>
        Load Records
      </button>

      {data && (
        <>
          <h3>Medical History</h3>
          <pre>{JSON.stringify(data.medical_history, null, 2)}</pre>

          <h3>Medications</h3>
          <pre>{JSON.stringify(data.medications, null, 2)}</pre>

          <h3>Test Results</h3>
          <pre>{JSON.stringify(data.test_results, null, 2)}</pre>
        </>
      )}
    </main>
  );
}
