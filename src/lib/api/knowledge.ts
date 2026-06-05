import { apiFetch } from "./client";

export type SourceType = "note" | "mistake";

export type RelationType =
  | "explains"
  | "similar"
  | "prerequisite"
  | "follow_up"
  | "source_for";

export type RelationStatus = "suggested";

export type ReviewStateFilter = "due" | "overdue" | "upcoming" | "all";

export type CitationBlockType =
  | "source_backed_claim"
  | "ai_inference"
  | "insufficient_context";

export interface SourceRef {
  source_type: SourceType;
  source_id: string;
  title?: string;
  slug?: string;
  field?: string;
  excerpt?: string;
  url?: string;
  confidence?: number;
  match_reasons?: string[];
}

export interface RelationSuggestion {
  source_type: SourceType;
  source_id: string;
  target_type: SourceType;
  target_id: string;
  relation_type: RelationType;
  score: number;
  reason: string;
  status: RelationStatus;
}

export interface NoteBrief {
  id: string;
  slug: string;
  title: string;
  type: string;
  subject?: string | null;
  knowledge_points?: string | null;
  difficulty?: string | null;
  summary?: string | null;
  updated_at?: string | null;
}

export interface ContextPackStats {
  mistake_count: number;
  note_count: number;
  top_error_reasons: string[];
}

export interface ContextPackRequest {
  subject?: string;
  knowledge_points?: string[];
  tags?: string[];
  type?: string;
  difficulty?: string;
  date_range?: { from?: string; to?: string };
  review_state?: ReviewStateFilter;
  limit?: number;
}

export interface ContextPackResponse {
  sources: SourceRef[];
  related_notes: NoteBrief[];
  related_mistakes: NoteBrief[];
  suggested_relations: RelationSuggestion[];
  stats: ContextPackStats;
}

export interface WeakPointItem {
  subject: string;
  knowledge_point: string;
  mistake_count: number;
  due_review_count: number;
  recent_error_count: number;
  top_error_reasons: string[];
  evidence_sources: SourceRef[];
}

export interface WeakPointsResponse {
  days: number;
  weak_points: WeakPointItem[];
}

export interface CitationBlock {
  type: CitationBlockType;
  text: string;
  source_refs: SourceRef[];
}

export interface KnowledgeSummaryRequest {
  mode?: string;
  context_pack: ContextPackResponse;
  requirements?: {
    language?: string;
    style?: string;
    max_length?: number;
    require_citations?: boolean;
  };
}

export interface KnowledgeSummaryResponse {
  title: string;
  blocks: CitationBlock[];
}

export interface InsufficientContextResponse {
  status: "insufficient_context";
  message: string;
  outline: string[];
}

export async function getContextPack(
  request: ContextPackRequest
): Promise<ContextPackResponse> {
  return apiFetch<ContextPackResponse>("/api/knowledge/context-pack", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export async function getWeakPoints(
  days: number = 30
): Promise<WeakPointsResponse> {
  return apiFetch<WeakPointsResponse>(
    `/api/knowledge/weak-points?days=${days}`
  );
}

export async function getKnowledgeSummary(
  request: KnowledgeSummaryRequest
): Promise<KnowledgeSummaryResponse | InsufficientContextResponse> {
  return apiFetch<KnowledgeSummaryResponse | InsufficientContextResponse>(
    "/api/ai/knowledge-summary",
    {
      method: "POST",
      body: JSON.stringify(request),
    }
  );
}
