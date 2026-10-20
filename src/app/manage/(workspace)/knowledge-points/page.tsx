import Link from 'next/link'
import { Uiv2PageHeader } from '@/components/ui-v2'

export default function ManageKnowledgePointsPage() {
  return (
    <div className='space-y-8'>
      <Uiv2PageHeader eyebrow='知识体系' title='知识点' subtitle='知识点以科目下的树组织；请先选择一个科目进入树管理。' />
      <Link
        href='/manage/subjects'
        className='inline-flex rounded-lg bg-[var(--brand)] px-4 py-2.5 text-sm font-medium text-white'
      >
        打开科目列表
      </Link>
    </div>
  )
}
