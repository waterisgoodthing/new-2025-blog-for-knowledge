import Link from 'next/link'

import { ManagePageHeader } from '../../../components/manage-page-header'
import { AiRunsPanel } from '../components/ai-runs-panel'

export default function ManageAiRunsPage() {
  return (
    <div className='space-y-8'>
      <div className='flex flex-wrap items-start justify-between gap-4'>
        <ManagePageHeader
          eyebrow='Batch 11 · AI Run Audit'
          title='AI Run 审计'
          description='查看业务 Run 的受控输出并完成人工流转；技术调用日志仍由 AI 控制台独立承载。'
        />
        <Link
          href='/manage/ai'
          className='rounded-lg border border-slate-200 bg-white/60 px-3 py-2 text-sm text-slate-600 hover:bg-white'
        >
          返回 AI 控制台
        </Link>
      </div>
      <AiRunsPanel />
    </div>
  )
}
