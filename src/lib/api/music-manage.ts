import { apiFetch } from "./client";

export interface NetEaseConfig {
  api_base_url: string;
  enabled: boolean;
  timeout_seconds: number;
  retry_count: number;
}

export interface SourceRule {
  id: number;
  source_type: string;
  source_value: string;
  enabled: boolean;
  sort_order: number;
}

export interface MusicCandidateItem {
  id: number;
  netease_id: number | null;
  title: string;
  artist: string | null;
  album: string | null;
  artwork_url: string | null;
  netease_url: string | null;
  synced_at: string | null;
}

export interface DailySongItem {
  id: number;
  date: string;
  title: string;
  artist: string | null;
  album: string | null;
  artwork_url: string | null;
  preview_url: string | null;
  netease_url: string | null;
  recommendation_reason: string | null;
}

export interface SyncLogItem {
  id: number;
  action: string;
  status: string;
  candidates_found: number;
  error_message: string | null;
  created_at: string | null;
}

export async function getNetEaseConfig(): Promise<NetEaseConfig> {
  return apiFetch<NetEaseConfig>("/api/music/manage/config");
}

export async function updateNetEaseConfig(data: Partial<NetEaseConfig>): Promise<void> {
  return apiFetch("/api/music/manage/config", {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function checkNetEaseHealth(): Promise<{ status: string; data?: any }> {
  return apiFetch("/api/music/manage/health");
}

export async function getSourceRules(): Promise<SourceRule[]> {
  return apiFetch<SourceRule[]>("/api/music/manage/source-rules");
}

export async function createSourceRule(data: { source_type: string; source_value: string }): Promise<void> {
  return apiFetch("/api/music/manage/source-rules", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateSourceRule(id: number, data: Partial<SourceRule>): Promise<void> {
  return apiFetch(`/api/music/manage/source-rules/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteSourceRule(id: number): Promise<void> {
  return apiFetch(`/api/music/manage/source-rules/${id}`, { method: "DELETE" });
}

export async function syncAllCandidates(): Promise<{ total_synced: number }> {
  return apiFetch("/api/music/manage/sync", { method: "POST" });
}

export async function getCandidates(page = 1, size = 50): Promise<{ items: MusicCandidateItem[]; total: number }> {
  return apiFetch(`/api/music/manage/candidates?page=${page}&size=${size}`);
}

export async function getManageDailySong(): Promise<DailySongItem | null> {
  return apiFetch("/api/music/manage/daily-song");
}

export async function generateDailySong(): Promise<void> {
  return apiFetch("/api/music/manage/generate-song", { method: "POST" });
}

export async function getSongHistory(limit = 30): Promise<DailySongItem[]> {
  return apiFetch(`/api/music/manage/history?limit=${limit}`);
}

export async function getSyncLogs(limit = 50): Promise<SyncLogItem[]> {
  return apiFetch(`/api/music/manage/sync-logs?limit=${limit}`);
}

export async function getPublicDailySong(): Promise<DailySongItem | null> {
  return apiFetch("/api/music/manage/daily-song/public");
}

export async function getPublicSongHistory(limit = 30): Promise<DailySongItem[]> {
  return apiFetch(`/api/music/manage/history/public?limit=${limit}`);
}
