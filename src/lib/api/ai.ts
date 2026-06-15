import { apiFetch } from "./client";
import { getApiBase } from "./config";

const API_BASE = getApiBase()

export interface DiagramItem {
  type: "flowchart" | "timeline" | "formula_breakdown" | "network_topology" | "geometry" | "state_machine";
  title: string;
  mermaid: string;
}

export interface AnalyzeResponse {
  title: string;
  question: string;
  correct_answer: string;
  analysis: string;
  knowledge_points: string;
  subject: string;
  difficulty: string;
  tags: string[];
  error_reason?: string;
  key_step?: string;
  similar_traps?: string[];
  generalization?: string;
  review_advice?: string;
  variant_questions?: string[];
  related_notes?: { slug: string; title: string }[];
  diagrams?: DiagramItem[];
  personalized_diagnosis?: string;
  misread_signal?: string;
  next_time_checklist?: string[];
  latex_warnings?: string[];
  visual_context?: string;
  image_dependency?: string;
}

export type StreamEvent =
  | { type: 'received'; label: string }
  | { type: 'progress'; step: string; label: string }
  | { type: 'done'; label: string }
  | { type: 'result'; data: AnalyzeResponse }
  | { type: 'error'; message: string }

export async function analyzeMistake(images: { base64: string; mime_type: string }[], options?: AnalyzeTextOptions): Promise<AnalyzeResponse> {
  return apiFetch<AnalyzeResponse>("/api/ai/analyze", {
    method: "POST",
    body: JSON.stringify({ images, ...options }),
  });
}

export interface AnalyzeTextOptions {
  question?: string;
  my_answer?: string;
  correct_answer?: string;
  user_error_analysis?: string;
  analysis_mode?: string;
}

export async function analyzeText(text: string, options?: AnalyzeTextOptions): Promise<AnalyzeResponse> {
  return apiFetch<AnalyzeResponse>("/api/ai/analyze-text", {
    method: "POST",
    body: JSON.stringify({ text, ...options }),
  });
}

export interface VariantResponse {
  question: string;
  correct_answer: string;
  analysis: string;
  difficulty: string;
  knowledge_points: string;
  subject: string;
}

export interface KnowledgeCardResponse {
  title: string;
  content: string;
  knowledge_points: string;
  subject: string;
}

export async function generateVariant(knowledge_point: string, subject?: string): Promise<VariantResponse> {
  return apiFetch<VariantResponse>("/api/ai/generate-variant", {
    method: "POST",
    body: JSON.stringify({ knowledge_point, subject }),
  });
}

export async function generateKnowledgeCard(knowledge_point: string, subject?: string): Promise<KnowledgeCardResponse> {
  return apiFetch<KnowledgeCardResponse>("/api/ai/generate-knowledge-card", {
    method: "POST",
    body: JSON.stringify({ knowledge_point, subject }),
  });
}

export async function analyzeMistakeStream(
  images: { base64: string; mime_type: string }[],
  onEvent: (event: StreamEvent) => void,
  signal?: AbortSignal,
  options?: AnalyzeTextOptions
): Promise<void> {
  let response: Response
  try {
    response = await fetch(`${API_BASE}/api/ai/analyze-stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ images, ...options }),
      signal,
    })
  } catch (err: any) {
    if (err.name === 'AbortError') return
    onEvent({ type: 'error', message: '网络错误' })
    return
  }

  if (!response.ok) {
    onEvent({ type: 'error', message: `服务错误 (${response.status})` })
    return
  }

  const reader = response.body?.getReader()
  if (!reader) { onEvent({ type: 'error', message: '无法读取响应' }); return }

  const decoder = new TextDecoder()
  let buffer = ''

  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const events = buffer.split('\n\n')
      buffer = events.pop() || ''

      for (const event of events) {
        const lines = event.split('\n')
        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          const data = line.slice(6).trim()
          try {
            const parsed = JSON.parse(data)
            if (parsed.type === 'error') {
              onEvent({ type: 'error', message: parsed.message || '未知错误' })
              return
            }
            if (parsed.type === 'done') {
              onEvent({ type: 'done', label: parsed.label || '完成' })
              return
            }
            if (parsed.type === 'result') {
              onEvent({ type: 'result', data: parsed.data })
            } else {
              onEvent(parsed as StreamEvent)
            }
          } catch {
            continue
          }
        }
      }
    }
  } catch (err: any) {
    if (err.name === 'AbortError') return
    onEvent({ type: 'error', message: '读取响应失败' })
  }
}

export async function analyzeTextStream(
  text: string,
  onEvent: (event: StreamEvent) => void,
  signal?: AbortSignal,
  options?: AnalyzeTextOptions
): Promise<void> {
  let response: Response
  try {
    response = await fetch(`${API_BASE}/api/ai/analyze-text-stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ text, ...options }),
      signal,
    })
  } catch (err: any) {
    if (err.name === 'AbortError') return
    onEvent({ type: 'error', message: '网络错误' })
    return
  }

  if (!response.ok) {
    onEvent({ type: 'error', message: `服务错误 (${response.status})` })
    return
  }

  const reader = response.body?.getReader()
  if (!reader) { onEvent({ type: 'error', message: '无法读取响应' }); return }

  const decoder = new TextDecoder()
  let buffer = ''

  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const events = buffer.split('\n\n')
      buffer = events.pop() || ''

      for (const event of events) {
        const lines = event.split('\n')
        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          const data = line.slice(6).trim()
          try {
            const parsed = JSON.parse(data)
            if (parsed.type === 'error') {
              onEvent({ type: 'error', message: parsed.message || '未知错误' })
              return
            }
            if (parsed.type === 'done') {
              onEvent({ type: 'done', label: parsed.label || '完成' })
              return
            }
            if (parsed.type === 'result') {
              onEvent({ type: 'result', data: parsed.data })
            } else {
              onEvent(parsed as StreamEvent)
            }
          } catch {
            continue
          }
        }
      }
    }
  } catch (err: any) {
    if (err.name === 'AbortError') return
    onEvent({ type: 'error', message: '读取响应失败' })
  }
}


