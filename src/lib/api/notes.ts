import { apiFetch } from "./client";

export interface NoteListItem {
  id: string;
  slug: string;
  title: string;
  type: "note" | "blog" | "mistake";
  status: "draft" | "published";
  hidden: boolean;
  created_at: string;
  updated_at: string;
  tags: { id: number; name: string }[];
  summary?: string;
  cover?: string;
  category?: string;
  subject?: string;
  difficulty?: "easy" | "medium" | "hard";
  ef?: number;
  interval?: number;
  repetitions?: number;
  next_review?: string;
  last_reviewed?: string;
  images?: string[];
}

export interface NoteDetail extends NoteListItem {
  content: string;
  question?: string;
  my_answer?: string;
  correct_answer?: string;
  analysis?: string;
  knowledge_points?: string;
}

export interface NoteListResponse {
  items: NoteListItem[];
  total: number;
  page: number;
  size: number;
}

export interface NoteCreateInput {
  slug: string;
  title: string;
  content: string;
  type?: "note" | "blog" | "mistake";
  status?: "draft" | "published";
  hidden?: boolean;
  tags?: string[];
  summary?: string;
  cover?: string;
  category?: string;
  subject?: string;
  difficulty?: "easy" | "medium" | "hard";
  question?: string;
  my_answer?: string;
  correct_answer?: string;
  analysis?: string;
  knowledge_points?: string;
  images?: string[];
}

export interface NoteUpdateInput {
  title?: string;
  content?: string;
  type?: "note" | "blog" | "mistake";
  status?: "draft" | "published";
  hidden?: boolean;
  tags?: string[];
  summary?: string;
  cover?: string;
  category?: string;
  subject?: string;
  difficulty?: "easy" | "medium" | "hard";
  question?: string;
  my_answer?: string;
  correct_answer?: string;
  analysis?: string;
  knowledge_points?: string;
  images?: string[];
}

export interface NoteListParams {
  type?: "note" | "blog" | "mistake";
  tag?: string;
  subject?: string;
  category?: string;
  difficulty?: "easy" | "medium" | "hard";
  status?: "draft" | "published";
  q?: string;
  hidden?: boolean;
  page?: number;
  size?: number;
}

export async function listNotes(params: NoteListParams = {}): Promise<NoteListResponse> {
  const searchParams = new URLSearchParams();
  if (params.type) searchParams.set("type", params.type);
  if (params.tag) searchParams.set("tag", params.tag);
  if (params.subject) searchParams.set("subject", params.subject);
  if (params.category) searchParams.set("category", params.category);
  if (params.difficulty) searchParams.set("difficulty", params.difficulty);
  if (params.status) searchParams.set("status", params.status);
  if (params.q) searchParams.set("q", params.q);
  if (params.hidden !== undefined) searchParams.set("hidden", String(params.hidden));
  if (params.page) searchParams.set("page", String(params.page));
  if (params.size) searchParams.set("size", String(params.size));
  const qs = searchParams.toString();
  return apiFetch<NoteListResponse>(`/api/notes${qs ? `?${qs}` : ""}`);
}

export async function getNote(slug: string): Promise<NoteDetail> {
  return apiFetch<NoteDetail>(`/api/notes/${slug}`);
}

export async function createNote(data: NoteCreateInput): Promise<NoteDetail> {
  return apiFetch<NoteDetail>("/api/notes", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateNote(slug: string, data: NoteUpdateInput): Promise<NoteDetail> {
  return apiFetch<NoteDetail>(`/api/notes/${slug}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteNote(slug: string): Promise<void> {
  return apiFetch<void>(`/api/notes/${slug}`, { method: "DELETE" });
}

export async function batchDeleteNotes(slugs: string[]): Promise<void> {
  return apiFetch<void>("/api/notes/batch-delete", {
    method: "POST",
    body: JSON.stringify(slugs),
  });
}

export async function promoteNote(slug: string, newType: "note" | "blog" | "mistake"): Promise<NoteDetail> {
  return apiFetch<NoteDetail>(`/api/notes/${slug}/promote?new_type=${newType}`, {
    method: "POST",
  });
}

export async function uploadImage(file: File): Promise<{ url: string }> {
  const formData = new FormData();
  formData.append("file", file);
  return apiFetch<{ url: string }>("/api/notes/upload-image", {
    method: "POST",
    body: formData,
  });
}
