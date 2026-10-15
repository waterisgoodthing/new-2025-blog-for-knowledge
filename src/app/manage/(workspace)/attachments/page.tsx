import { AttachmentWorkspace } from './components/attachment-workspace'

export default function ManageAttachmentsPage() {
  return (
    <div className='space-y-7'>
      <header>
        <p className='text-xs font-medium tracking-[0.16em] text-[var(--color-brand)]/75'>资料管理</p>
        <h1 className='mt-2 text-3xl font-semibold text-slate-900'>附件</h1>
        <p className='mt-2 text-sm text-slate-500'>管理私有学习附件及其题目、草稿、错题关联。</p>
      </header>
      <AttachmentWorkspace />
    </div>
  )
}
