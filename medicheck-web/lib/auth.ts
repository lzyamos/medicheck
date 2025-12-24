export type Role = "PATIENT" | "DOCTOR" | "INSTITUTION";

export function setAuth(token: string, role: Role) {
  localStorage.setItem("mc_token", token);
  localStorage.setItem("mc_role", role);
}

export function getToken() {
  return localStorage.getItem("mc_token");
}

export function getRole(): Role | null {
  return (localStorage.getItem("mc_role") as Role) || null;
}

export function clearAuth() {
  localStorage.removeItem("mc_token");
  localStorage.removeItem("mc_role");
  localStorage.removeItem("mc_selected_role");
}

export function setSelectedRole(role: Role) {
  localStorage.setItem("mc_selected_role", role);
}

export function getSelectedRole(): Role | null {
  return (localStorage.getItem("mc_selected_role") as Role) || null;
}
