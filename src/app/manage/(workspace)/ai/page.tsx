import { ManagePlaceholderPage } from '../../components/manage-placeholder-page'

export default function ManageAiPage() {
  return (
    <ManagePlaceholderPage
      batch='Batch 6 · AI Placeholder'
      title='AI'
      description='AI 能力尚未启用；当前工作区继续使用人工题目、错题与复习流程。'
      futureScope='本批只保留能力入口和边界说明，不读取 AI runs，不展示 provider、model、cost 或成功率，也不会调用任何 AI API。'
    />
  )
}
