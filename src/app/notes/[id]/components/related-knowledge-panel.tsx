"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { ChevronDown, ChevronRight, ExternalLink } from "lucide-react";
import { useContextPack } from "@/hooks/use-knowledge";
import type { ContextPackRequest } from "@/lib/api/knowledge";
import type { NoteDetail } from "@/lib/api/notes";

interface Props {
  note: NoteDetail;
}

function splitKnowledgePoints(raw: string | null | undefined): string[] {
  if (!raw) return [];
  return raw
    .split(/[,，;；、\s]+/)
    .map((s) => s.trim())
    .filter(Boolean);
}

export function RelatedKnowledgePanel({ note }: Props) {
  const [sourcesOpen, setSourcesOpen] = useState(false);

  const request: ContextPackRequest | null = useMemo(() => {
    const subject = note.subject || undefined;
    const kps = splitKnowledgePoints(note.knowledge_points);
    const tags = note.tags?.map((t) => t.name) ?? [];
    const difficulty = note.difficulty || undefined;
    const hasCriteria = subject || kps.length > 0 || tags.length > 0 || difficulty;
    if (!hasCriteria) return null;
    return {
      subject,
      knowledge_points: kps,
      tags,
      difficulty,
      limit: 8,
    };
  }, [note.subject, note.knowledge_points, note.tags, note.difficulty]);

  const { data, isLoading, error } = useContextPack(request);

  if (!request) {
    return (
      <div className="rounded-xl border border-white/40 bg-white/60 p-4 text-sm text-gray-400">
        暂无检索线索
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="rounded-xl border border-white/40 bg-white/60 p-4 text-sm text-gray-400">
        加载关联资料…
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-white/40 bg-white/60 p-4 text-sm text-gray-400">
        关联资料暂时不可用
      </div>
    );
  }

  if (
    !data ||
    ((!data.related_notes || data.related_notes.length === 0) &&
      (!data.related_mistakes || data.related_mistakes.length === 0) &&
      (!data.suggested_relations || data.suggested_relations.length === 0))
  ) {
    return (
      <div className="rounded-xl border border-white/40 bg-white/60 p-4 text-sm text-gray-400">
        暂无结构化关联资料
      </div>
    );
  }

  const relatedMistakes = (data.related_mistakes || []).filter(
    (m) => m.slug !== note.slug && String(m.id) !== String(note.id)
  );

  const dedupedRelations = dedupeRelations(data.suggested_relations || []);

  return (
    <div className="mb-6 space-y-3">
      <h2 className="text-lg font-bold text-gray-800">关联知识</h2>

      {data.related_notes && data.related_notes.length > 0 && (
        <section className="rounded-xl border border-teal-200/70 bg-teal-50/50 p-4">
          <h3 className="mb-2 text-sm font-semibold text-teal-800">
            关联笔记 ({data.related_notes.length})
          </h3>
          <div className="flex flex-wrap gap-2">
            {data.related_notes.map((rn) => (
              <Link
                key={rn.id}
                href={`/notes/${rn.slug}`}
                className="inline-flex items-center gap-1 rounded-lg bg-teal-100 px-3 py-1.5 text-sm text-teal-700 transition-colors hover:bg-teal-200"
              >
                {rn.title}
                <ExternalLink size={12} />
              </Link>
            ))}
          </div>
        </section>
      )}

      {relatedMistakes.length > 0 && (
        <section className="rounded-xl border border-red-200/70 bg-red-50/50 p-4">
          <h3 className="mb-2 text-sm font-semibold text-red-800">
            相似错题 ({relatedMistakes.length})
          </h3>
          <div className="flex flex-wrap gap-2">
            {relatedMistakes.map((rm) => (
              <Link
                key={rm.id}
                href={`/notes/${rm.slug}`}
                className="inline-flex items-center gap-1 rounded-lg bg-red-100 px-3 py-1.5 text-sm text-red-700 transition-colors hover:bg-red-200"
              >
                {rm.title}
                <ExternalLink size={12} />
              </Link>
            ))}
          </div>
        </section>
      )}

      {dedupedRelations.length > 0 && (
        <section className="rounded-xl border border-purple-200/70 bg-purple-50/50 p-4">
          <h3 className="mb-2 text-sm font-semibold text-purple-800">
            关系建议 ({dedupedRelations.length})
          </h3>
          <div className="space-y-1.5">
            {dedupedRelations.map((rel, i) => (
              <div
                key={i}
                className="rounded-lg bg-purple-100/60 px-3 py-2 text-xs text-purple-800"
              >
                <span className="font-medium">{rel.relation_type}</span>{" "}
                &mdash; {rel.reason}
              </div>
            ))}
          </div>
        </section>
      )}

      {data.sources && data.sources.length > 0 && (
        <div className="rounded-xl border border-gray-200/70 bg-gray-50/50 p-4">
          <button
            onClick={() => setSourcesOpen(!sourcesOpen)}
            className="flex w-full items-center gap-1 text-sm font-semibold text-gray-700"
          >
            {sourcesOpen ? (
              <ChevronDown size={16} />
            ) : (
              <ChevronRight size={16} />
            )}
            引用来源 ({data.sources.length})
          </button>
          {sourcesOpen && (
            <div className="mt-2 space-y-1.5">
              {data.sources.map((src, i) => (
                <div
                  key={i}
                  className="rounded-lg bg-white/60 px-3 py-2 text-xs text-gray-600"
                >
                  <div className="flex items-center gap-1">
                    <span className="rounded bg-gray-200 px-1.5 py-0.5 text-[10px] font-medium uppercase text-gray-500">
                      {src.source_type}
                    </span>
                    <span className="font-medium">{src.title ?? "—"}</span>
                  </div>
                  {src.excerpt && (
                    <p className="mt-1 line-clamp-2 text-gray-500">
                      {src.excerpt}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function dedupeRelations(
  rels: {
    source_type: string;
    source_id: string;
    target_type: string;
    target_id: string;
    relation_type: string;
    score: number;
    reason: string;
  }[]
) {
  const seen = new Set<string>();
  return rels.filter((rel) => {
    const key = `${rel.source_id}:${rel.target_id}:${rel.relation_type}`;
    const reverse = `${rel.target_id}:${rel.source_id}:${rel.relation_type}`;
    if (seen.has(key) || seen.has(reverse)) return false;
    seen.add(key);
    return true;
  });
}
