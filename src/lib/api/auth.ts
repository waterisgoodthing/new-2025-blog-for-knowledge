import { apiFetch } from "./client";
import { getApiBase } from "./config";

const API_BASE = getApiBase();

export interface LoginResponse {
  user: SessionUser;
  message: string;
}

export interface SessionUser {
  id: string;
  username: string;
  is_admin: boolean;
  auth_level: "passkey" | "password";
}

export interface User {
  id: string;
  username: string;
  is_admin: boolean;
  auth_level: "passkey" | "password";
}

export interface SessionState {
  authenticated: boolean;
  is_admin: boolean;
}

export async function login(username: string, password: string): Promise<LoginResponse> {
  const res = await apiFetch<LoginResponse>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
  return res;
}

function base64UrlToBuffer(base64Url: string): ArrayBuffer {
  const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
  const padLen = (4 - (base64.length % 4)) % 4;
  const padded = base64 + "=".repeat(padLen);
  const binary = atob(padded);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes.buffer;
}

function bufferToBase64Url(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer);
  let binary = "";
  for (let i = 0; i < bytes.length; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

export async function getPasskeyAuthOptions(): Promise<any> {
  const res = await fetch(`${API_BASE}/api/auth/passkey/auth-options`, {
    credentials: "include",
  });
  if (!res.ok) {
    throw new Error(`Failed to get auth options: ${res.status}`);
  }
  return res.json();
}

export async function loginWithPasskey(): Promise<LoginResponse> {
  const options = await getPasskeyAuthOptions();
  const publicKey = options.publicKey;
  publicKey.challenge = base64UrlToBuffer(publicKey.challenge);

  const credential = (await navigator.credentials.get({
    publicKey,
  })) as PublicKeyCredential;

  if (!credential) {
    throw new Error("Passkey authentication cancelled");
  }

  const response = credential.response as AuthenticatorAssertionResponse;

  const assertion = {
    id: credential.id,
    rawId: bufferToBase64Url(credential.rawId),
    type: credential.type,
    response: {
      clientDataJSON: bufferToBase64Url(response.clientDataJSON),
      authenticatorData: bufferToBase64Url(response.authenticatorData),
      signature: bufferToBase64Url(response.signature),
      userHandle: response.userHandle
        ? bufferToBase64Url(response.userHandle)
        : null,
    },
  };

  const res = await fetch(`${API_BASE}/api/auth/login-passkey`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ assertion }),
  });

  if (!res.ok) {
    const data = await res.json().catch(() => null);
    const detail = data?.detail || "";
    if (res.status === 401 && detail.includes("No passkey")) {
      throw new Error("未注册 Passkey，请使用密码登录或先注册 Passkey");
    }
    if (res.status === 401 && detail.includes("verification failed")) {
      throw new Error("Passkey 验证失败，请重试");
    }
    throw new Error(detail || `Passkey 登录失败 (${res.status})`);
  }

  return res.json();
}

export async function getMe(): Promise<User> {
  return apiFetch<User>("/api/auth/me");
}

export async function getSessionState(): Promise<SessionState> {
  return apiFetch<SessionState>("/api/auth/session-state");
}

export async function logout(): Promise<void> {
  try {
    await apiFetch("/api/auth/logout", { method: "POST" });
  } catch {
    // ignore logout errors
  }
}

export function isPasskeyAvailable(): boolean {
  if (typeof window === "undefined") return false;
  return !!(
    window.PublicKeyCredential &&
    typeof navigator.credentials !== "undefined"
  );
}

export type PasskeyStatusResult =
  | { registered: true }
  | { registered: false }
  | { error: true; message: string };

export async function checkPasskeyRegistered(): Promise<PasskeyStatusResult> {
  try {
    const res = await fetch(`${API_BASE}/api/auth/passkey/status`, {
      credentials: "include",
    });
    if (!res.ok) {
      return { error: true, message: `服务器返回 ${res.status}` };
    }
    const data = await res.json();
    return { registered: !!data.registered };
  } catch (err: any) {
    return { error: true, message: err?.message || "无法连接服务器" };
  }
}
