import { apiFetch } from "./client";

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: string;
  username: string;
}

export async function login(username: string, password: string): Promise<LoginResponse> {
  const res = await apiFetch<LoginResponse>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
  if (typeof window !== "undefined") {
    localStorage.setItem("token", res.access_token);
  }
  return res;
}

export async function getMe(): Promise<User> {
  return apiFetch<User>("/api/auth/me");
}

export function logout() {
  if (typeof window !== "undefined") {
    localStorage.removeItem("token");
  }
}

export function isLoggedIn(): boolean {
  if (typeof window === "undefined") return false;
  return !!localStorage.getItem("token");
}
