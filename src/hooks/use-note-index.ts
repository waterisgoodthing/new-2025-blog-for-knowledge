import useSWR from "swr";
import { listNotes, type NoteListParams, type NoteListResponse } from "@/lib/api/notes";
import { getReviewPlan, getReviewStats, type ReviewPlan, type ReviewStats } from "@/lib/api/review";

export function useNoteIndex(params: NoteListParams = {}) {
  const key = `/api/notes?${new URLSearchParams(
    Object.entries(params)
      .filter(([_, v]) => v !== undefined && v !== null)
      .map(([k, v]) => [k, String(v)])
  ).toString()}`;

  return useSWR<NoteListResponse>(key, () => listNotes(params), {
    revalidateOnFocus: false,
  });
}

export function useReviewStats(enabled = true) {
  return useSWR<ReviewStats>(enabled ? "/api/review/stats" : null, getReviewStats, {
    revalidateOnFocus: false,
  });
}

export function useReviewPlan(enabled = true) {
  return useSWR<ReviewPlan>(enabled ? "/api/review/plan" : null, getReviewPlan, {
    revalidateOnFocus: false,
  });
}
