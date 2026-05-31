import { apiFetch } from "./client";
import type { NoteDetail } from "./notes";

export interface ReviewStats {
  total_mistakes: number;
  mastered: number;
  pending_review: number;
  due_today: number;
}

export async function getReviewQueue(): Promise<NoteDetail[]> {
  return apiFetch<NoteDetail[]>("/api/review/queue");
}

export async function submitReview(slug: string, quality: number): Promise<NoteDetail> {
  return apiFetch<NoteDetail>(`/api/review/${slug}`, {
    method: "POST",
    body: JSON.stringify({ quality }),
  });
}

export async function getReviewStats(): Promise<ReviewStats> {
  return apiFetch<ReviewStats>("/api/review/stats");
}
