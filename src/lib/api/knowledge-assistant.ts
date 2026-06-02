import { apiFetch } from "./client";

export interface Suggestion {
  type: string;
  title: string;
  description: string;
  targets: string[];
  action: string;
  reason: string;
}

export interface SuggestionListResponse {
  suggestions: Suggestion[];
}

export interface ExecuteSuggestionRequest {
  type: string;
  action: string;
  targets?: string[];
  tag?: string;
  folder_id?: string;
}

export interface ExecuteSuggestionResponse {
  executed: number;
  failed: number;
  errors: string[];
}

export async function getSuggestions(): Promise<Suggestion[]> {
  const res = await apiFetch<SuggestionListResponse>("/api/ai/suggestions");
  return res.suggestions;
}

export async function executeSuggestion(req: ExecuteSuggestionRequest): Promise<ExecuteSuggestionResponse> {
  return apiFetch<ExecuteSuggestionResponse>("/api/ai/suggestions/execute", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

export interface WeeklySummary {
  week_start: string;
  week_end: string;
  new_notes: number;
  new_mistakes: number;
  reviewed_count: number;
  top_subjects: { subject: string; count: number }[];
  top_knowledge_points: { name: string; count: number }[];
}

export async function getWeeklySummary(): Promise<WeeklySummary> {
  return apiFetch<WeeklySummary>("/api/ai/weekly-summary");
}
