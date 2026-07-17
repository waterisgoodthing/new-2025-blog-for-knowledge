import { ManagePageHeader } from '../../components/manage-page-header'
import { MistakeWorkspace } from './components/mistake-workspace'

export default function ManageMistakesPage() {
  return (
    <div className='space-y-8'>
      <ManagePageHeader
        eyebrow='Mistake System'
        title='Mistakes'
        description='查看已确认的私有错题与复盘入口。'
      />
      <MistakeWorkspace />
    </div>
  )
}
