import { apiFetch } from "./client";
import type { NoteDetail } from "./notes";

export interface ReviewStats {
  total_mistakes: number;
  mastered: number;
  pending_review: number;
  due_today: number;
}

export interface ReviewSubjectSummary {
  subject: string;
  total: number;
  due_today: number;
  hard: number;
  average_ef: number;
}

export interface ReviewWeaknessItem {
  name: string;
  count: number;
  due_today: number;
  subjects: string[];
}

export interface ReviewPlan {
  today_count: number;
  overdue_count: number;
  week_count: number;
  next_review_date?: string | null;
  subject_summaries: ReviewSubjectSummary[];
  weaknesses: ReviewWeaknessItem[];
  recommendations: string[];
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

export async function getReviewPlan(): Promise<ReviewPlan> {
  return apiFetch<ReviewPlan>("/api/review/plan");
}
