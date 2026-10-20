import { Uiv2PageHeader } from '@/components/ui-v2'
import { SubjectList } from './components/subject-list'

export default function ManageSubjectsPage() {
  return (
    <div className='space-y-8'>
      <Uiv2PageHeader eyebrow='知识体系' title='科目' subtitle='管理单人学习系统的科目与知识组织入口。' />
      <SubjectList />
    </div>
  )
}
