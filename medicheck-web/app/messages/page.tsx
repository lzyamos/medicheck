"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { getToken, getRole } from "@/lib/auth";
import { useRouter } from "next/navigation";

export default function MessagesPage() {
  const router = useRouter();
  const token = getToken();
  const role = getRole();

  const [patientId, setPatientId] = useState("");
  const [receiverId, setReceiverId] = useState("");
  const [text, setText] = useState("");
  const [thread, setThread] = useState<any[]>([]);

  if (!token || (role !== "PATIENT" && role !== "DOCTOR")) {
    router.push("/");
    return null;
  }

  const send = async () => {
    await api(
      "/messages",
      {
        method: "POST",
        body: JSON.stringify({
          patient_id: patientId,
          receiver_user_id: receiverId,
          message_text: text,
        }),
      },
      token
    );
    setText("");
    load();
  };

  const load = async () => {
    const res = await api(`/messages/patient/${patientId}`, {}, token);
    setThread(res.messages);
  };

  return (
    <main style={{ maxWidth: 900, margin: "20px auto", padding: 16 }}>
      <h1>Secure Messaging</h1>

      <input placeholder="Patient ID" value={patientId} onChange={(e) => setPatientId(e.target.value)} />
      <input placeholder="Receiver User ID" value={receiverId} onChange={(e) => setReceiverId(e.target.value)} />

      <textarea
        placeholder="Write a message (non-diagnostic)"
        value={text}
        onChange={(e) => setText(e.target.value)}
        style={{ width: "100%", height: 100 }}
      />

      <button onClick={send}>Send</button>
      <button onClick={load} style={{ marginLeft: 8 }}>Load Conversation</button>

      <ul style={{ marginTop: 20 }}>
        {thread.map((m) => (
          <li key={m.id} style={{ borderBottom: "1px solid #ddd", padding: 8 }}>
            <b>{m.sender_role}</b>: {m.message_text}
            <br />
            <small>{m.created_at}</small>
          </li>
        ))}
      </ul>
    </main>
  );
}
