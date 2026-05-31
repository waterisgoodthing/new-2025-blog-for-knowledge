import { apiFetch } from "./client";

export interface MusicItem {
  id: number;
  title: string;
  artist: string | null;
  artwork: string | null;
  apple_music_url: string;
  preview_url: string | null;
  track_id: number | null;
  sort_order: number;
  is_active: boolean;
  created_at: string;
}

export interface MusicItemCreate {
  title: string;
  artist?: string;
  artwork?: string;
  apple_music_url: string;
  preview_url?: string;
  track_id?: number;
  sort_order?: number;
  is_active?: boolean;
}

export interface MusicItemUpdate {
  title?: string;
  artist?: string;
  artwork?: string;
  apple_music_url?: string;
  preview_url?: string;
  track_id?: number;
  sort_order?: number;
  is_active?: boolean;
}

export function getPlaylist(): Promise<MusicItem[]> {
  return apiFetch<MusicItem[]>("/api/music/playlist");
}

export function createMusicItem(data: MusicItemCreate): Promise<MusicItem> {
  return apiFetch<MusicItem>("/api/music/items", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function updateMusicItem(id: number, data: MusicItemUpdate): Promise<MusicItem> {
  return apiFetch<MusicItem>(`/api/music/items/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export function deleteMusicItem(id: number): Promise<void> {
  return apiFetch<void>(`/api/music/items/${id}`, {
    method: "DELETE",
  });
}
