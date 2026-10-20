import { Uiv2PageHeader } from '@/components/ui-v2'
import { MistakeWorkspace } from './components/mistake-workspace'

export default function ManageMistakesPage() {
  return (
    <div className='space-y-8'>
      <Uiv2PageHeader
        eyebrow='内容管理'
        title='错题'
        subtitle='查看已确认的私有错题与复盘入口。'
      />
      <MistakeWorkspace />
    </div>
  )
}
