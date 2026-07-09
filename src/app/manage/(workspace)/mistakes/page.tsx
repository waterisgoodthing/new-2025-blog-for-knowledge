import { ManagePageHeader } from '../../components/manage-page-header'
import { MistakeWorkspace } from './components/mistake-workspace'

export default function ManageMistakesPage() {
  return (
    <div className='space-y-8'>
      <ManagePageHeader
        eyebrow='Batch 4 · 私有错题'
        title='错题'
        description='管理新私有错题。历史公开错题不在此处编辑。从正式题目创建错题草稿，人工确认后进入复习队列。'
      />
      <MistakeWorkspace />
    </div>
  )
}
