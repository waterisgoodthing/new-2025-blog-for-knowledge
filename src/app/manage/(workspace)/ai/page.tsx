import { FutureCapabilityPage } from '../components/future-capability-page'

export default function ManageAiPage() {
  return (
    <FutureCapabilityPage
      eyebrow='Batch 6 · AI 占位'
      title='AI 控制台'
      description='未来用于管理模型、Prompt 与调用记录；当前只展示无副作用占位。'
      sections={[
        {
          title: '模型配置',
          description: '未来会记录模型能力、成本、延迟和可用性。',
          items: ['模型 provider 尚未接入', '不会读取 API key', '不会发起模型请求'],
        },
        {
          title: 'Prompt 模板',
          description: '未来会做版本化 prompt 管理和审核。',
          items: ['Prompt 保存暂未启用', '无编辑表单', '无假保存状态'],
        },
        {
          title: '调用记录',
          description: '未来会展示 run id、状态、错误和审计信息。',
          items: ['当前没有虚构记录', '没有轮询', '没有运行详情 API'],
        },
      ]}
      disabledActions={['生成分析', '重新生成', '保存 Prompt', '切换模型', '查看真实运行记录']}
    />
  )
}
