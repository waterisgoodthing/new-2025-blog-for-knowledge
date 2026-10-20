import { Uiv2PageHeader } from '@/components/ui-v2'
import { PracticeToday } from './practice-today'

export default function ManagePracticePage() {
  return (
    <div className='space-y-8'>
      <Uiv2PageHeader eyebrow='学习计划' title='今日练习' subtitle='从薄弱知识点中挑选最近未作答的题目进行练习，全部来自 canonical 学习数据。' />
      <PracticeToday />
    </div>
  )
}