// --- Staged mistake workflow types and functions ---

export interface ImageInput {
  base64: string;
  mime_type: string;
}

export interface QuestionDraftResponse {
  title: string;
  question: string;
  options: string[];
  visual_context: string;
  key_conditions: string[];
  candidate_answer: string;
  knowledge_points: string;
  question_type: string;
  subject: string;
  difficulty: string;
  tags: string[];
  image_dependency: string;
}

export interface QuestionDraftConfirmResponse {
  status: "confirmed";
  draft: QuestionDraftResponse;
  confirmed_at: string;
}

export interface ErrorInterpretationResponse {
  interpretation_id: string;
  version: number;
  summary: string;
  diagnosis: string;
  root_cause: string;
  knowledge_gap: string;
  suggested_correction: string;
  reasoning_trace: string;
}

export interface FinalAnalysisResponse {
  analysis: string;
  error_reason: string;
  key_step: string;
  similar_traps: string[];
  generalization: string;
  review_advice: string;
  variant_questions: string[];
  accepted_interpretation_id: string;
  accepted_interpretation_version: number;
}

export interface StructuredDiagramNode {
  id: string;
  label: string;
  x: number;
  y: number;
  highlighted: boolean;
  annotation: string;
}

export interface StructuredDiagramEdge {
  source: string;
  target: string;
  label: string;
  highlighted: boolean;
  weight: string;
}

export interface StructuredDiagramTableRow {
  cells: string[];
}

export interface StructuredDiagramTable {
  headers: string[];
  rows: StructuredDiagramTableRow[];
  caption: string;
}

export interface StructuredDiagramData {
  diagram_type: "graph" | "table" | "flowchart" | "packet_slices";
  title: string;
  nodes: StructuredDiagramNode[];
  edges: StructuredDiagramEdge[];
  table: StructuredDiagramTable | null;
  mermaid: string;
  caption: string;
  error_reason_annotation: string;
}

export interface DiagramResponse {
  strategy: "structured" | "qwen_image_fallback";
  strategy_reason: string;
  structured_data: StructuredDiagramData | null;
  image_url: string;
  image_prompt: string;
  accepted_interpretation_id: string;
  accepted_interpretation_version: number;
  uses_error_interpretation: boolean;
}

export async function generateQuestionDraft(
  images: ImageInput[],
  text: string
): Promise<QuestionDraftResponse> {
  return apiFetch<QuestionDraftResponse>("/api/ai/mistake/question-draft", {
    method: "POST",
    body: JSON.stringify({ images, text }),
  });
}

export async function confirmQuestionDraft(
  draft: QuestionDraftResponse
): Promise<QuestionDraftConfirmResponse> {
  return apiFetch<QuestionDraftConfirmResponse>("/api/ai/mistake/question-draft/confirm", {
    method: "POST",
    body: JSON.stringify({ draft }),
  });
}

export async function generateErrorInterpretation(
  questionDraft: QuestionDraftResponse,
  userErrorReason: string,
  rejectionHistory: string[] = []
): Promise<ErrorInterpretationResponse> {
  return apiFetch<ErrorInterpretationResponse>("/api/ai/mistake/error-interpretation", {
    method: "POST",
    body: JSON.stringify({
      question_draft: questionDraft,
      user_error_reason: userErrorReason,
      rejection_history: rejectionHistory,
    }),
  });
}

export async function rejectErrorInterpretation(
  questionDraft: QuestionDraftResponse,
  userErrorReason: string,
  currentInterpretation: ErrorInterpretationResponse,
  rejectionReason: string,
  rejectionHistory: string[] = []
): Promise<ErrorInterpretationResponse> {
  return apiFetch<ErrorInterpretationResponse>("/api/ai/mistake/error-interpretation/reject", {
    method: "POST",
    body: JSON.stringify({
      question_draft: questionDraft,
      user_error_reason: userErrorReason,
      current_interpretation: currentInterpretation,
      rejection_reason: rejectionReason,
      rejection_history: rejectionHistory,
    }),
  });
}

export async function generateFinalAnalysis(
  questionDraft: QuestionDraftResponse,
  userErrorReason: string,
  acceptedInterpretation: ErrorInterpretationResponse
): Promise<FinalAnalysisResponse> {
  return apiFetch<FinalAnalysisResponse>("/api/ai/mistake/final-analysis", {
    method: "POST",
    body: JSON.stringify({
      question_draft: questionDraft,
      user_error_reason: userErrorReason,
      accepted_interpretation: acceptedInterpretation,
    }),
  });
}

export async function generateDiagram(
  questionDraft: QuestionDraftResponse,
  acceptedInterpretation: ErrorInterpretationResponse,
  finalAnalysis: FinalAnalysisResponse
): Promise<DiagramResponse> {
  return apiFetch<DiagramResponse>("/api/ai/mistake/diagram", {
    method: "POST",
    body: JSON.stringify({
      question_draft: questionDraft,
      accepted_interpretation: acceptedInterpretation,
      final_analysis: finalAnalysis,
    }),
  });
}
