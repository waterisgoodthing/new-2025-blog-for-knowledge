import { ManagePageHeader } from '../../components/manage-page-header'
import { SubjectList } from './components/subject-list'

export default function ManageSubjectsPage() {
  return (
    <div className='space-y-8'>
      <ManagePageHeader
        eyebrow='知识体系'
        title='科目'
        description='管理单人学习系统的科目与知识组织入口。'
      />
      <SubjectList />
    </div>
  )
}
