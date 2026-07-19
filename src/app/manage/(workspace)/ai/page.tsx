import { ManagePlaceholderPage } from '../../components/manage-placeholder-page'

export default function ManageAiPage() {
  return (
    <ManagePlaceholderPage
      batch='工具 · 后续能力'
      title='AI 助手'
      description='当前版本未启用 AI 产品功能，人工题目、错题与复习流程不受影响。'
      futureScope='现有 Gateway 与运行记录基础设施不会在此页面自动启用；本阶段不调用 AI、不生成内容，也不改变正式学习数据。'
    />
  )
}
