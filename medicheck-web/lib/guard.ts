import { getRole, getSelectedRole, getToken } from "./auth";

export function isAuthed() {
  return Boolean(getToken() && getRole());
}

export function hasSelectedRole() {
  return Boolean(getSelectedRole());
}
