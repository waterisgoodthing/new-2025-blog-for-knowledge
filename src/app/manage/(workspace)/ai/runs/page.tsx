import { ManagePlaceholderPage } from '../../../components/manage-placeholder-page'

export default function ManageAiRunsPage() {
  return (
    <ManagePlaceholderPage
      batch='Batch 6 · AI Run Placeholder'
      title='AI Runs'
      description='AI 调用审计尚未启用；当前页面不读取历史运行记录。'
      futureScope='本批不显示 ai_runs 或 ai_call_logs，不创建、不重试、不统计任何运行记录。'
    />
  )
}
