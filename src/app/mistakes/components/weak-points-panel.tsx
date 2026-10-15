"use client";

import Link from "next/link";
import { useWeakPoints } from "@/hooks/use-knowledge";

export function WeakPointsPanel({ enabled = true }: { enabled?: boolean }) {
  const { data, isLoading, error } = useWeakPoints(30, enabled);

  if (isLoading) {
    return (
      <div className="rounded-xl border border-white/40 bg-white/60 p-4 text-sm text-gray-400">
        加载薄弱点数据…
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-white/40 bg-white/60 p-4 text-sm text-gray-400">
        薄弱点数据暂时不可用
      </div>
    );
  }

  if (!data || !data.weak_points || data.weak_points.length === 0) {
    return (
      <div className="rounded-xl border border-white/40 bg-white/60 p-4 text-sm text-gray-400">
        暂无薄弱点数据
      </div>
    );
  }

  const top = data.weak_points.slice(0, 5);

  return (
    <div className="rounded-xl border border-white/40 bg-white/60 p-4 backdrop-blur-sm">
      <h2 className="text-sm font-semibold text-gray-800">
        结构化薄弱点 (近{data.days}天)
      </h2>
      <div className="mt-3 space-y-2">
        {top.map((wp, i) => (
          <div
            key={i}
            className="rounded-lg bg-white/45 px-3 py-2 text-xs"
          >
            <div className="flex items-center gap-2">
              <span className="truncate font-medium text-gray-800">
                {wp.knowledge_point}
              </span>
              {wp.subject && (
                <span className="shrink-0 rounded bg-purple-500/15 px-1.5 py-0.5 text-purple-600">
                  {wp.subject}
                </span>
              )}
            </div>
            <div className="mt-1.5 flex flex-wrap items-center gap-1.5">
              <span className="rounded bg-red-500/10 px-1.5 py-0.5 text-red-600">
                {wp.mistake_count} 错题
              </span>
              {wp.due_review_count > 0 && (
                <span className="rounded bg-orange-500/10 px-1.5 py-0.5 text-orange-600">
                  {wp.due_review_count} 待复习
                </span>
              )}
              {wp.recent_error_count > 0 && (
                <span className="rounded bg-amber-500/10 px-1.5 py-0.5 text-amber-600">
                  近{data.days}天 {wp.recent_error_count} 次
                </span>
              )}
            </div>
            {wp.top_error_reasons && wp.top_error_reasons.length > 0 && (
              <div className="mt-1.5 flex flex-wrap gap-1">
                {wp.top_error_reasons.map((reason, j) => (
                  <span
                    key={j}
                    className="rounded-full bg-gray-200/60 px-2 py-0.5 text-[11px] text-gray-600"
                  >
                    {reason}
                  </span>
                ))}
              </div>
            )}
            {wp.evidence_sources && wp.evidence_sources.length > 0 && (
              <div className="mt-1.5 flex flex-wrap gap-1">
                {wp.evidence_sources.map((src, j) =>
                  src.slug ? (
                    <Link
                      key={j}
                      href={`/notes/${src.slug}`}
                      className="rounded bg-blue-500/10 px-1.5 py-0.5 text-[11px] text-blue-600 transition-colors hover:bg-blue-500/20"
                    >
                      {src.title ?? src.slug}
                    </Link>
                  ) : (
                    <span
                      key={j}
                      className="rounded bg-blue-500/10 px-1.5 py-0.5 text-[11px] text-blue-600"
                    >
                      {src.title ?? src.source_id}
                    </span>
                  )
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
