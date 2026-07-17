import Link from 'next/link'
import { ManagePageHeader } from '../../components/manage-page-header'

export default function ManageKnowledgePointsPage() {
  return (
    <div className='space-y-8'>
      <ManagePageHeader
        eyebrow='Learning Foundation'
        title='Knowledge Points'
        description='知识点以科目下的树组织；请先选择一个科目进入树管理。'
      />
      <Link
        href='/manage/subjects'
        className='inline-flex rounded-lg bg-[var(--color-brand)] px-4 py-2.5 text-sm font-medium text-white'
      >
        打开科目列表
      </Link>
    </div>
  )
}
