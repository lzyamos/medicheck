"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";

type Role = "PATIENT" | "DOCTOR" | "INSTITUTION";

export default function LoginPage() {
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<Role>("PATIENT");
  const [mode, setMode] = useState<"login" | "register">("login");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setError(null);
    setLoading(true);

    try {
      const payload = {
        email,
        password,
        role: role.toLowerCase(),
      };

      const endpoint =
        mode === "login" ? "/auth/login" : "/auth/register";

      const res = await api.post(endpoint, payload);

      const { access_token, role: returnedRole } = res.data;

      localStorage.setItem("access_token", access_token);
      localStorage.setItem(
        "selected_role",
        returnedRole.toUpperCase()
      );


      router.push(`/dashboard/${returnedRole.toLowerCase()}`);
    } catch (err: any) {
      if (err?.response?.data) {
        setError(JSON.stringify(err.response.data, null, 2));
      } else {
        setError("Request failed");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <h1 className="text-3xl font-bold mb-4">Medicheck</h1>

      <p className="mb-4">
        Role: <strong>{role}</strong>
      </p>

      <div className="flex gap-2 mb-4">
        <button
          onClick={() => setMode("login")}
          className={`border px-4 py-2 ${
            mode === "login" ? "bg-gray-200" : ""
          }`}
        >
          Login
        </button>
        <button
          onClick={() => setMode("register")}
          className={`border px-4 py-2 ${
            mode === "register" ? "bg-gray-200" : ""
          }`}
        >
          Register
        </button>
      </div>

      <div className="w-full max-w-md flex flex-col gap-3">
        <input
          type="email"
          placeholder="Email"
          className="border p-2"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          type="password"
          placeholder="Password"
          className="border p-2"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <select
          className="border p-2"
          value={role}
          onChange={(e) =>
            setRole(e.target.value as Role)
          }
        >
          <option value="PATIENT">PATIENT</option>
          <option value="DOCTOR">DOCTOR</option>
          <option value="INSTITUTION">INSTITUTION</option>
        </select>

        {error && (
          <pre className="text-red-600 text-sm whitespace-pre-wrap">
            {error}
          </pre>
        )}

        <button
          onClick={handleSubmit}
          disabled={loading}
          className="border p-2 bg-gray-100"
        >
          {loading
            ? "Please wait..."
            : mode === "login"
            ? "Login"
            : "Create account"}
        </button>
      </div>
    </main>
  );
}
