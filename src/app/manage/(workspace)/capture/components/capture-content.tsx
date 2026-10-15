'use client'

import { useState } from 'react'
import { BookPlus, Camera, PenLine } from 'lucide-react'

import { cn } from '@/lib/utils'

import { CaptureWorkspace } from './capture-workspace'
import { ManualQuestionEntry } from './manual-question-entry'
import { MistakeDraftEntry } from './mistake-draft-entry'

type CaptureMode = 'image' | 'manual' | 'mistake'

const modes: Array<{ value: CaptureMode; label: string; icon: typeof Camera }> = [
  { value: 'image', label: '上传图片', icon: Camera },
  { value: 'manual', label: '手工录入题目', icon: PenLine },
  { value: 'mistake', label: '从题库记录错题', icon: BookPlus },
]

/**
 * Mode selector + workspace renderer for the capture page.
 * Shows a segmented button row to choose between image capture,
 * manual question entry, and mistake draft creation; the selected
 * workspace expands below.
 *
 * Uses lazy-mount + keep-alive: a mode's component is mounted
 * only when first activated, then stays mounted but hidden
 * (CSS `hidden`) when the user switches away. This preserves
 * unsaved form state across mode switches.
 */
export function CaptureContent() {
  const [mode, setMode] = useState<CaptureMode>('image')
  const [activated, setActivated] = useState<Set<CaptureMode>>(
    () => new Set<CaptureMode>(['image']),
  )

  const handleSetMode = (next: CaptureMode) => {
    setMode(next)
    setActivated((prev) => {
      if (prev.has(next)) return prev
      const nextSet = new Set(prev)
      nextSet.add(next)
      return nextSet
    })
  }

  return (
    <div className='space-y-6'>
      <div className='flex flex-wrap gap-2' role='group' aria-label='采集方式'>
        {modes.map(({ value, label, icon: Icon }) => (
          <button
            key={value}
            type='button'
            aria-pressed={mode === value}
            onClick={() => handleSetMode(value)}
            className={cn(
              'inline-flex items-center gap-2 rounded-lg border px-4 py-2 text-sm font-medium transition-colors',
              mode === value
                ? 'border-[var(--color-brand)] bg-[var(--color-brand)]/5 text-[var(--color-brand)]'
                : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50',
            )}
          >
            <Icon className='h-4 w-4' aria-hidden='true' />
            {label}
          </button>
        ))}
      </div>
      {activated.has('image') ? (
        <div className={mode === 'image' ? undefined : 'hidden'}>
          <CaptureWorkspace />
        </div>
      ) : null}
      {activated.has('manual') ? (
        <div className={mode === 'manual' ? undefined : 'hidden'}>
          <ManualQuestionEntry />
        </div>
      ) : null}
      {activated.has('mistake') ? (
        <div className={mode === 'mistake' ? undefined : 'hidden'}>
          <MistakeDraftEntry />
        </div>
      ) : null}
    </div>
  )
}
