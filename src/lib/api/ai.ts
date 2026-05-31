import { apiFetch } from "./client";

export interface AnalyzeResponse {
  title: string;
  question: string;
  correct_answer: string;
  analysis: string;
  knowledge_points: string;
  subject: string;
  difficulty: string;
  tags: string[];
}

export async function analyzeMistake(images: { base64: string; mime_type: string }[]): Promise<AnalyzeResponse> {
  return apiFetch<AnalyzeResponse>("/api/ai/analyze", {
    method: "POST",
    body: JSON.stringify({ images }),
  });
}

export async function analyzeText(text: string): Promise<AnalyzeResponse> {
  return apiFetch<AnalyzeResponse>("/api/ai/analyze-text", {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}
