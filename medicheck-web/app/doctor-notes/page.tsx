"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { getToken, getRole } from "@/lib/auth";
import { useRouter } from "next/navigation";

export default function DoctorNotesPage() {
  const router = useRouter();
  const token = getToken();
  const role = getRole();

  const [patientId, setPatientId] = useState("");
  const [note, setNote] = useState("");

  if (!token || role !== "DOCTOR") {
    router.push("/");
    return null;
  }

  const submit = async () => {
    await api(
      "/doctor-notes",
      {
        method: "POST",
        body: JSON.stringify({ patient_id: patientId, note_text: note }),
      },
      token
    );
    setNote("");
  };

  return (
    <main style={{ maxWidth: 720, margin: "20px auto", padding: 16 }}>
      <h1>Doctor Notes</h1>

      <input
        placeholder="Patient ID"
        value={patientId}
        onChange={(e) => setPatientId(e.target.value)}
      />

      <textarea
        placeholder="Clinical note (non-diagnostic)"
        value={note}
        onChange={(e) => setNote(e.target.value)}
        style={{ width: "100%", height: 120 }}
      />

      <button onClick={submit} style={{ marginTop: 12 }}>
        Save Note
      </button>
    </main>
  );
}
