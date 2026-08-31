import { apiFetch } from "./client";

export type RecommendationType =
  | "note"
  | "mistake"
  | "review"
  | "resource"
  | "music"
  | "podcast";

export interface DailyRecommendation {
  date: string;
  title: string;
  type: RecommendationType;
  reason: string;
  target: string | null;
  action_label: string | null;
  source: string | null;
}

export interface RecommendationHistoryItem {
  id: number;
  date: string;
  title: string;
  type: RecommendationType;
  reason: string;
  target: string | null;
  action_label: string | null;
  source: string | null;
  created_at: string;
}

export function getTodayRecommendation(): Promise<DailyRecommendation> {
  return apiFetch<DailyRecommendation>("/api/recommendations/today");
}

export function generateTodayRecommendation(): Promise<DailyRecommendation> {
  return apiFetch<DailyRecommendation>("/api/recommendations/today/generate", {
    method: "POST",
  });
}

export function deleteTodayRecommendation(): Promise<void> {
  return apiFetch<void>("/api/recommendations/today", {
    method: "DELETE",
  });
}

export function getRecommendationHistory(limit = 30): Promise<RecommendationHistoryItem[]> {
  return apiFetch<RecommendationHistoryItem[]>(`/api/recommendations/history?limit=${limit}`);
}
