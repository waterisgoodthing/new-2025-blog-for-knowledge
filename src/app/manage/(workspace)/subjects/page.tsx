import { ManagePageHeader } from '../../components/manage-page-header'
import { SubjectList } from './components/subject-list'

export default function ManageSubjectsPage() {
  return (
    <div className='space-y-8'>
      <ManagePageHeader
        eyebrow='Batch 2 · 分类基础'
        title='科目与知识点'
        description='维护科目、章节和正式知识点，供后续题目与复习流程复用。'
      />
      <SubjectList />
    </div>
  )
}
