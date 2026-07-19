import { ManagePlaceholderPage } from '../../../components/manage-placeholder-page'

export default function ManageAiRunsPage() {
  return (
    <ManagePlaceholderPage
      batch='工具 · 后续能力'
      title='AI 运行记录'
      description='当前版本未开放 AI 运行记录产品页面。'
      futureScope='已有 ai_runs 与 ai_call_logs 数据合同保持不变；本页面不读取、不重试，也不提交人工决定。'
    />
  )
}
