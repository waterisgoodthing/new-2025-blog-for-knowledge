'use client'

import Link from 'next/link'
import { motion } from 'motion/react'
import { ArrowUpRight, Brain, ClipboardCheck, Upload } from 'lucide-react'
import { useCenterStore } from '@/hooks/use-center'
import { useSize } from '@/hooks/use-size'

const learningLinks = [
  {
    href: '/manage/review',
    label: '待复习',
    meta: '—',
    icon: Brain,
  },
  {
    href: '/manage/drafts',
    label: '待审核',
    meta: '—',
    icon: ClipboardCheck,
  },
  {
    href: '/manage/dashboard',
    label: '进入学习空间',
    icon: ArrowUpRight,
  },
  {
    href: '/manage/attachments',
    label: '上传资料',
    icon: Upload,
  },
] as const

export default function LearningSpaceCard() {
  const center = useCenterStore()
  const { maxSM } = useSize()
  const width = 360
  const x = center.x - width / 2
  const y = Math.max(24, center.y - 272)

  return (
    <motion.section
      aria-label='学习空间快捷入口'
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0, left: x, top: y }}
      transition={{ duration: 0.35, ease: 'easeOut' }}
      style={{ width: maxSM ? 'min(360px, calc(100vw - 2rem))' : width }}
      className='absolute rounded-[26px] border border-white/55 bg-white/54 p-3 shadow-[0_18px_50px_-32px_rgba(59,115,118,0.58)] backdrop-blur-xl max-sm:static'
    >
      <div className='grid grid-cols-2 gap-1.5'>
        {learningLinks.map(({ href, label, icon: Icon, ...item }) => (
          <Link
            key={href}
            href={href}
            className='group flex min-h-10 items-center gap-2 rounded-2xl px-2.5 py-2 text-sm text-slate-600 transition-colors hover:bg-white/70 hover:text-slate-900 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-brand)]/45'
          >
            <span className='inline-flex h-7 w-7 shrink-0 items-center justify-center rounded-xl bg-[var(--color-brand)]/9 text-[var(--color-brand)]'>
              <Icon className='h-3.5 w-3.5' aria-hidden='true' />
            </span>
            <span className='min-w-0 flex-1 truncate'>{label}</span>
            {'meta' in item && (
              <span className='text-xs text-slate-400' aria-label={`${label}数量尚未接入`}>
                {item.meta}
              </span>
            )}
          </Link>
        ))}
      </div>
    </motion.section>
  )
}
