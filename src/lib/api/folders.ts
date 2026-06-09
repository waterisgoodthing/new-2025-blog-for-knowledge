import { apiFetch } from "./client";

export interface FolderNode {
  id: string;
  name: string;
  parent_id: string | null;
  sort_order: number;
  created_at: string;
  updated_at: string;
  children: FolderNode[];
  note_count: number;
}

export interface FolderCreateInput {
  name: string;
  parent_id?: string | null;
}

export interface FolderUpdateInput {
  name?: string;
  parent_id?: string | null;
  sort_order?: number;
}

export async function listFolders(): Promise<FolderNode[]> {
  return apiFetch<FolderNode[]>("/api/folders");
}

export async function createFolder(data: FolderCreateInput): Promise<FolderNode> {
  return apiFetch<FolderNode>("/api/folders", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateFolder(id: string, data: FolderUpdateInput): Promise<FolderNode> {
  return apiFetch<FolderNode>(`/api/folders/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteFolder(id: string): Promise<void> {
  return apiFetch<void>(`/api/folders/${id}`, { method: "DELETE" });
}

export async function reorderFolders(items: { id: string; sort_order: number }[]): Promise<void> {
  return apiFetch<void>("/api/folders/reorder", {
    method: "POST",
    body: JSON.stringify({ items }),
  });
}

export async function moveNoteToFolder(slug: string, folderId: string | null): Promise<void> {
  return apiFetch<void>(`/api/folders/move-note/${slug}`, {
    method: "POST",
    body: JSON.stringify({ folder_id: folderId }),
  });
}

export async function moveFolder(folderId: string, newParentId: string | null): Promise<FolderNode> {
  return updateFolder(folderId, { parent_id: newParentId });
}

export async function renameFolder(folderId: string, name: string): Promise<FolderNode> {
  return updateFolder(folderId, { name });
}
