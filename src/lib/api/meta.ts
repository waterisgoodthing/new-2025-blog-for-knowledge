import { apiFetch } from "./client";

export interface Tag {
  id: number;
  name: string;
}

export interface Subject {
  id: number;
  name: string;
}

export interface Category {
  id: number;
  name: string;
  sort_order: number;
}

export async function listTags(): Promise<Tag[]> {
  return apiFetch<Tag[]>("/api/tags");
}

export async function createTag(name: string): Promise<Tag> {
  return apiFetch<Tag>("/api/tags", {
    method: "POST",
    body: JSON.stringify({ name }),
  });
}

export async function deleteTag(id: number): Promise<void> {
  return apiFetch<void>(`/api/tags/${id}`, { method: "DELETE" });
}

export async function renameTag(id: number, name: string): Promise<Tag> {
  return apiFetch<Tag>(`/api/tags/${id}`, {
    method: "PUT",
    body: JSON.stringify({ name }),
  });
}

export async function mergeTag(sourceId: number, targetId: number): Promise<Tag> {
  return apiFetch<Tag>(`/api/tags/${sourceId}/merge`, {
    method: "POST",
    body: JSON.stringify({ target_tag_id: targetId }),
  });
}

export async function listSubjects(): Promise<Subject[]> {
  return apiFetch<Subject[]>("/api/subjects");
}

export async function createSubject(name: string): Promise<Subject> {
  return apiFetch<Subject>("/api/subjects", {
    method: "POST",
    body: JSON.stringify({ name }),
  });
}

export async function deleteSubject(id: number): Promise<void> {
  return apiFetch<void>(`/api/subjects/${id}`, { method: "DELETE" });
}

export async function listCategories(): Promise<Category[]> {
  return apiFetch<Category[]>("/api/categories");
}

export async function createCategory(name: string): Promise<Category> {
  return apiFetch<Category>("/api/categories", {
    method: "POST",
    body: JSON.stringify({ name }),
  });
}

export async function updateCategory(id: number, data: { name?: string; sort_order?: number }): Promise<Category> {
  return apiFetch<Category>(`/api/categories/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteCategory(id: number): Promise<void> {
  return apiFetch<void>(`/api/categories/${id}`, { method: "DELETE" });
}
